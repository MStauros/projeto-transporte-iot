#!/bin/bash

COMPOSE_FILE="../docker-compose.yml"
PROJECT_NAME="kafka-postgres-demo"

start_environment() {
    echo "Iniciando Kafka, Zookeeper, PostgreSQL e PGAdmin..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    echo -e "\nAcesse:"
    echo "- PGAdmin: http://localhost:5050 (admin@admin.com/admin123)"
    echo "- Kafka: localhost:9092"
    echo "- PostgreSQL: localhost:5432 (admin/admin123)"
}

stop_environment() {
    echo "Parando containers..."
    docker-compose -p $PROJECT_NAME down
}

clean_environment() {
    echo "Removendo containers, volumes e redes..."
    docker-compose -p $PROJECT_NAME down -v
    docker volume prune -f
    docker network prune -f
}

status_environment() {
    echo "Status dos containers:"
    docker-compose -p $PROJECT_NAME ps
    echo -e "\nEndereços úteis:"
    echo "- PGAdmin: http://localhost:5050"
    echo "- Kafka: localhost:9092"
}

case "$1" in
    start)
        start_environment
        ;;
    stop)
        stop_environment
        ;;
    clean)
        clean_environment
        ;;
    status)
        status_environment
        ;;
    *)
        echo "Uso: $0 {start|stop|clean|status}"
        echo "Comandos:"
        echo "  start   : Inicia todos os serviços"
        echo "  stop    : Para os serviços mantendo volumes"
        echo "  clean   : Remove tudo (containers, volumes, redes)"
        echo "  status  : Mostra o estado dos containers"
        exit 1
esac

exit 0