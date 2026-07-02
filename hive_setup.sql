CREATE DATABASE IF NOT EXISTS ndox_sn;
USE ndox_sn;

CREATE TABLE IF NOT EXISTS pression_historique (
    capteur_secure STRING,
    zone STRING,
    pression_bars DOUBLE,
    pression_nominale DOUBLE,
    debit_m3h DOUBLE,
    statut_capteur STRING,
    age_canalisation_ans DOUBLE,
    ingestion_ts TIMESTAMP
)
PARTITIONED BY (date_obs STRING)
STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

CREATE OR REPLACE VIEW vue_etat_reseau AS
SELECT
    zone,
    AVG(pression_bars / COALESCE(pression_nominale,4.0)) AS ratio_pression_moy,
    MIN(pression_bars) AS pression_mini,
    AVG(age_canalisation_ans) AS age_moy_canalisation,
    SUM(CASE WHEN statut_capteur = 'RUPTURE_IMMINENTE' THEN 1 ELSE 0 END) AS nb_alertes_24h,
    CASE
        WHEN AVG(pression_bars/COALESCE(pression_nominale,4.0)) < 0.4 THEN 'CRITIQUE'
        WHEN AVG(pression_bars/COALESCE(pression_nominale,4.0)) < 0.7 THEN 'ALERTE'
        ELSE 'NORMAL'
    END AS statut_zone
FROM pression_historique
WHERE date_obs >= DATE_SUB(CURRENT_DATE(), 1)
GROUP BY zone;

CREATE OR REPLACE VIEW vue_maintenance_prioritaire AS
SELECT
    zone,
    AVG(age_canalisation_ans) AS age_moy,
    COUNT(CASE WHEN statut_capteur != 'NORMAL' THEN 1 END) AS nb_incidents,
    AVG(age_canalisation_ans) * 0.4 + COUNT(CASE WHEN statut_capteur != 'NORMAL' THEN 1 END) * 0.6 AS score_priorite
FROM pression_historique
GROUP BY zone
ORDER BY score_priorite DESC;