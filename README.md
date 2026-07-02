# Ndocx-SN — Prédiction des ruptures de réseau d'eau au Sénégal

> **Ndox** signifie « eau » en Wolof.  
> Projet tutoré inscrit dans la **Stratégie Sénégal Numérique 2025-2035** et le **Plan Sénégal Émergent (PSE)**.  
> Système de prédiction des ruptures imminentes du réseau de distribution d'eau (SONES/Sen Eau) avec maintenance préventive et optimisation des camions citernes en zones rurales.

---

## Architecture

```
┌────────────────────────────────────────────┐
│  Kafka Producers (simulation)              │
│  ndox_pression_raw / ndox_conso_raw        │
└────────────┬───────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────┐
│  Spark Structured Streaming                │
│  Anonymisation SHA-256, fenêtrage 1h,      │
│  calcul criticité → ndox_alerts + Parquet  │
└────────────┬───────────────────────────────┘
             │
    ┌────────┴────────┬──────────────────┐
    ▼                 ▼                  ▼
┌─────────┐    ┌──────────┐     ┌──────────┐
│  HBase  │    │  Hive    │     │ Airflow  │
│ temps   │    │ ORC      │     │ DAG      │
│ réel    │    │ SNAPPY   │     │ toutes   │
│         │    │ historiq │     │ 4h       │
└─────────┘    └──────────┘     └────┬─────┘
                                      │
                                      ▼
                              ┌────────────────┐
                              │  ML (GBT)       │
                              │  MLflow + AUC   │
                              └────────────────┘
                                      │
                                      ▼
                              ┌────────────────┐
                              │  Dashboard     │
                              │  (Matplotlib)  │
                              └────────────────┘
```

## Stack technique

| Composant               | Technologie |
|------------------------|-------------|
| Ingestion              | Kafka (Confluent 7.4.0) |
| Streaming              | Spark Structured Streaming 3.5.7 |
| Base temps réel        | HBase |
| Base historique        | Hive 4.0.0 (ORC + SNAPPY) |
| Orchestration          | Airflow 2.7.3 |
| Machine Learning       | GBTClassifier + MLflow 2.8.1 |
| ETL / Flow             | Apache NiFi 1.23.2 |
| Dashboard              | Matplotlib 3.7.3 / Seaborn 0.12.2 |
| Conteneurisation       | Docker Compose |

## Prérequis

- RAM : 16 Go minimum
- CPU : 4 cœurs
- OS : Ubuntu 22.04 LTS
- Docker Engine 24.x + Docker Compose
- Java 11
- Python 3.9+

## Installation

```bash
git clone <url-du-repo>
cd ndox-sn
chmod +x setup.sh
./setup.sh
```

Le script `setup.sh` :
1. Crée les répertoires (`data/`, `dags/`, `models/`, `dashboard/`, `tests/`)
2. Lance Docker Compose (Zookeeper, Kafka, NiFi, HBase, Hive, Spark, Airflow)
3. Crée le namespace et les tables HBase (`ndox:capteurs_temps_reel`, `ndox:alertes_rupture`, `ndox:tournees_citernes`)
4. Lance le simulateur Kafka de données pression/consommation

## Interfaces web

| Service       | Port |
|---------------|------|
| Spark Master  | 8081 |
| HBase Master  | 16010 |
| Airflow       | 8082 |
| Hive JDBC     | 10000 |

## Structure du projet

```
uadb-m2-ndox-sn/
├── docker/
│   ├── docker-compose.yml     # 9 services (Zk, Kafka, NiFi, HBase, Hive, Spark M+W, Postgres, Airflow)
│   ├── Dockerfile              # Image Airflow custom
│   └── requirements-airflow.txt
├── scripts/
│   ├── kafka_producer_ndox_sn.py   # Simulateur données (7 zones Sénégal)
│   ├── streaming_ndox_sn.py        # Pipeline Spark Streaming
│   ├── kafka_to_hbase.py           # Consommateur Kafka → HBase
│   └── hbase_setup.py              # Création tables HBase
├── dags/
│   └── ndox_sn_dag.py              # DAG Airflow (branch retrain/update)
├── models/
│   └── train_rupture_model.py      # GBTClassifier + MLflow
├── dashboard/
│   └── dashboard_priorites.png     # Dashboard (PNG uniquement)
├── hive_setup.sql                  # DDL Hive (ORC partitionné)
├── requirements.txt
├── setup.sh
└── README.md
```

## Détail des composants

### Simulateur Kafka (`scripts/kafka_producer_ndox_sn.py`)

- 7 zones : DAKAR_NORD, DAKAR_SUD, PIKINE, THIES, SAINT_LOUIS, KAOLACK, ZIGUINCHOR
- Pression nominale : 2.8–4.5 bars selon zone
- Fragilité réseau : 0.05–0.25 (probabilité de rupture)
- Consommation avec pics matin (6-8h) et soir (18-20h)
- Production toutes les 5 secondes

### Pipeline Spark (`scripts/streaming_ndox_sn.py`)

- Lecture Kafka topic `ndox_pression_raw`
- Ratio pression + criticité (CRITIQUE &lt; 0.3, ALERTE &lt; 0.6, SURVEILLANCE &lt; 0.8, NORMAL)
- Anonymisation SHA-256 des capteurs
- Score de priorité composite :
  - 40% écart de pression normalisé
  - 30% débit bas
  - 20% âge canalisation
  - 10% statut anormal
- Sortie Parquet partitionnée par zone

### Hive (`hive_setup.sql`)

- Table `pression_historique` : ORC + SNAPPY, partitionnée par `date_obs`
- Vue `vue_etat_reseau` : ratio pression, alertes, statut zone par jour
- Vue `vue_maintenance_prioritaire` : score = age × 0.4 + incidents × 0.6

### DAG Airflow (`dags/ndox_sn_dag.py`)

- `ndox_sn_monitoring` toutes les 4h
- `BranchPythonOperator` : si > 1 zone CRITIQUE → retrain, sinon → update_alerts
- `retrain_model` : `spark-submit` du modèle ML
- `update_alerts` : écriture des alertes dans HBase

### Modèle ML (`models/train_rupture_model.py`)

- GBTClassifier (maxIter=50, maxDepth=5)
- Features : `ratio_pression_moy`, `age_moy_canalisation`, `nb_alertes_24h`
- Label : `statut_zone = 'CRITIQUE'`
- Métrique : AUC ROC
- Tracking : MLflow experiment `ndox_rupture`

---

## Corrections appliquées

| # | Problème | Correctif |
|---|----------|-----------|
| 1 | **Pipeline interrompu** | `streaming_ndox_sn.py`← lit maintenant `ndox_pression_raw` (topic produit). Criticité calculée en continu (CRITIQUE/ALERTE/SURVEILLANCE/NORMAL) + anonymisation SHA-256. |
| 2 | **`kafka_to_hbase.py` utilise `subprocess`** | Réécrit avec `happybase.Connection` et `table.put()` — plus de `docker exec`. |
| 3 | **Tests absents** | Créés : `tests/test_schemas.py` (validation Pandera des schémas pression/consommation) + `tests/test_udfs.py` (anonymisation SHA-256, criticité). |
| 4 | **Dashboard sans code source** | Créé : `dashboard/dashboard_ndox.py` — barplot priorités + optimisation tournées (plus proche voisin). |
| 5 | **`.gitignore` vide** | Créé avec règles pour `__pycache__/`, `nifi-data/`, `postgres-data/`, `models/metastore_db/`, `derby.log`, `.env`, etc. |
| 6 | **Pas de validation de schéma** | `tests/test_schemas.py` avec Pandera : validation des colonnes, types, plages, motifs regex pour les 2 flux (pression + consommation). |

> Note : Le montage Docker Compose (`../dags:/opt/airflow/dags`) est déjà correct — le dossier racine `dags/` est bien accessible depuis Airflow.

## Tests

```bash
cd ndox-sn
pip install -r requirements.txt
pytest tests/ -v
```

## Licence

## Licence

Projet tutoré — Université.