# Projeto de Monitoramento de Transportes IoT

## Descrição do Projeto

Este projeto implementa um sistema de monitoramento de dados de transportes baseado em uma arquitetura de streaming, utilizando Kafka para ingestão de dados em tempo real e PostgreSQL para persistência e agregação. O objetivo é simular um fluxo de dados de sensores IoT de um aplicativo de transporte privado, processá-los e armazená-los para análise.

O pipeline de dados consiste em:
1.  **Produtor (Producer)**: Simula a geração de dados de viagens.
2.  **Apache Kafka**: Atua como uma plataforma de streaming para a ingestão e transporte dos dados de viagens.
3.  **Consumidor (Consumer)**: Processa as mensagens do Kafka e as persiste em um banco de dados PostgreSQL.
4.  **Agregador de Dados Diários**: Processa os dados brutos de viagens e gera uma tabela sumarizada com métricas diárias.
5.  **PostgreSQL**: Banco de dados relacional para armazenamento dos dados de viagens e dos dados agregados.


## Como Iniciar o Projeto Localmente

Certifique-se de ter Docker, Docker Compose, Python 3.11 e Poetry instalados.

1.  **Clonar o Repositório:**
    ```bash
    git clone <https://github.com/MStauros/projeto-transporte-iot.git>
    cd <nome_da_pasta_do_projeto>
    ```

2.  **Conceder Permissões de Execução (Linux/macOS ou Git Bash no Windows):**
    ```bash
    chmod +x scripts/setup-local-env.sh
    ```

3.  **Iniciar os Serviços Docker:**
    Este comando construirá as imagens Docker (se necessário) e levantará todos os serviços (Kafka, Zookeeper, PostgreSQL, PGAdmin, Consumer, Producer, Aggregator) em segundo plano.

    ```bash
    ./scripts/setup-local-env.sh start
    ```

4.  **Verificar o Status dos Contêineres:**
    Confirme que todos os serviços estão `Up` e `(healthy)`.
    ```bash
    ./scripts/setup-local-env.sh status
    ```

5.  **Monitorar os Logs do Consumidor (Opcional):**
    Para ver o consumidor processando as mensagens em tempo real (abra um novo terminal):
    ```bash
    docker-compose logs -f viagem-consumer
    ```

6.  **Acessar o PGAdmin:**
    Abra seu navegador e acesse `http://localhost:5050`.
    * **Credenciais do PGAdmin:** Email: `admin@admin.com` | Senha: `admin123`
    * **Conexão ao Servidor PostgreSQL:**
        * Host: `postgres`
        * Porta: `5432`
        * Banco de Dados: `iot`
        * Usuário: `admin`
        * Senha: `admin123`
    Você deverá ver a tabela `viagens` sendo populada pelos dados do consumidor.

## Como Executar o Agregador de Dados Diários (Fase 8)

O script `daily_aggregator.py` pode ser executado como um serviço `run` do Docker Compose, de forma independente do consumidor e produtor (embora precise que a tabela `viagens` tenha dados).

1.  **Execute o Serviço Agregador:**
    ```bash
    docker-compose run --rm aggregator
    ```
    Este comando criará um contêiner temporário, executará o script de agregação e o removerá após a conclusão. Verifique os logs no seu terminal para confirmar o sucesso da agregação.

2.  **Verificar a Tabela `info_corridas_do_dia`:**
    Após a execução do agregador, acesse o PGAdmin para inspecionar a nova tabela `info_corridas_do_dia` com os dados sumarizados.

## Como Executar os Testes

Este projeto inclui testes unitários para garantir a qualidade do código e do fluxo de dados.

1.  **Garantir o Ambiente Principal Ativo:**
    Certifique-se de que seus serviços principais (Kafka, Postgres) estão rodando: `./scripts/setup-local-env.sh status`.


## CI/CD com GitHub Actions

Este projeto está configurado com um pipeline de CI/CD usando GitHub Actions, definido em `.github/workflows/main_ci_cd.yml`.

O pipeline é acionado em `push` e `pull_request` para as branches `main` e `develop` e executa as seguintes etapas:

* **Checkout do Código**: Baixa o código do repositório.
* **Configuração do Ambiente Python**: Configura o Python 3.11.
* **Instalação de Dependências**: Utiliza Poetry para instalar as dependências do projeto.
* **Linting**: Executa Black, Flake8 e Isort para garantir a conformidade com padrões de estilo.
* **Testes Unitários**: Roda os testes definidos em `tests/unit/`.
* **Build das Imagens Docker**: Constrói as imagens dos serviços `producer` e `consumer`.

Para verificar o status das execuções do CI/CD, acesse a aba "Actions" no seu repositório GitHub.

## Limpeza do Ambiente Local

Para parar e remover todos os contêineres, volumes e redes criados pelo projeto:

```bash
./scripts/setup-local-env.sh clean