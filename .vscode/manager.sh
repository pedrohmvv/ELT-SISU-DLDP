#!/bin/bash
eval export $(cat ./src/docker/.env)

PARAMS=""
# handle params
while (( "$#" )); do
  case "$1" in
    -a|--action)
      shift
      ;;
    *)
      PARAMS="$1"
      shift
      ;;
  esac

done
# set positional arguments in their proper place
eval set -- "$PARAMS"

# Conditionals
if [ "$PARAMS" == "Deploy/Update Docker Environment" ]; then
    docker compose -f ./src/docker/docker-compose.yaml up -d
    echo "Running Airflow UI on http://localhost:8080 or https://airflow.lemaufpb.dev/"
fi

if [ "$PARAMS" == "Run DAG in Terminal" ]; then
    echo "Running data workflow ..."
    docker compose -f ./src/docker/docker-compose.yaml up -d
    docker exec -it airflow-worker-container airflow dags test mec-sisu
fi

if [ "$PARAMS" == "Update Docker Submodules" ]; then
    git submodule update --init --remote --recursive --force
fi

if [ "$PARAMS" == "Code Analysis" ]; then
    echo "Code Analysis"
    if [[ "$OSTYPE" =~ ^darwin ]]; then
      autopep8 -rai src 
      flake8 src --exit-zero 
      pylint --fail-under=8 src
    else
      python -m autopep8 -rai src 
      python -m flake8 src --exit-zero 
      python -m pylint --fail-under=8 src
    fi
fi

if [ "$PARAMS" == "Remove/Down Docker Environment" ]; then
    docker compose -f ./src/docker/docker-compose.yaml down
fi

if [ "$PARAMS" == "Add Docker Submodule" ]; then
    git submodule add -b main git@gitlab.com:lema-ufpb-hub/docker.git  src/docker
fi





