# -*- coding: UTF-8 -*-
"""Import modules"""
from os.path import abspath, dirname, join
from sys import path as sys_path
from pathlib import Path
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator


# initialize airflow base dir
BASE_DIR = dirname(abspath(__file__))
sys_path.append(BASE_DIR)


class DAGModel():
    """
    Create a DAG model
    """

    def __init__(self) -> None:
        """Handle version"""
        try:
            with open(join(BASE_DIR, '.release')) as f:
                version = f.readline()
            f.close()
        except:
            version = "dev"
        self.version = version

    def __load_docs(self, filename: str) -> str:
        """Load docs from markdown files"""
        return Path(dirname(__file__), filename).read_text(encoding="utf8")

    def create_dag(self, **params):
        """Create model artifact for dag factory"""

        default_args = {
            "owner": params.get('owner'),
            "depends_on_past": False,
            "start_date": datetime(2022, 1, 8),
            'email_on_failure': False,
            "retries": 0,
            "retry_delay": timedelta(minutes=1),
            "dagrun_timeout": timedelta(minutes=params.get('timeout')),
            "on_success_callback": params.get('on_success_callback'),
            "on_failure_callback": params.get('on_failure_callback')
        }

        dag = DAG(
            dag_id=params.get('dag_id'),
            description=params.get('description'),
            default_args=default_args,
            schedule_interval=params.get('schedule'),
            catchup=False,
            tags=params.get('tags'),
            params={
                "region": Param(
                    default=params.get('region'),
                    type="string",
                    description="Region for filter download data (ex. PB, SP, RN...)"
                ),
                "start_year": Param(
                    default=params.get('start_year'),
                    type="int",
                    description="Start year for filter download data (ex. 2015, 2016, 2017...)"
                )
            }
        )
        with dag:

            # Import local modules
            from lib_mec_sisu.operators import download, transform

            # Define tasks: ST
            task_1 = PythonOperator(
                task_id="download_data",
                python_callable=download,
                provide_context=True
            )

            # Define tasks: EQ
            task_2 = PythonOperator(
                task_id="process_data",
                python_callable=transform,
                provide_context=True
            )

            # Model workflow
            task_1 >> task_2

            # Load docs
            dag.doc_md = self.__load_docs("docs/main.md")

        return dag
