# -*- coding: UTF-8 -*-
"""Import modules"""
from os import path


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
        return f"Transform and insert data into: {str(self.config.table)}"

    def __str__(self) -> str:
        """ Print representation """
        return f"Transform and insert data into: {str(self.config.table)}"

    def __check_files(self) -> list:
        """ Check files
        return list
        """

        return []

    def __transform(self) -> None:
        """ Transform information
        returns DataFrame
        """

        return None

    def execute(self) -> str:
        """ Transform dataset
        return str
        """

        if self.__check_files() is True:
            self.__transform()

        return 'Successfully processed'
