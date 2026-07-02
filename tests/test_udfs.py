import hashlib


def anonymiser_capteur(capteur_id, salt):
    return hashlib.sha256(f'{salt}{capteur_id}'.encode()).hexdigest()


def calculer_criticite(ratio_pression):
    if ratio_pression < 0.3:
        return 'CRITIQUE'
    if ratio_pression < 0.6:
        return 'ALERTE'
    if ratio_pression < 0.8:
        return 'SURVEILLANCE'
    return 'NORMAL'


def test_anonymisation_deterministe():
    result1 = anonymiser_capteur('CPT_DAKAR_001', 'salt_test')
    result2 = anonymiser_capteur('CPT_DAKAR_001', 'salt_test')
    assert result1 == result2, "L'anonymisation doit être déterministe"


def test_anonymisation_salt_different():
    r1 = anonymiser_capteur('CPT_DAKAR_001', 'salt_a')
    r2 = anonymiser_capteur('CPT_DAKAR_001', 'salt_b')
    assert r1 != r2, "Des sels différents doivent produire des hash différents"


def test_anonymisation_longueur():
    result = anonymiser_capteur('CPT_DAKAR_001', 'salt_test')
    assert len(result) == 64, "SHA-256 doit produire 64 caractères hexadécimaux"


def test_anonymisation_ids_differents():
    r1 = anonymiser_capteur('CPT_ZONE_A', 'salt')
    r2 = anonymiser_capteur('CPT_ZONE_B', 'salt')
    assert r1 != r2, "Deux IDs différents doivent produire des hash différents"


def test_criticite_critique():
    assert calculer_criticite(0.1) == 'CRITIQUE'
    assert calculer_criticite(0.29) == 'CRITIQUE'


def test_criticite_alerte():
    assert calculer_criticite(0.3) == 'ALERTE'
    assert calculer_criticite(0.59) == 'ALERTE'


def test_criticite_surveillance():
    assert calculer_criticite(0.6) == 'SURVEILLANCE'
    assert calculer_criticite(0.79) == 'SURVEILLANCE'


def test_criticite_normal():
    assert calculer_criticite(0.8) == 'NORMAL'
    assert calculer_criticite(1.0) == 'NORMAL'
    assert calculer_criticite(2.0) == 'NORMAL'


def test_criticite_limites():
    assert calculer_criticite(0.3) == 'ALERTE'
    assert calculer_criticite(0.6) == 'SURVEILLANCE'
    assert calculer_criticite(0.8) == 'NORMAL'


def test_criticite_zero():
    assert calculer_criticite(0.0) == 'CRITIQUE'


def test_criticite_negatif():
    assert calculer_criticite(-0.5) == 'CRITIQUE'