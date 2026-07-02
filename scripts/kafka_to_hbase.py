#!/usr/bin/env python3
from kafka import KafkaConsumer
import json
import time
import sys
import happybase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('KafkaToHBase')

KAFKA_BROKERS = 'localhost:9092'
KAFKA_TOPIC = 'ndox_pression_raw'
CONSUMER_GROUP = 'hbase_writer_group'
HBASE_HOST = 'localhost'
HBASE_PORT = 9090
HBASE_TABLE = 'ndox:alertes_rupture'


def create_consumer():
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKERS,
            group_id=CONSUMER_GROUP,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        logger.info(f"Connecté à Kafka (%s), topic : %s", KAFKA_BROKERS, KAFKA_TOPIC)
        return consumer
    except Exception as e:
        logger.error("Erreur de connexion à Kafka : %s", e)
        sys.exit(1)


def get_hbase_connection():
    try:
        conn = happybase.Connection(HBASE_HOST, port=HBASE_PORT, timeout=10000)
        conn.open()
        return conn
    except Exception as e:
        logger.error("Erreur de connexion HBase : %s", e)
        return None


def process_message(msg, table):
    data = msg.value
    zone = data.get('zone')
    if not zone:
        logger.warning("Message sans zone, ignoré")
        return

    pression = data.get('pression_bars')
    pression_nom = data.get('pression_nominale')
    statut = data.get('statut_capteur', 'INCONNU')
    timestamp = data.get('timestamp')

    if pression is None or pression_nom is None or pression_nom == 0:
        ratio = 0.0
    else:
        ratio = pression / pression_nom

    table.put(zone.encode(), {
        b'meta:pression': str(pression).encode(),
        b'meta:statut': statut.encode(),
        b'meta:ratio': f'{ratio:.2f}'.encode(),
        b'meta:ts': (timestamp or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())).encode(),
    })
    logger.info("✓ Écrit HBase : %s | pression=%s | ratio=%.2f | statut=%s", zone, pression, ratio, statut)


def main():
    logger.info("Démarrage du consommateur Kafka -> HBase (via HappyBase)")
    consumer = create_consumer()
    conn = get_hbase_connection()
    if conn is None:
        consumer.close()
        sys.exit(1)

    table = conn.table(HBASE_TABLE.encode())
    try:
        for msg in consumer:
            process_message(msg, table)
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur.")
    finally:
        consumer.close()
        conn.close()
        logger.info("Consommateur et connexion HBase fermés.")


if __name__ == "__main__":
    main()