from os import path, system
from subprocess import getstatusoutput

if not path.isdir("./docker/airflow"):
    print("Add docker submodule")
    system("git submodule add -b main --force git@gitlab.com:lema-ufpb-hub/docker.git docker")
    system("git submodule update --init --remote --recursive --force")


check_cmd, _ = getstatusoutput("python3 --version")
py_cmd = "python3" if check_cmd == 0 else "python"

system(f"{py_cmd} ./docker/airflow/options.py --name dag-test")
