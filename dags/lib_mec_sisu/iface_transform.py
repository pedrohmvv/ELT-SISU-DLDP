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

        projects = {"_id": True,'filename': True, 'year': True}

        files = list(
            self.config.registry.aggregate(
                [{"$match": filters}, {"$project": projects}]
            )
        )

        if len(files) == 0:
            self.log.info("No new files to be processed")

        processed_files = []
        for elem in files:
            year = elem['year']
            file = elem['filename']
            file_list = glob(f'{self.data_dir}/{year}/{file}*.[cC][sS][vV].gz')
            for file in file_list:
                processed_files.append({'year': year, 'table': self.config.vars.table,
                                        "_id": elem['_id'], 'filename': file})

        return processed_files

    
    def __read_file(self) -> DataFrame:
        """
        Read files due to the separation and encoding variation
        over the years
        -------------------------------------------------------
        Args:
            file (str): file path
        Return:
            data (DataFrame) 
        """
        encoding = 'utf-8'
        separators = [',', ';', '|']
        # Tries with utf-8 encoding
        try:
            for sep in separators:
                data = read_csv(self.__file, sep=sep, encoding=encoding, low_memory=False, nrows=3, on_bad_lines='warn')
                if len(data.columns) > 1:
                    sep_adjusted = sep
                    break
        except UnicodeDecodeError:
            # If the encoding used dont't works, try using 'latin1' 
            encoding = 'latin1'
            for sep in separators:
                data = read_csv(self.__file, sep=sep, encoding=encoding, low_memory=False, nrows=3, on_bad_lines='warn')
                if len(data.columns) > 1:
                    sep_adjusted = sep
                    break

        data = read_csv(self.__file, sep=sep_adjusted, encoding=encoding, low_memory=False, on_bad_lines='warn')

        return data

    def __get_columns(self, df):
            # Sufixes to remove
            sufixes = ['ST_', 'SG_', 'NU_', 'NO_', 'NOME_']
            for sufix in sufixes:
                for col in df.columns:
                    if col.startswith(sufix):
                        new_col = col.replace(sufix, '')
                        df.rename(columns={col: new_col}, inplace=True)
            # Returns filtered df
            return df[self.config.vars.target_columns]
    
    def __transform(self, file) -> DataFrame:
        """Transform Sisu information
        returns DataFrame
        """
        try:
            self.__file = file
            # Read file
            raw_data = self.__read_file()
            # Filter data columns
            filtered_data = self.__get_columns(raw_data)
            # Filter target data
            data = filtered_data.loc[
                    (filtered_data['MATRICULA'] == 'EFETIVADA') &
                    (filtered_data['SIGLA_IES'] == 'UFPB') &
                    (filtered_data['UF_IES'] == 'PB')
                ]

            return data
        
        except Exception as error:
            raise OSError(error) from error

    def execute(self) -> str:
        """ Trasnform and Insert dataset
        return str
        """

        files = self.__check_files()

        for index, doc in enumerate(files):
            file = doc['filename']
            id_file = doc['_id']
            self.log.info(f'Processing {id_file}: {index+1}/{len(files)}')

            if not path.exists(file):
                raise FileNotFoundError(f'Not found: {file}')
            
            data = self.__transform(file)

            if len(data) > 0:
                self.log.info(f"Bulk insert to database: {self.config.vars.table} - {doc['year']}")
                table_name = self.config.vars.table
                print('Nome tabela', table_name)
                self.config.db_conntable[table_name].insert_many(
                    data.to_dict('records')
                    )
            
            self.log.info("Registry metadata")
            self.config.registry.update_one(
                {'_id': id_file},
                {'$set':
                    {'processed': True,
                     'table': table_name,
                     'nrows': data.shape[0],
                     'ncols': data.shape[1],
                     'processing_date': datetime.now()}
                 }
            )

        rmtree(self.data_dir)
        
        return 'Successfuly processed'