#!/bin/bash
eval export $(cat .env)

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
if [ "$PARAMS" == "Deploy Docker Environment" ]; then
    docker-compose up -d
    docker-compose ps
    echo "Running Airflow UI on http://localhost:8080"

fi

if [ "$PARAMS" == "Run DAG" ]; then
    echo "Updating envinroment ..."
    docker-compose up -d
    echo "Running data workflow ..."
    docker exec -it airflow-worker-container airflow dags test $DAG_ID
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

if [ "$PARAMS" == "Config Git Repositories" ]; then
  for remote in \
    "git@gitlab.com:lema_ufpb/projetos/airflow/skeleton.git" 
  do
    git remote set-url --delete --push origin $remote 2> /dev/null
    git remote set-url --add --push origin $remote
  done
  git remote show origin
fi




