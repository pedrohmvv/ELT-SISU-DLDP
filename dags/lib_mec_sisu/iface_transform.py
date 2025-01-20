# -*- coding: UTF-8 -*-
"""Import modules"""
from os import path, rmdir
from pandas import DataFrame, read_csv
from glob import glob
from numpy import nan
from datetime import datetime
from shutil import rmtree

class Transform:
    """ Extract data interface """

    def __init__(self, **airflow_context: dict):
        """ Load instance variables """

        # module import in airflow context
        from lib_mec_sisu.iface_config import Config

        self.config = Config()
        self.context = airflow_context
        self.data_dir = path.join(self.config.vars.data_dir, self.config.vars.files_dir)
        self.log = self.config.log

    def __repr__(self) -> str:
        """ Basic instance representation """
        return f"Tranform and insert data into: {str(self.config.table)}"

    def __str__(self) -> str:
        """ Print representation """
        return f"Tranform and insert data into: {str(self.config.table)}"

    def __check_files(self) -> list:
        """ Check files
        return list
        """
        self.log.info("Checking files")
        filters = {"table": self.config.vars.table, "processed": None}
        # Define projection
        projects = {"_id": True, 'filename': True, 'year': True}
        # Get files to be processed
        files = list(
            self.config.registry.aggregate(
                [{"$match": filters}, {"$project": projects}]
            )
        )
        # Check if there are files to be processed
        if len(files) == 0:
            self.log.info("No new files to be processed")
        # Check if files exist
        processed_files = []
        for elem in files:
            year = elem['year']
            file = elem['filename']
            file_list = glob(f'{self.data_dir}/{year}/{file}*.[cC][sS][vV].gz')
            for file in file_list:
                processed_files.append({'year': year, 'table': self.config.vars.table,
                                        "_id": elem['_id'], 'filename': file})

        return processed_files

    def __read_file(self, file: str, chunksize: int = 10000):
        """
        Read CSV file in chunks, yielding each chunk for processing.
        -------------------------------------------------------
        Args:
            file (str): file path
            chunksize (int): Size of chunks to read (default=10000)
        Yields:
            DataFrame: A chunk of the loaded data.
        """
        encoding_options = ['utf-8', 'latin1']
        separators = [',', ';', '|']

        for encoding in encoding_options:
            for sep in separators:
                try:
                    # Test reading with detected encoding and separator
                    sample = read_csv(file, sep=sep, encoding=encoding, nrows=5, on_bad_lines='skip')
                    if sample.shape[1] > 1:  # Likely valid separator
                        self.log.info(f"Detected encoding={encoding} and separator='{sep}'")
                        # Yield chunks of the file
                        for chunk in read_csv(file, sep=sep, encoding=encoding, chunksize=chunksize, on_bad_lines='skip', low_memory=False):
                            yield chunk
                        return
                except Exception:
                    continue

        raise ValueError("Failed to read the file with available encodings and separators.")

    def __get_columns(self, df):
        """Remove unwanted prefixes from column names and filter target columns."""
        sufixes = ['ST_', 'SG_', 'NU_', 'NO_', 'NOME_']
        columns = df.columns
        joined_columns = '|'.join(columns)
        # Remove unwanted prefixes
        for sufix in sufixes:
                joined_columns = joined_columns.replace(sufix, '')
        df.columns = joined_columns.split('|')
        return df[self.config.vars.target_columns]

    def __transform(self, chunk: DataFrame) -> DataFrame:
        """
        Transform a single chunk of data.
        Returns:
            DataFrame: Filtered chunk.
        """
        # Filter data columns
        filtered_data = self.__get_columns(chunk)
        # Filter target data
        data = filtered_data.loc[
            (filtered_data['MATRICULA'] == 'EFETIVADA') &
            (filtered_data['SIGLA_IES'] == 'UFPB') &
            (filtered_data['UF_IES'] == 'PB')
        ]
        return data

    def execute(self) -> str:
        """ Transform and insert dataset incrementally with chunks """
        files = self.__check_files()
        for index, doc in enumerate(files):
            file = doc['filename']
            id_file = doc['_id']
            self.log.info(f'Processing {id_file}: {index+1}/{len(files)}')

            if not path.exists(file):
                raise FileNotFoundError(f'Not found: {file}')
            # Keep track of total rows processed
            total_rows = 0  
            total_columns = 0
            # Process each chunk
            for chunk in self.__read_file(file):
                try:
                    processed_data = self.__transform(chunk)
                except KeyError as error:
                    self.log.error(f"Error processing chunk: {error}, MATRICULA columns doesn't exist.")
                    continue
                # Insert
                if not processed_data.empty:
                    self.log.info(f"Bulk inserting {len(processed_data)} rows to database.")
                    self.config.db_conntable[self.config.vars.table].insert_many(processed_data.to_dict('records'))
                    total_rows += len(processed_data)
                    total_columns = processed_data.shape[1]
            # Update metadata for the file
            self.log.info("Updating registry metadata")
            self.config.registry.update_one(
                {'_id': id_file},
                {'$set':
                    {'processed': True,
                     'table': self.config.vars.table,
                     'nrows': total_rows,
                     'ncols': total_columns,
                     'processing_date': datetime.now()}
                 }
            )
        # Clean up the data directory
        rmtree(self.data_dir)

        return 'Successfully processed'
