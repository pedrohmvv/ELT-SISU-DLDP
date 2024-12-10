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

    
    def __read_file(self, year) -> DataFrame:
        """ Read CSV file
        return DataFrame
        """
        try:
            if year >= 2022 or year == 2017:
                data = read_csv(self.__file, sep='|', encoding='latin')
            if 2018 <= year <= 2021:
                if 'regular' in self.__file.lower():
                    data = read_csv(self.__file, sep=';')
                else:
                    data = read_csv(self.__file, sep='|', encoding='latin')
            if year == 2016:
                data = read_csv(self.__file, sep='|')

        except Exception as error:
            return error

        return data

    def __sisu(self, data, year) -> DataFrame:
        """Aggregate SISU data
        return DataFrame
        """
        score_columns = [
            'nota_l', 'nota_ch',
            'nota_cn','nota_m', 
            'nota_r'
            ]

        matricula_map = {
        'PENDENTE':'P', 'NÃO COMPARECEU':'F', 'EFETIVADA':'E', 'CANCELADA':'C',
        'DOCUMENTACAO REJEITADA':'R', 'NÃO CONVOCADO':'NC',
        'SUBSTITUIDA - MATRICULA FORA DO PRAZO':'S', 'NÃO MATRICULADO':'NM'
        }

        cote_remap = {
            'Indígena': 3,
            'Preto': 5,
            'Preto,Pardos, Indígenas e Quilombolas': 6,
            'Ampla': 7,
            'Ignorado': 9
        }


        rename = {}

        if year == 2016: 
            rename = {
                'nome_curso':'curso','ds_modalidade':'mod_concorrencia',
                'cod_ies':'co_ies'
            }

            if '1' in data['ds_etapa'].iloc[0].lower():
                data['etapa'] = '4'
            else:
                data['etapa'] = '7'

        if  2017 <= year <= 2021 :
            data = data.rename(columns={'NO_MUNUCIPIO_CAMPUS':'municipio_campus'}) 

        try:
            data = data.drop(columns = ['DS_ETAPA'])
        except KeyError:
            data = data.drop(columns = ['ds_etapa'])

        data = (
            data.rename(columns = lambda x: x.lower())
            .rename(columns = rename).rename(
            columns = lambda x: x.replace('co_','').replace('nu_','').replace('st_','').replace('ds_','').replace('no_','').replace('sg_','')                                    
            ))

        try:
            data['matricula']
        except KeyError:
            data['matricula'] = None

        data[score_columns] = data[score_columns].replace(',','.', regex=True).astype(float)
        data['tipo_cota'] = data['mod_concorrencia'].map(self.config.vars.cota_map).replace(nan,'Outro')
        data['tipo_cota'] = data['tipo_cota'].map(cote_remap).replace(nan,9)
        data['matricula'] = data['matricula'].map(matricula_map)
        data['etapa'] = data['etapa'].astype(str)

        data = (
            data.assign(
                media = lambda x: (x.nota_l + x.nota_r + x.nota_cn + x.nota_m + x.nota_ch)/5,
                aprovados = lambda x: x.aprovado.str.count('S'),
                nao_aprovados = lambda x: x.aprovado.str.count('N'),
                pendente = lambda x: x.matricula.str.count('P'),
                nao_compareceu = lambda x: x.matricula.str.count('F'),
                efetivada = lambda x: x.matricula.str.count('E'),
                cancelada = lambda x: x.matricula.str.count('C'),
                doc_rejeitada = lambda x: x.matricula.str.count('R'),
                nao_convocado = lambda x: x.matricula.str.count('NC'),
                nao_matriculado = lambda x: x.matricula.str.count('NM')
            ).groupby(['ano','edicao','etapa','uf_ies','municipio_campus','tipo_cota'])
            .agg({
                'media':'mean','aprovados':'sum',
                'nao_aprovados':'sum','pendente':'sum','nao_compareceu':'sum',
                'efetivada':'sum', 'cancelada':'sum','doc_rejeitada':'sum',
                'nao_convocado':'sum'
            })
            ).reset_index()

        return data
    
    def __transform(self, file, year) -> DataFrame:
        """Transform Sisu information
        returns DataFrame
        """
        try:
            self.__file = file
            data = self.__read_file(year)
            data = self.__sisu(data, year)

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
            year = doc['year']
            self.log.info(f'Processing {id_file}: {index+1}/{len(files)}')

            if not path.exists(file):
                raise FileNotFoundError(f'Not found: {file}')
            
            data = self.__transform(file, year)

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

