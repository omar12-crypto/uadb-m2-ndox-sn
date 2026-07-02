import pandas as pd
import re

ZONES_VALIDES = {
    'DAKAR_NORD', 'DAKAR_SUD', 'PIKINE', 'THIES',
    'SAINT_LOUIS', 'KAOLACK', 'ZIGUINCHOR'
}
STATUTS_VALIDES = {'NORMAL', 'PRESSION_BASSE', 'RUPTURE_IMMINENTE'}
TIMESTAMP_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')


def valider_pression(df):
    assert (df['capteur_id'].str.match(r'^CPT_.+')).all(), "capteur_id doit commencer par CPT_"
    assert df['zone'].isin(ZONES_VALIDES).all(), f"zone doit être dans {ZONES_VALIDES}"
    assert df['pression_bars'].between(0.0, 6.0).all(), "pression_bars doit être entre 0 et 6"
    assert df['pression_nominale'].between(2.5, 5.0).all(), "pression_nominale doit être entre 2.5 et 5"
    assert (df['debit_m3h'] >= 0).all(), "debit_m3h doit être >= 0"
    assert df['statut_capteur'].isin(STATUTS_VALIDES).all(), f"statut_capteur doit être dans {STATUTS_VALIDES}"
    assert df['age_canalisation_ans'].between(0.0, 100.0).all(), "age_canalisation_ans doit être entre 0 et 100"
    assert df['timestamp'].apply(lambda x: bool(TIMESTAMP_RE.match(str(x)))).all(), "timestamp doit être au format ISO"
    return True


def valider_consommation(df):
    assert (df['compteur_id'].str.match(r'^CMT_.+')).all(), "compteur_id doit commencer par CMT_"
    assert df['zone'].isin(ZONES_VALIDES).all(), f"zone doit être dans {ZONES_VALIDES}"
    assert (df['consommation_m3'] >= 0).all(), "consommation_m3 doit être >= 0"
    assert df['heure'].between(0, 23).all(), "heure doit être entre 0 et 23"
    assert df['timestamp'].apply(lambda x: bool(TIMESTAMP_RE.match(str(x)))).all(), "timestamp doit être au format ISO"
    return True


def test_schema_pression_valide():
    df = pd.DataFrame([{
        'capteur_id': 'CPT_DAKAR_NORD_a1b2c3d4',
        'zone': 'DAKAR_NORD',
        'pression_bars': 3.8,
        'pression_nominale': 4.5,
        'debit_m3h': 320.5,
        'statut_capteur': 'NORMAL',
        'age_canalisation_ans': 15.0,
        'timestamp': '2026-06-23T10:00:00Z',
    }])
    assert valider_pression(df)


def test_schema_pression_zone_invalide():
    import pytest
    df = pd.DataFrame([{
        'capteur_id': 'CPT_INVALIDE_abc',
        'zone': 'ZONE_INCONNUE',
        'pression_bars': 3.8,
        'pression_nominale': 4.5,
        'debit_m3h': 320.5,
        'statut_capteur': 'NORMAL',
        'age_canalisation_ans': 15.0,
        'timestamp': '2026-06-23T10:00:00Z',
    }])
    with pytest.raises(AssertionError):
        valider_pression(df)


def test_schema_consommation_valide():
    df = pd.DataFrame([{
        'compteur_id': 'CMT_abcdef1234',
        'adresse_client': 'Rue 123 DAKAR_NORD',
        'zone': 'DAKAR_NORD',
        'consommation_m3': 2.5,
        'heure': 8,
        'timestamp': '2026-06-23T10:00:00Z',
    }])
    assert valider_consommation(df)


def test_schema_consommation_heure_invalide():
    import pytest
    df = pd.DataFrame([{
        'compteur_id': 'CMT_abcdef1234',
        'adresse_client': 'Rue 123 DAKAR_NORD',
        'zone': 'DAKAR_NORD',
        'consommation_m3': 2.5,
        'heure': 25,
        'timestamp': '2026-06-23T10:00:00Z',
    }])
    with pytest.raises(AssertionError):
        valider_consommation(df)


def test_pression_capteur_id_invalide():
    import pytest
    df = pd.DataFrame([{
        'capteur_id': 'INVALIDE_123',
        'zone': 'DAKAR_NORD',
        'pression_bars': 3.8,
        'pression_nominale': 4.5,
        'debit_m3h': 320.5,
        'statut_capteur': 'NORMAL',
        'age_canalisation_ans': 15.0,
        'timestamp': '2026-06-23T10:00:00Z',
    }])
    with pytest.raises(AssertionError):
        valider_pression(df)


def test_pression_statut_invalide():
    import pytest
    df = pd.DataFrame([{
        'capteur_id': 'CPT_DAKAR_001',
        'zone': 'DAKAR_NORD',
        'pression_bars': 3.8,
        'pression_nominale': 4.5,
        'debit_m3h': 320.5,
        'statut_capteur': 'STATUT_FAKE',
        'age_canalisation_ans': 15.0,
        'timestamp': '2026-06-23T10:00:00Z',
    }])
    with pytest.raises(AssertionError):
        valider_pression(df)


def test_pression_timestamp_invalide():
    import pytest
    df = pd.DataFrame([{
        'capteur_id': 'CPT_DAKAR_001',
        'zone': 'DAKAR_NORD',
        'pression_bars': 3.8,
        'pression_nominale': 4.5,
        'debit_m3h': 320.5,
        'statut_capteur': 'NORMAL',
        'age_canalisation_ans': 15.0,
        'timestamp': 'not-a-date',
    }])
    with pytest.raises(AssertionError):
        valider_pression(df)