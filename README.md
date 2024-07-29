# Módulo DAG para Airflow

## 💡 ETL de dados - MEC SISU

Esse projeto é um modelo com estrutura de organização básica orientada a objetos.

---

## 📗 Licença

As informações aqui contidas são confidenciais e de propriedade do grupo de pesquisa.

É proibido o uso, a cópia, a transferência ou a divulgação dessas informações sem o consentimento do proprietário.

DIREITOS RESERVADOS
(c) 2023 LEMA-UFPB.
João Pessoa, PB, Brasil

---

## 📋 Pré-requisitos

Ferramentas:

- [Docker](https://www.docker.com/)
- [Apache Airflow](https://airflow.apache.org/)

---

## ☢️ Boas práticas

- Nunca salvar dados sensíveis de credenciais no gitlab (mesmo que criptografadas)
- Revisar código e aplicar lint antes de fazer _push_.
- Usar o código da task ou feature na mensagem de _commit_. Ex: `git commit -m "task/01: mensagem ..."`.
- Abrir _merge request_ para o ramo `main` e solicitar revisor.

---

## 📦 Ambiente de teste

No VSCode, basta instalar a extensão _F5 Anything_ e executar os testes no **Airflow por linha de comando**
usando a tecla F5. No diretório `.vscode` foram configuradas tasks para pré-checagem do ambiente docker
para execução local da pipeline de dados.

- Acessar Airflow Webserver [http://localhost:8080](http://localhost:8080)

---

## 🔗 Links relacionados

- [How to Design Better DAGs in Apache Airflow](https://towardsdatascience.com/how-to-design-better-dags-in-apache-airflow-494f5cb0c9ab)
- [Apache Airflow Best Practices and Advantages](https://medium.com/digital-transformation-and-platform-engineering/apache-airflow-best-practices-and-advantages-9ec71f1ef3cc)
- [Best Practices - Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Apache Airflow – How to write DAGs and master all best practices](https://itgix.com/blog/apache-airflow-how-to-write-dags-and-master-all-best-practices/)

## 👏 Contatos e agradecimentos

- hilton.martins@academico.ufpb.br
- alessio.almeida@academico.ufpb.br
