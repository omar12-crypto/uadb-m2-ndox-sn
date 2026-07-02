FROM apache/airflow:2.7.3

# Passer en root pour installer les dépendances système
USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libsasl2-dev \
        python3-dev \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Revenir à l'utilisateur airflow (recommandé pour pip)
USER airflow

# Copier le fichier des dépendances Python
COPY requirements-airflow.txt /requirements.txt

# Installer les packages Python (nécessite la compilation, mais les outils sont présents)
RUN pip install --no-cache-dir -r /requirements.txt
