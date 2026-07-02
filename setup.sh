#!/bin/bash
set -e

echo "Création des dossiers..."
mkdir -p data dags models dashboard tests

echo "Lancement de Docker Compose..."
cd docker
docker compose up -d

echo "Attente de la disponibilité de HBase (port 9090)..."
# Attendre que le port 9090 soit ouvert sur localhost
while ! nc -z localhost 9090; do
    sleep 2
    echo "En attente de HBase..."
done
echo "HBase est prêt !"
docker exec -i docker-hbase-1 hbase shell <<< "create_namespace 'ndox'"

echo "Création des tables HBase..."
cd ..
cd scripts
python3 hbase_setup.py

#echo "Lancement du simulateur Kafka (arrière-plan)..."
#python3 kafka_producer_ndox_sn.py &


echo "Infrastructure prête !"
echo "Accès :"

echo "  Spark Master   : http://localhost:8080"
echo "  HBase Master   : http://localhost:16010"
echo "  Airflow        : http://localhost:8082"
