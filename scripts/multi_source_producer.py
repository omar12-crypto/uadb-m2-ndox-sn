#!/usr/bin/env python3
"""
Multi-source producer for Ndocx-SN.
Simulates 3 sources → 2 Kafka topics with GPS coordinates.

Sources:
  1. SONES  – capteurs pression réseau (topic: ndox_pression_raw)
  2. Météo  – pluviométrie par zone    (topic: ndox_pression_raw)
  3. Sen Eau – consommation résidentielle (topic: ndox_conso_raw)
"""

from kafka import KafkaProducer
import json, random, time, uuid
from datetime import datetime
import numpy as np

random.seed(42)
np.random.seed(42)

ZONES = ['DAKAR_NORD', 'DAKAR_SUD', 'PIKINE', 'THIES',
         'SAINT_LOUIS', 'KAOLACK', 'ZIGUINCHOR']

GPS = {
    'DAKAR_NORD':    {'lat': 14.73, 'lon': -17.45},
    'DAKAR_SUD':     {'lat': 14.67, 'lon': -17.43},
    'PIKINE':        {'lat': 14.75, 'lon': -17.38},
    'THIES':         {'lat': 14.79, 'lon': -16.93},
    'SAINT_LOUIS':   {'lat': 16.03, 'lon': -16.50},
    'KAOLACK':       {'lat': 14.15, 'lon': -16.08},
    'ZIGUINCHOR':    {'lat': 12.55, 'lon': -16.27},
}

PRESSION_NOMINALE = {
    'DAKAR_NORD': 4.5, 'DAKAR_SUD': 4.2, 'PIKINE': 3.8,
    'THIES': 3.5, 'SAINT_LOUIS': 3.2, 'KAOLACK': 3.0, 'ZIGUINCHOR': 2.8,
}

FRAGILITE = {
    'DAKAR_NORD': 0.05, 'DAKAR_SUD': 0.08, 'PIKINE': 0.20,
    'THIES': 0.15, 'SAINT_LOUIS': 0.18, 'KAOLACK': 0.22, 'ZIGUINCHOR': 0.25,
}

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode(),
)

# ── Source 1 : SONES (pression + GPS) ──────────────────────────

def gen_sones(zone):
    p_nom = PRESSION_NOMINALE[zone]
    frag = FRAGILITE[zone]
    if random.random() < frag:
        pression = round(max(0.1, p_nom * random.uniform(0.2, 0.5)), 2)
        statut = 'RUPTURE_IMMINENTE'
    elif random.random() < 0.1:
        pression = round(p_nom * random.uniform(0.6, 0.8), 2)
        statut = 'PRESSION_BASSE'
    else:
        pression = round(np.random.normal(p_nom, p_nom * 0.05), 2)
        statut = 'NORMAL'
    return {
        'source': 'SONES',
        'capteur_id': f'CPT_{zone}_{uuid.uuid4().hex[:8]}',
        'zone': zone,
        'pression_bars': pression,
        'pression_nominale': p_nom,
        'debit_m3h': round(random.uniform(50, 500) * (pression / p_nom), 1),
        'statut_capteur': statut,
        'age_canalisation_ans': round(random.uniform(5, 45), 1),
        'gps_lat': GPS[zone]['lat'],
        'gps_lon': GPS[zone]['lon'],
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

# ── Source 2 : Pluviométrie ───────────────────────────────────

SEASONS = {'DRY': (11, 5), 'RAINY': (6, 10)}

def gen_pluviometrie(zone):
    month = datetime.utcnow().month
    is_rainy = SEASONS['RAINY'][0] <= month <= SEASONS['RAINY'][1]
    base = random.uniform(0, 25) if is_rainy else random.uniform(0, 2)
    return {
        'source': 'METEO',
        'zone': zone,
        'pluviometrie_mm': round(base, 1),
        'humidite_pct': round(random.uniform(40, 95) if is_rainy else random.uniform(20, 60), 1),
        'gps_lat': GPS[zone]['lat'],
        'gps_lon': GPS[zone]['lon'],
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

# ── Source 3 : Consommation (Sen Eau) ─────────────────────────

def gen_conso(zone):
    h = datetime.utcnow().hour
    facteur = 1.5 if (6 <= h <= 8 or 18 <= h <= 20) else 0.8
    return {
        'source': 'SEN_EAU',
        'compteur_id': f'CMT_{uuid.uuid4().hex[:10]}',
        'zone': zone,
        'adresse_client': f'Rue {random.randint(1, 500)} {zone}',
        'consommation_m3': round(random.uniform(0.5, 5.0) * facteur, 2),
        'nombre_occupants': random.randint(1, 10),
        'gps_lat': GPS[zone]['lat'],
        'gps_lon': GPS[zone]['lon'],
        'heure': h,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

# ── Boucle principale ─────────────────────────────────────────

if __name__ == '__main__':
    print("═" * 55)
    print("  Ndocx-SN – Ingestion Multi-Sources")
    print("  Sources : SONES | MÉTÉO | SEN_EAU")
    print("  Topics  : ndox_pression_raw | ndox_conso_raw")
    print("═" * 55)
    while True:
        for zone in ZONES:
            producer.send('ndox_pression_raw', gen_sones(zone))
            producer.send('ndox_pression_raw', gen_pluviometrie(zone))
            producer.send('ndox_conso_raw', gen_conso(zone))
        producer.flush()
        t = datetime.utcnow().strftime('%H:%M:%S')
        print(f"[{t}] 7 zones × 3 sources envoyées vers Kafka")
        time.sleep(5)