# -*- coding: UTF-8 -*-
"""Import modules"""
from os import path, system, remove, makedirs
from datetime import datetime
from glob import glob
from re import sub
from bs4 import BeautifulSoup
from requests import get
from pandas import DataFrame, to_numeric
from pymongo.errors import DuplicateKeyError


class Extract:
    """ Extract data interface """

    def __init__(self, **airflow_context: dict):
        """ Load instance variables """

        # module import in airflow context
        from lib_mec_sisu.iface_config import Config

        self.config = Config()
        self.context = airflow_context
        self.data_dir = path.join(self.config.vars.data_dir, self.config.vars.files_dir)
        self.log = self.config.log
        self.log.info("Checking staging")
        makedirs(self.data_dir, exist_ok=True)

    def __repr__(self) -> str:
        """ Basic instance representation """
        return f"Staging dir: {str(self.data_dir)}"

    def __str__(self) -> str:
        """ Print representation """
        return str(self.data_dir)

    def __check_files(self) -> DataFrame:
        """ Check files
        return DataFrame
        """

        try:

            key = self.config.vars.table

            data_registry = DataFrame(
                self.config.registry.find(
                    {"table": key},
                    {"filename": True, "_id": False})
            ).rename(columns={"filename": "_id"})

            start = 0
            download_links = []

            self.log.info('Read data')
            while True:
                data_page = get(self.config.vars.data_url+str(start))
                data_page_soup = BeautifulSoup(data_page.content, 'html.parser')
                data_pages_url = [self.config.vars.domain+title.a['href'] for title in data_page_soup.find_all('h2', class_='tileHeadline')]

                if len(data_pages_url) == 0:
                    break
                
                for page in data_pages_url:
                    link_page_soup = get(page)
                    content = BeautifulSoup(link_page_soup.content, 'html.parser')
                    div = content.find_all('div', class_='formatos')
                    if div[0].find('span', class_='csv'):
                        link = div[0].a['href']
                        download_links.append(link)
                    else:
                        pass

                start += 10

            
            data = DataFrame({
                    'url':download_links,
                    }).assign(
                        file=lambda x: x.url.str.replace(".*/", "", regex=True),
                        year=lambda x: to_numeric(x.url.str.extract(r'(\d{4})').iloc[:, 0], errors='coerce'),
                        sisu=lambda x: x.url.str[-5:-4],
                        extension=lambda x: x.url.str[-4:],
                        _id=lambda x: x.file.str.replace('(.CSV)|(.csv)|(.ZIP)|(.zip)','',regex=True).str.lower()   
                    )
            
            data['session'] = data['file'].apply(lambda x: 'espera' if 'espera' in x.lower() else 'regular')

            if len(data) == 0:
                raise FileNotFoundError(f"Error on read {self.config.vars.data_url}")
            
            self.log.info("Handle data")
            start_year = self.context['params']['start_year']
            data = data.query('year>=@start_year')

            self.log.info("Searching for existing files")
            if len(data_registry) > 0:
                data = data.merge(
                    data_registry, on="_id", how="outer", indicator=True
                ).query('_merge=="left_only"')

            return data

        except Exception as error:
            raise OSError(error) from error

    def download(self, limit: int = 10000) -> str:
        """ Download file
        args:
            limit: integer; default value: 10000
        return string
        """

        files = self.__check_files()

        if len(files) == 0:
            return 'No new files to download'
        
        for file in files.to_dict('records'):
            try:
                url = file['url']
                year = int(file['year'])
                filename = file['file']
                sisu = file['sisu']
                session = file['session']
                extension = file['extension']
                destfile = path.join(self.data_dir,str(year))
                
                if not path.exists(destfile):
                    makedirs(destfile)
                    
                os_cmd = (
                        f"wget --limit-rate {limit}k "
                        f"--no-check-certificate -c {url} -O {destfile}/{filename}"
                        )
                
                self.log.info(f"Downloading {file}, on URL:{url}")
                system(os_cmd)

                if extension == '.zip':
                    self.log.info('Uncompress ZIP file')
                    system(f"7z e {destfile}/{filename} -O{destfile} -aoa")

                self.log.info("Compress to GZIP...")
                file_list = glob(f'{destfile}/*.[cC][sS][vV]')

                for file in file_list:
                    system(f'gzip -f {file}')
                
                try:
                    self.config.registry.insert_one(
                        {
                            'table':self.config.vars.table,
                            'year':year,
                            'download_date':datetime.now(),
                            'filename':sub('.CSV|.csv','',filename),
                            '_id': f'{self.config.vars.table}_{session}_{sisu}_{year}'
                        }
                    )
                    self.log.info(f'Tabela: {self.config.vars.table}')
                    self.log.info(f'Tabela: {self.config.registry}')
                
                except DuplicateKeyError:
                    self.log.info(
                        f'Data is already in table {self.config.vars.registry}'
                    )

            except Exception as error:
                raise OSError(error) from error
            
        return 'Download files finished'