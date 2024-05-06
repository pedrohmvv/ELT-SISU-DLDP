# -*- coding: UTF-8 -*-
"""Import modules"""
from os.path import abspath, dirname
from sys import path as sys_path
from pathlib import Path
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator


# initialize this local module base dir
sys_path.insert(0, abspath(dirname(__file__)))


class DAGModel():
    """
    Create a DAG model
    """

    def __init__(self) -> None:
        """Create a general project id"""
        self.project_id = "provider-theme"

    def load_docs(self, filename: str):
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
                )
            }
        )
        with dag:

            # Import local modules
            from lib_provider_theme.operators import download, transform

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
            dag.doc_md = self.load_docs("docs/dag.md")

        return dag
