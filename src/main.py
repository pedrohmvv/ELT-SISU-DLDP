# -*- coding: UTF-8 -*-
"""Import modules"""
from os.path import dirname, abspath
from sys import path as sys_path
from dag import DAGModel

# initialize airflow base dir
AIRFLOW_BASE = dirname(abspath(__file__))
sys_path.append(AIRFLOW_BASE)


# Build dag for local test
globals()["dag-test"] = DAGModel().create_dag(
    dag_id=DAGModel().project_id,
    schedule=None,
    owner="test-env",
    tags=[],
    timeout=10,
    region="BR"
)
