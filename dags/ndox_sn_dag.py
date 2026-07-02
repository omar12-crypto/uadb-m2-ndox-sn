from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import subprocess, logging
from pyhive import hive
import happybase
from datetime import datetime

logger = logging.getLogger('ndox_dag')
default_args = {
    'owner': 'omar_coumba',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

def check_ruptures(**context):
    # Airflow tourne dans un conteneur, on utilise le nom du service hive-metastore
    conn = hive.Connection(host='hive-metastore', port=10000)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ndox_sn.vue_etat_reseau WHERE statut_zone='CRITIQUE'")
    n = cur.fetchone()[0]
    return 'retrain_model' if n > 1 else 'update_alerts'

def retrain_model(**context):
    subprocess.run(['spark-submit', '--master', 'spark://spark-master:7077',
                    '/opt/models/train_rupture_model.py'], check=True, timeout=3600)

def update_alerts(**context):
    conn_hbase = happybase.Connection('hbase', port=9090)
    conn_hbase.open()
    conn_hive = hive.Connection(host='hive-metastore', port=10000)
    cur = conn_hive.cursor()
    cur.execute("SELECT zone, ratio_pression_moy, nb_alertes_24h, statut_zone FROM ndox_sn.vue_etat_reseau")
    table = conn_hbase.table(b'ndox:alertes_rupture')
    for row in cur.fetchall():
        zone, ratio, nb, statut = row
        if statut != 'NORMAL':
            table.put(zone.encode(), {
                b'alerte:zone': zone.encode(),
                b'alerte:ratio': str(round(ratio,3)).encode(),
                b'alerte:statut': statut.encode(),
                b'alerte:ts': datetime.utcnow().isoformat().encode()
            })
    conn_hbase.close()

with DAG(
    'ndox_sn_monitoring',
    default_args=default_args,
    schedule_interval='0 */4 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['ndox-sn', 'eau', 'assainissement']
) as dag:
    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    branch = BranchPythonOperator(
        task_id='check_ruptures',
        python_callable=check_ruptures,
        provide_context=True
    )
    t_train = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model,
        provide_context=True
    )
    t_alert = PythonOperator(
        task_id='update_alerts',
        python_callable=update_alerts,
        provide_context=True
    )
    start >> branch >> [t_train, t_alert]
    t_train >> t_alert >> end
    t_alert >> end