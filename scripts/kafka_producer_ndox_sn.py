from kafka import KafkaProducer
import json, random, time, uuid
from datetime import datetime
import numpy as np

random.seed(42)
np.random.seed(42)

ZONES = ['DAKAR_NORD', 'DAKAR_SUD', 'PIKINE', 'THIES', 'SAINT_LOUIS', 'KAOLACK', 'ZIGUINCHOR']
PRESSION_NOMINALE = {
    'DAKAR_NORD': 4.5, 'DAKAR_SUD': 4.2, 'PIKINE': 3.8,
    'THIES': 3.5, 'SAINT_LOUIS': 3.2, 'KAOLACK': 3.0, 'ZIGUINCHOR': 2.8
}
FRAGILITE_RESEAU = {
    'DAKAR_NORD': 0.05, 'DAKAR_SUD': 0.08, 'PIKINE': 0.20,
    'THIES': 0.15, 'SAINT_LOUIS': 0.18, 'KAOLACK': 0.22, 'ZIGUINCHOR': 0.25
}

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode()
)

def gen_pression(zone):
    p_nom = PRESSION_NOMINALE[zone]
    frag = FRAGILITE_RESEAU[zone]
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
        'capteur_id': f'CPT_{zone}_{uuid.uuid4().hex[:8]}',
        'zone': zone,
        'pression_bars': pression,
        'pression_nominale': p_nom,
        'debit_m3h': round(random.uniform(50, 500) * (pression / p_nom), 1),
        'statut_capteur': statut,
        'age_canalisation_ans': round(random.uniform(5, 45), 1),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

def gen_conso(zone):
    h = datetime.utcnow().hour
    facteur = 1.5 if (6 <= h <= 8 or 18 <= h <= 20) else 0.8
    return {
        'compteur_id': f'CMT_{uuid.uuid4().hex[:10]}',
        'adresse_client': f'Rue {random.randint(1,500)} {zone}',
        'zone': zone,
        'consommation_m3': round(random.uniform(0.5, 5.0) * facteur, 2),
        'heure': h,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

if __name__ == '__main__':
    print("Simulateur Ndocx-SN démarré... (Kafka sur localhost:9092)")
    while True:
        for zone in ZONES:
            producer.send('ndox_pression_raw', gen_pression(zone))
            producer.send('ndox_conso_raw', gen_conso(zone))
        producer.flush()
        time.sleep(5)