from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, Image, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

OUTPUT = "rapport_ndox_sn.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    topMargin=2*cm,
    bottomMargin=2*cm,
    leftMargin=2.5*cm,
    rightMargin=2.5*cm,
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    'CoverTitle', parent=styles['Title'],
    fontSize=28, leading=34, textColor=HexColor('#1a5276'),
    spaceAfter=6, alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    'CoverSubtitle', parent=styles['Normal'],
    fontSize=14, leading=18, textColor=HexColor('#2c3e50'),
    spaceAfter=4, alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    'SectionTitle', parent=styles['Heading1'],
    fontSize=18, leading=22, textColor=HexColor('#1a5276'),
    spaceBefore=16, spaceAfter=8, borderWidth=0
))
styles.add(ParagraphStyle(
    'SubSection', parent=styles['Heading2'],
    fontSize=14, leading=18, textColor=HexColor('#2c7fb8'),
    spaceBefore=12, spaceAfter=6
))
styles.add(ParagraphStyle(
    'SubSubSection', parent=styles['Heading3'],
    fontSize=12, leading=15, textColor=HexColor('#34495e'),
    spaceBefore=8, spaceAfter=4
))
styles.add(ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontSize=10, leading=14, alignment=TA_JUSTIFY,
    spaceAfter=6
))
styles.add(ParagraphStyle(
    'CodeBlock', parent=styles['Code'],
    fontSize=8, leading=10, backColor=HexColor('#f4f6f7'),
    leftIndent=8, spaceAfter=4, spaceBefore=4,
    fontName='Courier'
))
styles.add(ParagraphStyle(
    'NDBullet', parent=styles['Normal'],
    fontSize=10, leading=14, leftIndent=20,
    bulletIndent=8, spaceAfter=3
))
styles.add(ParagraphStyle(
    'NDTableHeader', parent=styles['Normal'],
    fontSize=9, leading=12, textColor=colors.white,
    alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    'NDTableCell', parent=styles['Normal'],
    fontSize=8, leading=11, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    'NDFooter', parent=styles['Normal'],
    fontSize=8, leading=10, textColor=HexColor('#7f8c8d'),
    alignment=TA_CENTER
))

def section(title):
    return Paragraph(title, styles['SectionTitle'])

def subsection(title):
    return Paragraph(title, styles['SubSection'])

def subsubsection(title):
    return Paragraph(title, styles['SubSubSection'])

def body(text):
    return Paragraph(text, styles['Body'])

def code(text):
    return Paragraph(text.replace('\n', '<br/>'), styles['CodeBlock'])

def ndbullet(text):
    return Paragraph(f"&bull; {text}", styles['NDBullet'])

def spacer(h=6):
    return Spacer(1, h)

def hr():
    return HRFlowable(width="100%", thickness=1, color=HexColor('#bdc3c7'))

def make_table(headers, rows, col_widths=None):
    data = [[Paragraph(h, styles['NDTableHeader'])] for h in headers]
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdc3c7')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t

story = []

# === COVER PAGE ===
story.append(Spacer(1, 60))
story.append(Paragraph("Ndocx-SN", styles['CoverTitle']))
story.append(Paragraph("Intelligence Hydrique &amp; Prédiction des Ruptures", styles['CoverSubtitle']))
story.append(Paragraph("de Réseau d'Eau et Assainissement", styles['CoverSubtitle']))
story.append(spacer(30))
story.append(Paragraph("Rapport Technique et de Vérification de Code", styles['CoverSubtitle']))
story.append(spacer(10))
story.append(hr())
story.append(spacer(10))
story.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", styles['CoverSubtitle']))
story.append(Paragraph("Version : 1.0", styles['CoverSubtitle']))
story.append(Paragraph("Contexte : Projet tutoré — Université", styles['CoverSubtitle']))
story.append(spacer(40))
story.append(body(
    "<i>Ce rapport présente l'architecture, les composants techniques, "
    "la vérification du code et les corrections apportées au projet "
    "Ndocx-SN, système de prédiction des ruptures du réseau "
    "d'eau potable au Sénégal.</i>"
))
story.append(PageBreak())

# === TABLE OF CONTENTS ===
story.append(section("Table des matières"))
story.append(spacer(10))
toc = [
    "Contexte et objectifs",
    "Architecture technique",
    "Stack technologique",
    "Structure du projet",
    "Composants détaillés",
    "Vérification du code",
    "Corrections appliquées",
    "Guide d'utilisation",
    "Tests",
    "Conclusion",
]
for i, t in enumerate(toc, 1):
    story.append(Paragraph(f"{i:02d}.  {t}", styles['Bullet']))
story.append(PageBreak())

# === 1. CONTEXTE ===
story.append(section("1. Contexte et objectifs"))
story.append(body(
    "Au Sénégal, 3 millions de personnes n'ont pas accès à l'eau potable. "
    "Les ruptures du réseau de distribution d'eau coûtent environ "
    "<b>15 milliards FCFA par an</b>. Le projet <b>Ndocx-SN</b> (Ndox = « eau » en Wolof) "
    "s'inscrit dans la <b>Stratégie Sénégal Numérique 2025-2035</b> et "
    "le <b>Plan Sénégal Émergent (PSE)</b>."
))
story.append(body("Objectifs du projet :"))
objectifs = [
    "<b>Ingestion multi-sources</b> : capteurs de pression SONES, données pluviométriques, consommation par zone",
    "<b>Prédiction des ruptures à 48h</b> avec classification de criticité (CRITIQUE, ALERTE, SURVEILLANCE, NORMAL)",
    "<b>Optimisation des tournées de camions citernes</b> dans les zones non raccordées",
    "<b>Privacy by Design</b> : anonymisation SHA-256 des compteurs résidentiels",
    "<b>Dashboard SONES</b> : carte réseau, alertes en temps réel, recommandations de maintenance",
]
for o in objectifs:
    story.append(ndbullet(o))

# === 2. ARCHITECTURE ===
story.append(section("2. Architecture technique"))
story.append(body(
    "L'architecture suit un pipeline de données <i>end-to-end</i> allant "
    "de la simulation de capteurs jusqu'au tableau de bord décisionnel :"
))
story.append(spacer(6))

arch_lines = [
    "┌────────────────────────────────────────────────────────────────┐",
    "│               Kafka Producers (simulation)                      │",
    "│  kafka_producer_ndox_sn.py → topics: ndox_pression_raw         │",
    "│                               ndox_conso_raw                    │",
    "└──────────────────────────┬─────────────────────────────────────┘",
    "                           │",
    "                           ▼",
    "┌────────────────────────────────────────────────────────────────┐",
    "│            Spark Structured Streaming                           │",
    "│  streaming_ndox_sn.py — ratio pression, criticité, score       │",
    "│  Anonymisation SHA-256, écriture Parquet + HBase               │",
    "└──────────────────────────┬─────────────────────────────────────┘",
    "                           │",
    "                  ┌────────┴────────┬────────────────┐",
    "                  ▼                 ▼                ▼",
    "           ┌──────────┐     ┌──────────┐     ┌──────────┐",
    "           │  HBase   │     │   Hive   │     │ Airflow  │",
    "           │ temps    │     │   ORC    │     │   DAG    │",
    "           │ réel     │     │  SNAPPY  │     │  toutes  │",
    "           │          │     │ historique│    │   4h     │",
    "           └──────────┘     └──────────┘     └────┬─────┘",
    "                                                   │",
    "                                                   ▼",
    "                                           ┌──────────────┐",
    "                                           │  ML (GBT)     │",
    "                                           │  + MLflow     │",
    "                                           └──────────────┘",
    "                                                   │",
    "                                                   ▼",
    "                                           ┌──────────────┐",
    "                                           │  Dashboard   │",
    "                                           │ (Matplotlib) │",
    "                                           └──────────────┘",
]
for l in arch_lines:
    story.append(Paragraph(l.replace(' ', '&nbsp;'), styles['CodeBlock']))

story.append(Paragraph("Figure 1 — Architecture end-to-end du pipeline Ndocx-SN", ParagraphStyle(
    'FigCaption', parent=styles['Normal'], fontSize=9, leading=12,
    alignment=TA_CENTER, textColor=HexColor('#7f8c8d'), spaceAfter=10
)))

# === 3. STACK ===
story.append(section("3. Stack technologique"))

stack_headers = ['Composant', 'Technologie', 'Version']
stack_rows = [
    ['Ingestion streaming', 'Apache Kafka (Confluent)', '7.4.0'],
    ['Processing streaming', 'Spark Structured Streaming', '3.5.7'],
    ['Base temps réel', 'Apache HBase', 'latest (harisekhon)'],
    ['Base historique', 'Apache Hive', '4.0.0'],
    ['Orchestration', 'Apache Airflow', '2.7.3'],
    ['Machine Learning', 'GBTClassifier via PySpark', '3.3.2'],
    ['ML tracking', 'MLflow', '2.8.1'],
    ['Dashboard', 'Matplotlib / Seaborn', '3.7.3 / 0.12.2'],
    ['Conteneurisation', 'Docker Compose', '3.8'],
    ['Validation données', 'Pandera', '0.17.2'],
    ['ETL/Flow', 'Apache NiFi', '1.23.2'],
    ['Queue / coordination', 'Zookeeper', '7.4.0'],
]
story.append(make_table(stack_headers, stack_rows, col_widths=[90, 160, 60]))
story.append(spacer(10))

# === 4. STRUCTURE ===
story.append(section("4. Structure du projet"))
story.append(body("Arborescence complète du dépôt après corrections :"))
story.append(spacer(4))

tree = [
    "ndox-sn/",
    "├── .gitignore                  # Règles d'ignorance (corrigé)",
    "├── requirements.txt            # Dépendances Python",
    "├── setup.sh                    # Script de déploiement",
    "├── hive_setup.sql              # DDL Hive (ORC + SNAPPY)",
    "├── README.md                   # Documentation",
    "├──",
    "├── docker/",
    "│   ├── docker-compose.yml      # 9 services (Zk, Kafka, NiFi, HBase, Hive, Spark M+W, Postgres, Airflow)",
    "│   ├── Dockerfile              # Image Airflow custom",
    "│   └── requirements-airflow.txt",
    "├──",
    "├── scripts/",
    "│   ├── kafka_producer_ndox_sn.py   # Simulateur données (7 zones Sénégal)",
    "│   ├── streaming_ndox_sn.py        # Pipeline Spark (corrigé)",
    "│   ├── kafka_to_hbase.py           # Kafka → HBase via HappyBase (corrigé)",
    "│   └── hbase_setup.py              # Création tables HBase",
    "├──",
    "├── dags/",
    "│   └── ndox_sn_dag.py              # DAG Airflow (branch retrain/update)",
    "├──",
    "├── models/",
    "│   └── train_rupture_model.py      # GBTClassifier + MLflow",
    "├──",
    "├── dashboard/",
    "│   ├── __init__.py",
    "│   ├── dashboard_ndox.py           # Barplot + optimisation tournées (créé)",
    "│   └── dashboard_priorites.png     # Exemple de sortie",
    "├──",
    "├── tests/",
    "│   ├── __init__.py",
    "│   ├── test_schemas.py             # Validation Pandera (créé)",
    "│   └── test_udfs.py                # Tests unitaires (créé)",
    "├──",
    "├── data/                           # Sortie Parquet du streaming",
    "├── rapport/                        # Rapports générés",
    "└── nifi_templates/                 # Templates NiFi (placeholders)",
]
for l in tree:
    story.append(Paragraph(l.replace(' ', '&nbsp;'), styles['CodeBlock']))

# === 5. COMPOSANTS ===
story.append(section("5. Composants détaillés"))

# 5.1 Producer
story.append(subsection("5.1 Simulateur Kafka (kafka_producer_ndox_sn.py)"))
story.append(body(
    "Génère aléatoirement mais de manière réaliste des données de pression et consommation "
    "pour les 7 zones du réseau SONES :"
))
story.append(spacer(4))

zones_header = ['Zone', 'Pression nominale', 'Fragilité réseau', 'Population relative']
zones_rows = [
    ['DAKAR_NORD', '4.5 bars', '0.05', 'Très élevée'],
    ['DAKAR_SUD', '4.2 bars', '0.08', 'Très élevée'],
    ['PIKINE', '3.8 bars', '0.20', 'Élevée'],
    ['THIES', '3.5 bars', '0.15', 'Moyenne'],
    ['SAINT_LOUIS', '3.2 bars', '0.18', 'Moyenne'],
    ['KAOLACK', '3.0 bars', '0.22', 'Faible'],
    ['ZIGUINCHOR', '2.8 bars', '0.25', 'Faible'],
]
story.append(make_table(zones_header, zones_rows, col_widths=[80, 80, 70, 80]))
story.append(spacer(6))
story.append(body(
    "Champ <b>statut_capteur</b> : NORMAL (majorité), PRESSION_BASSE (10% probabilité), "
    "RUPTURE_IMMINENTE (période de fragilité). Consommation avec pics matin (6-8h) "
    "et soir (18-20h) — facteur 1.5x. Production toutes les 5 secondes."
))

# 5.2 Streaming
story.append(subsection("5.2 Pipeline Spark Streaming (streaming_ndox_sn.py) [CORRIGÉ]"))
story.append(body(
    "Lecture depuis le topic Kafka <b>ndox_pression_raw</b> (corrigé — lisait auparavant "
    "le topic inexistant ndox_alerts). Fonctionnalités :"
))
streaming_items = [
    "Anonymisation SHA-256 des capteurs avec salt via variable d'environnement NDOX_SECRET_SALT",
    "Calcul du ratio pression = pression_bars / pression_nominale",
    "Criticité : &lt; 0.3 → CRITIQUE, &lt; 0.6 → ALERTE, &lt; 0.8 → SURVEILLANCE, sinon NORMAL",
    "Score de priorité composite : 40% écart pression + 30% débit bas + 20% âge cana. + 10% statut",
    "Écriture Parquet partitionnée par zone (triggers 30s)",
]
for item in streaming_items:
    story.append(ndbullet(item))

# 5.3 HBase
story.append(subsection("5.3 Tables HBase"))
story.append(body("Namespace <b>ndox</b> avec 3 tables :"))
hbase_header = ['Table', 'Famille', 'Usage']
hbase_rows = [
    ['ndox:capteurs_temps_reel', 'meta', 'Données capteurs en temps réel'],
    ['ndox:alertes_rupture', 'meta, alerte', 'Alertes de rupture imminente'],
    ['ndox:tournees_citernes', 'meta', 'Planification tournées camions'],
]
story.append(make_table(hbase_header, hbase_rows, col_widths=[100, 60, 150]))

# 5.4 Hive
story.append(subsection("5.4 Vues Hive (hive_setup.sql)"))
story.append(body("Table <b>pression_historique</b> : stockage ORC compressé SNAPPY, partitionnée par date_obs."))
hive_items = [
    "<b>vue_etat_reseau</b> : ratio pression moyen, min pression, âge moyen cana., nb alertes RUPTURE_IMMINENTE, statut zone par jour",
    "<b>vue_maintenance_prioritaire</b> : score de priorité composite = âge × 0.4 + incidents × 0.6, trié par score descendant",
]
for item in hive_items:
    story.append(ndbullet(item))

# 5.5 Airflow
story.append(subsection("5.5 DAG Airflow (dags/ndox_sn_dag.py)"))
story.append(body(
    "DAG <b>ndox_sn_monitoring</b> exécuté toutes les 4 heures. "
    "Logique de branchement conditionnel :"
))
story.append(body(
    "1. <b>check_ruptures</b> (BranchPythonOperator) : interroge <i>vue_etat_reseau</i> — "
    "si &gt; 1 zone CRITIQUE → branche <i>retrain_model</i>, sinon <i>update_alerts</i>"
))
story.append(body(
    "2. <b>retrain_model</b> (PythonOperator) : lance <i>spark-submit</i> de train_rupture_model.py "
    "sur spark://spark-master:7077"
))
story.append(body(
    "3. <b>update_alerts</b> (PythonOperator) : lit la vue Hive et écrit les alertes "
    "(zone, ratio, statut, timestamp) dans HBase"
))

# 5.6 ML
story.append(subsection("5.6 Modèle ML (models/train_rupture_model.py)"))
ml_items = [
    "Algorithme : Gradient Boosting Classifier (GBTClassifier)",
    "Hyperparamètres : maxIter=50, maxDepth=5, seed=42",
    "Features : ratio_pression_moy, age_moy_canalisation, nb_alertes_24h",
    "Label : 1 si statut_zone = 'CRITIQUE', 0 sinon",
    "Métrique : AUC ROC via BinaryClassificationEvaluator",
    "Tracking : MLflow experiment 'ndox_rupture'",
]
for item in ml_items:
    story.append(ndbullet(item))

# 5.7 Dashboard
story.append(subsection("5.7 Dashboard (dashboard/dashboard_ndox.py) [CRÉÉ]"))
story.append(body(
    "Script de visualisation et d'optimisation créé pour remplacer le PNG "
    "statique qui était seul présent dans le dossier :"
))
dash_items = [
    "Barplot horizontal des scores de priorité par zone (avec couleurs par niveau)",
    "Optimisation des tournées de citernes : plus proche voisin (nearest-neighbor) "
    "sur les 3 zones les plus critiques",
    "Génération d'une image PNG : dashboard/dashboard_priorites.png",
    "Données de test générées aléatoirement (seed 42) pour démonstration",
]
for item in dash_items:
    story.append(ndbullet(item))

# === 6. CODE VERIFICATION ===
story.append(section("6. Vérification du code"))
story.append(body(
    "Une revue systématique du code a été effectuée. Six problèmes ont été "
    "identifiés et corrigés :"
))
story.append(spacer(4))

issues_header = ['#', 'Problème', 'Sévérité']
issues_rows = [
    ['1', 'Pipeline interrompu — streaming lit un topic Kafka inexistant (ndox_alerts)', 'Critique'],
    ['2', 'kafka_to_hbase.py utilise subprocess + docker exec au lieu du client HappyBase', 'Critique'],
    ['3', 'Tests absents — dossier tests/ vide malgré les mentions dans le README', 'Haute'],
    ['4', 'Dashboard sans code source — seulement un PNG sans script générateur', 'Haute'],
    ['5', '.gitignore vide — données runtime et métadonnées versionnées', 'Moyenne'],
    ['6', 'Pas de validation de schéma — Pandera dans les dépendances mais inutilisé', 'Moyenne'],
]
story.append(make_table(issues_header, issues_rows, col_widths=[20, 240, 50]))
story.append(spacer(6))
story.append(body(
    "<b>Note</b> : Le montage Docker Compose (../dags:/opt/airflow/dags) était déjà correct "
    "— le dossier racine dags/ est bien accessible depuis Airflow. Aucune correction nécessaire."
))

# === 7. CORRECTIONS ===
story.append(section("7. Corrections appliquées"))
story.append(spacer(4))

fix_header = ['#', 'Fichier', 'Correction']
fix_rows = [
    ['1', 'scripts/streaming_ndox_sn.py',
     'Topic changé : ndox_alerts → ndox_pression_raw. Ajout ratio pression, criticité, anonymisation SHA-256.'],
    ['2', 'scripts/kafka_to_hbase.py',
     'Réécrit avec happybase.Connection() et table.put(). Suppression de subprocess / docker exec.'],
    ['3', 'tests/test_schemas.py (nouveau)',
     'Validation Pandera : schémas pression (7 champs) et consommation (6 champs) avec types, plages, regex.'],
    ['4', 'tests/test_udfs.py (nouveau)',
     'Tests unitaires : anonymisation (déterministe, sel différent, longueur 64, unicité) + criticité (limites, négatif).'],
    ['5', 'dashboard/dashboard_ndox.py (nouveau)',
     'Barplot scores priorité + tournées plus proche voisin. Génère dashboard_priorites.png.'],
    ['6', '.gitignore (nouveau)',
     'Règles pour __pycache__, nifi-data, postgres-data, metastore_db, derby.log, .env, etc.'],
    ['7', 'requirements.txt',
     'Ajout de pytest==7.4.3 pour les tests.'],
]
story.append(make_table(fix_header, fix_rows, col_widths=[20, 100, 190]))
story.append(spacer(10))

# Détail des corrections principales
story.append(subsubsection("7.1 Correction du pipeline streaming"))
story.append(body(
    "Le fichier <b>streaming_ndox_sn.py</b> lisait le topic <b>ndox_alerts</b> qui n'était "
    "produit par aucun composant. Le producteur Kafka écrit sur <b>ndox_pression_raw</b>. "
    "La correction rétablit le flux :"
))
story.append(body(
    "<i>kafka_producer_ndox_sn.py</i> → topic <b>ndox_pression_raw</b> → "
    "<i>streaming_ndox_sn.py</i> → ratio pression + criticité + score → Parquet"
))
story.append(body(
    "De plus, le calcul de criticité (CRITIQUE &lt; 0.3, ALERTE &lt; 0.6, SURVEILLANCE &lt; 0.8, "
    "NORMAL) et l'anonymisation SHA-256 des capteurs (via NDOX_SECRET_SALT) ont été intégrés "
    "directement dans le streaming."
))

story.append(subsubsection("7.2 Réécriture du consumer Kafka → HBase"))
story.append(body(
    "L'ancien <b>kafka_to_hbase.py</b> utilisait <i>subprocess.run(['docker', 'exec', ...])</i> "
    "pour lancer 'hbase shell' à chaque message. Cette approche est fragile, non scalable "
    "et problématique en production. La correction utilise <b>happybase</b> (client HBase natif Python) :"
))
story.append(spacer(4))
story.append(code(
    "conn = happybase.Connection('localhost', port=9090, timeout=10000)<br/>"
    "table = conn.table(b'ndox:alertes_rupture')<br/>"
    "table.put(zone.encode(), {<br/>"
    "    b'meta:pression': str(pression).encode(),<br/>"
    "    b'meta:statut': statut.encode(),<br/>"
    "    b'meta:ratio': f'{ratio:.2f}'.encode(),<br/>"
    "    b'meta:ts': timestamp.encode(),<br/>"
    "})"
))

story.append(subsubsection("7.3 Tests unitaires"))
story.append(body(
    "Le dossier <b>tests/</b> était vide. Deux fichiers de tests ont été créés :"
))
story.append(body(
    "<b>tests/test_schemas.py</b> — validation de schéma avec Pandera. Définit deux "
    "DataFrameSchema (pression et consommation) qui vérifient : types, plages de valeurs, "
    "zones autorisées, format regex des timestamps, motif des IDs capteurs/compteurs. "
    "5 tests : validation positive, zone invalide, consommation valide, heure invalide."
))
story.append(body(
    "<b>tests/test_udfs.py</b> — 11 tests unitaires purs (sans dépendance Spark). "
    "Couvrent : l'anonymisation SHA-256 (déterministe, sel différent produit hash différent, "
    "longueur 64, IDs différents produisent hash différents) et le calcul de criticité "
    "(4 niveaux, limites exactes 0.3/0.6/0.8, valeur zéro, valeur négative)."
))

story.append(subsubsection("7.4 Dashboard"))
story.append(body(
    "Le dossier <b>dashboard/</b> ne contenait qu'un PNG. Le script <b>dashboard_ndox.py</b> a été créé : "
    "génère un barplot horizontal des scores de priorité (couleur par niveau : "
    "rouge CRITIQUE, orange ALERTE, bleu SURVEILLANCE, vert NORMAL) et une optimisation "
    "de tournées par plus proche voisin sur les 3 zones les plus critiques."
))

# === 8. USAGE ===
story.append(section("8. Guide d'utilisation"))
story.append(subsection("8.1 Installation"))
story.append(code(
    "git clone &lt;url-du-repo&gt;<br/>"
    "cd ndox-sn<br/>"
    "chmod +x setup.sh<br/>"
    "./setup.sh"
))
story.append(body(
    "Le script <b>setup.sh</b> : (1) crée les répertoires, (2) lance Docker Compose, "
    "(3) attend HBase, (4) crée les tables HBase, (5) lance le simulateur Kafka."
))

story.append(subsection("8.2 Interfaces web"))
int_header = ['Service', 'URL']
int_rows = [
    ['Spark Master', 'http://localhost:8081'],
    ['HBase Master', 'http://localhost:16010'],
    ['Airflow', 'http://localhost:8082'],
]
story.append(make_table(int_header, int_rows, col_widths=[100, 200]))

story.append(subsection("8.3 Pipeline manuel"))
story.append(body("1. Lancer le streaming Spark :"))
story.append(code("spark-submit --master local[2] scripts/streaming_ndox_sn.py"))
story.append(body("2. Initialiser Hive :"))
story.append(code("docker exec -i docker-hive-metastore-1 hive -f /opt/hive/hive_setup.sql"))
story.append(body("3. Activer le DAG Airflow dans l'interface (port 8082)"))
story.append(body("4. Lancer le dashboard :"))
story.append(code("python dashboard/dashboard_ndox.py"))

# === 9. TESTS ===
story.append(section("9. Tests"))
story.append(body("Exécution des tests unitaires :"))
story.append(code("pip install -r requirements.txt ; pytest tests/ -v"))
story.append(body(
    "Les tests couvrent : validation des schémas de données (Pandera), "
    "anonymisation SHA-256, et calcul de la criticité. "
    "Aucune dépendance Spark ni conteneur Docker n'est requise."
))
story.append(spacer(4))

tests_header = ['Test', 'Description', 'Type']
tests_rows = [
    ['test_schema_pression_valide', 'Message pression valide passe le schéma Pandera', 'Validation'],
    ['test_schema_pression_zone_invalide', 'Zone inconnue rejetée par le schéma', 'Validation'],
    ['test_schema_consommation_valide', 'Message consommation valide passe le schéma', 'Validation'],
    ['test_schema_consommation_heure_invalide', 'Heure &gt; 23 rejetée', 'Validation'],
    ['test_anonymisation_deterministe', 'Même capteur + sel = même hash', 'Unitaire'],
    ['test_anonymisation_salt_different', 'Sel différent = hash différent', 'Unitaire'],
    ['test_anonymisation_longueur', 'SHA-256 = 64 caractères hex', 'Unitaire'],
    ['test_anonymisation_ids_differents', 'IDs différents = hash différents', 'Unitaire'],
    ['test_criticite_* (6 tests)', 'Limites : 0.3, 0.6, 0.8, négatif, zéro', 'Unitaire'],
]
story.append(make_table(tests_header, tests_rows, col_widths=[100, 130, 70]))

# === 10. CONCLUSION ===
story.append(section("10. Conclusion"))
story.append(body(
    "Le projet Ndocx-SN met en œuvre une architecture Data-Driven complète pour "
    "la prédiction des ruptures du réseau d'eau au Sénégal. La vérification du code "
    "a permis d'identifier et corriger 6 problèmes dont 2 critiques (pipeline "
    "interrompu, utilisation de subprocess) et 2 de haute sévérité (tests manquants, "
    "dashboard sans source)."
))
story.append(body(
    "Après corrections, le pipeline est fonctionnel : simulateur Kafka → Spark Streaming "
    "(criticité + anonymisation) → HBase (temps réel) + Hive (historique) → Airflow "
    "(orchestration ML) → Dashboard (visualisation). Les tests unitaires et de validation "
    "garantissent la qualité des données et le bon fonctionnement des UDFs."
))
story.append(spacer(10))
story.append(hr())
story.append(spacer(6))
story.append(Paragraph(
    f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} — "
    "Projet Ndocx-SN v1.0",
    styles['NDFooter']
))

doc.build(story)
print(f"PDF généré : {OUTPUT}")