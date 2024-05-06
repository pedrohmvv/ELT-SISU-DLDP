# -*- coding: UTF-8 -*-
"""Import modules"""
from os import path, makedirs


class Extract:
    """ Extract data interface """

    def __init__(self, **airflow_context: dict):
        """ Load instance variables """

        # module import in airflow context
        from lib_provider_theme.iface_config import Config

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

    def __check_files(self) -> bool:
        """ Check files
        return bool
        """
        try:

            query_registry = list(
                self.config.registry.find(
                    {'table': self.config.vars.table},
                    {'_id': True})
            )

            if len(query_registry) > 0:
                return False
            return True

        except Exception as error:
            raise OSError(error) from error

    def __read_file(self) -> None:
        """ Read DBC/DBF file
        return dataframe
        """
        try:
            pass

        except (OSError, ValueError):
            pass

    def download(self) -> None:
        """ Download file
        args:
        return string
        """
        if self.__check_files() is True:
            self.__read_file()
