# PATH TO DATASETS
DATASET_RE_MEN_TGV_PATH = "data/regularite-mensuelle-tgv-aqst.csv"
DATASET_STATIONS_PATH = "data/liste-des-gares.csv"
DATASET_COMMUNES_PATH = "data/liste-communes-France.csv"
DATASET_RELIABLE_PATH = "data/data_reliable.csv"


TRIP_MULTI_COLUMNS = [
    # Contexte et Identification de la Liaison
    ("Contexte", "Date"),
    ("Contexte", "Service"),
    ("Contexte", "Gare de départ"),
    ("Contexte", "Gare d'arrivée"),
    ("Contexte", "Durée moyenne du trajet"),
    # Volumes et Annulations
    ("Volumes & Annulations", "Nombre de circulations prévues"),
    ("Volumes & Annulations", "Nombre de trains annulés"),
    ("Volumes & Annulations", "Commentaire annulations"),
    # Départ (retard)
    ("Départ (retard)", "Nombre de trains en retard au départ"),
    ("Départ (retard)", "Retard moyen des trains en retard au départ"),
    ("Départ (retard)", "Retard moyen de tous les trains au départ"),
    ("Départ (retard)", "Commentaire retards au départ"),
    # Arrivée (retard)
    ("Arrivée (retard)", "Nombre de trains en retard à l'arrivée"),
    ("Arrivée (retard)", "Retard moyen des trains en retard à l'arrivée"),
    ("Arrivée (retard)", "Retard moyen de tous les trains à l'arrivée"),
    ("Arrivée (retard)", "Commentaire retards à l'arrivée"),
    ("Arrivée (retard)", "Nombre trains en retard > 15min"),
    (
        "Arrivée (retard)",
        "Retard moyen trains en retard > 15 (si liaison concurrencée par vol)",
    ),
    ("Arrivée (retard)", "Nombre trains en retard > 30min"),
    ("Arrivée (retard)", "Nombre trains en retard > 60min"),
    # Causes en % (Retard)
    ("Causes en % (Retard)", "Prct retard pour causes externes"),
    ("Causes en % (Retard)", "Prct retard pour cause infrastructure"),
    ("Causes en % (Retard)", "Prct retard pour cause gestion trafic"),
    ("Causes en % (Retard)", "Prct retard pour cause matériel roulant"),
    (
        "Causes en % (Retard)",
        "Prct retard pour cause gestion en gare et réutilisation de matériel",
    ),
    (
        "Causes en % (Retard)",
        (
            "Prct retard pour cause prise en compte voyageurs "
            "(affluence, gestions PSH, correspondances)"
        ),
    ),
]


REGION_MAPPING = {
    "AIX EN PROVENCE TGV": "Provence-Alpes-Côte d'Azur",
    "ANGERS SAINT LAUD": "Pays de la Loire",
    "ANGOULEME": "Nouvelle-Aquitaine",
    "ANNECY": "Auvergne-Rhône-Alpes",
    "ARRAS": "Hauts-de-France",
    "AVIGNON TGV": "Provence-Alpes-Côte d'Azur",
    "BARCELONA": "International (Espagne)",
    "BELLEGARDE (AIN)": "Auvergne-Rhône-Alpes",
    "BESANCON FRANCHE COMTE TGV": "Bourgogne-Franche-Comté",
    "BORDEAUX ST JEAN": "Nouvelle-Aquitaine",
    "BREST": "Bretagne",
    "CHAMBERY CHALLES LES EAUX": "Auvergne-Rhône-Alpes",
    "DIJON VILLE": "Bourgogne-Franche-Comté",
    "DOUAI": "Hauts-de-France",
    "DUNKERQUE": "Hauts-de-France",
    "FRANCFORT": "International (Allemagne)",
    "GENEVE": "International (Suisse)",
    "GRENOBLE": "Auvergne-Rhône-Alpes",
    "ITALIE": "International (Italie)",
    "LA ROCHELLE VILLE": "Nouvelle-Aquitaine",
    "LAUSANNE": "International (Suisse)",
    "LAVAL": "Pays de la Loire",
    "LE CREUSOT MONTCEAU MONTCHANIN": "Bourgogne-Franche-Comté",
    "LE MANS": "Pays de la Loire",
    "LILLE": "Hauts-de-France",
    "LYON PART DIEU": "Auvergne-Rhône-Alpes",
    "MACON LOCHE": "Bourgogne-Franche-Comté",
    "MADRID": "International (Espagne)",
    "MARNE LA VALLEE": "Île-de-France",
    "MARSEILLE ST CHARLES": "Provence-Alpes-Côte d'Azur",
    "METZ": "Grand Est",
    "MONTPELLIER": "Occitanie",
    "MULHOUSE VILLE": "Grand Est",
    "NANCY": "Grand Est",
    "NANTES": "Pays de la Loire",
    "NICE VILLE": "Provence-Alpes-Côte d'Azur",
    "NIMES": "Occitanie",
    "PARIS EST": "Île-de-France",
    "PARIS LYON": "Île-de-France",
    "PARIS MONTPARNASSE": "Île-de-France",
    "PARIS NORD": "Île-de-France",
    "PARIS VAUGIRARD": "Île-de-France",
    "PERPIGNAN": "Occitanie",
    "POITIERS": "Nouvelle-Aquitaine",
    "QUIMPER": "Bretagne",
    "REIMS": "Grand Est",
    "RENNES": "Bretagne",
    "SAINT ETIENNE CHATEAUCREUX": "Auvergne-Rhône-Alpes",
    "ST MALO": "Bretagne",
    "ST PIERRE DES CORPS": "Centre-Val de Loire",
    "STRASBOURG": "Grand Est",
    "STUTTGART": "International (Allemagne)",
    "TOULON": "Provence-Alpes-Côte d'Azur",
    "TOULOUSE MATABIAU": "Occitanie",
    "TOURCOING": "Hauts-de-France",
    "TOURS": "Centre-Val de Loire",
    "VALENCE ALIXAN TGV": "Auvergne-Rhône-Alpes",
    "VANNES": "Bretagne",
    "ZURICH": "International (Suisse)",
}

STATION_TO_AIRPORT = {
    # Hubs régionaux
    "MARSEILLE ST CHARLES": "MARSEILLE PROVENCE",
    "NICE VILLE": "NICE CÔTE D'AZUR",
    "LYON PART DIEU": "LYON SAINT-EXUPÉRY",
    "STRASBOURG": "STRASBOURG-ENTZHEIM",
    "NANTES": "NANTES ATLANTIQUE",
    "BORDEAUX ST JEAN": "BORDEAUX-MÉRIGNAC",
    "TOULOUSE MATABIAU": "TOULOUSE-BLAGNAC",
    "RENNES": "RENNES SAINT-JACQUES",
    "MONTPELLIER": "MONTPELLIER-MÉDITERRANÉE",
    "MULHOUSE VILLE": "EUROAIRPORT BASEL-MULHOUSE-FREIBURG",
    # Hub parisien
    "PARIS EST": "PARIS-ORLY / PARIS-CHARLES-DE-GAULLE",
    "PARIS LYON": "PARIS-ORLY / PARIS-CHARLES-DE-GAULLE",
    "PARIS MONTPARNASSE": "PARIS-ORLY / PARIS-CHARLES-DE-GAULLE",
    "PARIS NORD": "PARIS-ORLY / PARIS-CHARLES-DE-GAULLE",
    # "PARIS VAUGIRARD": "PARIS-ORLY / PARIS-CHARLES-DE-GAULLE",
    # Gares internationales majeures
    "FRANCFORT": "AÉROPORT DE FRANCFORT",
    "ZURICH": "AÉROPORT DE ZURICH",
    "GENEVE": "AÉROPORT DE GENÈVE",
    "BARCELONA": "AÉROPORT DE BARCELONE-EL PRAT",
}
