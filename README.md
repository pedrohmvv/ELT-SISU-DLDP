# Módulo DAG para Airflow

## 💡 ETL de dados - MEC SISU

Este projeto consiste em uma DAG (Directed Acyclic Graph) modelada no Apache Airflow, que implementa uma pipeline de ETL (Extract, Transform, Load). O objetivo é carregar os dados no banco de dados utilizado no projeto DLDP, desenvolvido por pesquisadores do LEMA (Laboratório de Estudos em Modelagem Aplicada da UFPB) em parceria com a coordenação de Linguagens da UFPB.

[<img align="left" height="94px" width="94px" alt="LEMA" src="https://www.ccsa.ufpb.br/lema/wp-content/uploads/sites/179/sites/180/2024/05/cropped-logo-lema.png"/>](https://lema.ufpb.br/)

[**LEMA**](https://lema.ufpb.br/) \
Áreas de Estudo: `Ciência de Dados`,`Engenharia de Dados`,`Aprendizagem de Máquina`, `Indicadores Socioeconômicos`, `Objetivos de Desenvolvimento Sustentável` \
Alguns projetos: [SAEGO](https://lema.ufpb.br/saego/), [Preço da Hora](https://precodahora.tcepb.tc.br/), [Sistema de Inteligência de Dados de Ciência e Tecnologia da Paraíba](https://sidtec.secties.pb.gov.br/)
<br/>

---

## 📋 Ferramentas

- [Docker](https://www.docker.com/)
- [Apache Airflow](https://airflow.apache.org/)
- [Python](https://www.python.org/)
- [MongoDB](https://www.mongodb.com/pt-br) - Rodando em container Docker

<div style="display: inline_block"><br>
  <img align="center" alt="Python" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg"/>     
  <img align="center" alt="Mongo" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/mongodb/mongodb-original.svg"/>
  <img align="center" alt="Docker" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original.svg"/>
  <img align="center" alt="Airflow" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apacheairflow/apacheairflow-original.svg" />
          
</div>

---
## 📂 Estrutura do Projeto

```txt
├──.vscode                  # Configurações do VS Code para o projeto
├── dags/                   # Definições dos workflows (DAGs) do Airflow
│   ├── docs/               # Documentação sobre os DAGs
|   ├── lib_mec_sisu/       # Biblioteca personalizada para o projeto
|         ├── env.yaml      # Configurações de ambiente
|         ├── iface_*.py    # Scripts para ETL (Extract, Transform, Load)
|         ├── operators.py  # Operadores customizados para o Airflow
│   ├── .airflowignore      # Ignora arquivos do Airflow
│   ├── main.py             # Ponto de entrada principal
│   ├── model.py            # Modelos de dados
├── docker/                 # Configurações para Docker
├── plugins/                # Plugins customizados para o Airflow
├── .flake8                 # Configuração do linter flake8
├── .gitignore              # Arquivos a serem ignorados pelo Git
├── .gitlab-ci.yml          # Configuração do GitLab CI/CD
├── .gitmodules             # Configura submódulos Git
├── .pylintrc               # Configuração do linter pylint
├── .README.md              # Arquivo README do projeto
```

---

## 🔗 Links relacionados

- [How to Design Better DAGs in Apache Airflow](https://towardsdatascience.com/how-to-design-better-dags-in-apache-airflow-494f5cb0c9ab)
- [Apache Airflow Best Practices and Advantages](https://medium.com/digital-transformation-and-platform-engineering/apache-airflow-best-practices-and-advantages-9ec71f1ef3cc)
- [Best Practices - Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Apache Airflow – How to write DAGs and master all best practices](https://itgix.com/blog/apache-airflow-how-to-write-dags-and-master-all-best-practices/)

