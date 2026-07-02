import happybase, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HBaseSetup')

def create_ndox_sn_tables():
    conn = happybase.Connection('localhost', port=9090, timeout=20000)
    conn.open()
    
    # Créer le namespace 'ndox' s'il n'existe pas
    try:
        conn.create_namespace('ndox')
        logger.info("Namespace 'ndox' créé ✓")
    except Exception as e:
        # Si le namespace existe déjà, on ignore l'erreur
        if 'NamespaceExistsException' in str(e):
            logger.info("Namespace 'ndox' existe déjà")
        else:
            logger.warning(f"Erreur lors de la création du namespace: {e}")
    
    tables = {
        b'ndox:capteurs_temps_reel': {'meta': {'max_versions': 1}},
        b'ndox:alertes_rupture': {'meta': {'max_versions': 1}},
        b'ndox:tournees_citernes': {'meta': {'max_versions': 1}},
    }
    existantes = [t.decode() for t in conn.tables()]
    for name, fam in tables.items():
        name_str = name.decode()
        if name_str not in existantes:
            conn.create_table(name, fam)
            logger.info(f"Table {name_str} créée ✓")
        else:
            logger.info(f"Table {name_str} existe déjà")
    conn.close()

if __name__ == '__main__':
    create_ndox_sn_tables()
