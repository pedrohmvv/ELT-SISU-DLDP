# -*- coding: UTF-8 -*-
"""Import modules"""
import dataclasses
from os.path import join, dirname, abspath
from yaml import load
from yaml.loader import SafeLoader
from airflow.models import Variable
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.utils.log.logging_mixin import LoggingMixin as task_logger


@dataclasses.dataclass
class Variables:
    """ Variables dataclass """
    database: str
    registry: str
    data_dir: str
    files_dir: str
    data_url: str
    table: dict
    extension: str


class Config:
    """ Configuration interface """

    def __init__(self) -> None:
        """ Load instance variables """
        # Load project env vars
        data = {}
        with open(join(dirname(abspath(__file__)), 'env.yaml'), encoding='utf-8') as file:
            data = load(file, Loader=SafeLoader)
        self.vars = Variables(
            data_url=data.get("data_url"),
            database=data.get("database"),
            table=data.get("table"),
            registry=data.get("registry"),
            files_dir=data.get("files_dir"),
            data_dir=Variable.get("data_dir"),
            extension='.csv.gz'
        )

        self.db_connection = MongoHook(mongo_conn_id="mongo_default").get_conn()
        self.log = task_logger().log
        self.registry = self.db_connection[self.vars.database][self.vars.registry]
        self.db_conntable = self.db_connection[self.vars.database]


    def __repr__(self) -> str:
        """ Basic instance representation """
        return str(self.vars)

    def __str__(self) -> str:
        """ Print representation """
        return str(self.vars)
