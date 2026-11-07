import pandas as pd

multi_columns = [
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
        "Prct retard pour cause prise en compte voyageurs (affluence, gestions PSH, correspondances)",
    ),
]


region_mapping = {
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

station_to_airport = {
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
    "PARIS VAUGIRARD": "PARIS-ORLY / PARIS-CHARLES-DE-GAULLE",
    # Gares internationales majeures
    "FRANCFORT": "AÉROPORT DE FRANCFORT",
    "ZURICH": "AÉROPORT DE ZURICH",
    "GENEVE": "AÉROPORT DE GENÈVE",
    "BARCELONA": "AÉROPORT DE BARCELONE-EL PRAT",
}


def preprocessing(df, columns_order=multi_columns, columns_drop_idx=(7, 11, 17)):
    df.columns = pd.MultiIndex.from_tuples(columns_order)
    # datetime format
    df[("Contexte", "Date")] = pd.to_datetime(
        df[("Contexte", "Date")], format="%Y-%m"
    ).dt.to_period("M")
    # category format
    df[("Contexte", "Service")] = df[("Contexte", "Service")].astype("category")
    df[("Contexte", "Gare de départ")] = df[("Contexte", "Gare de départ")].astype(
        "category"
    )
    df[("Contexte", "Gare d'arrivée")] = df[("Contexte", "Gare d'arrivée")].astype(
        "category"
    )
    # drop empty/useless columns
    df.drop(columns=[columns_order[i] for i in columns_drop_idx], inplace=True)


def enrichment(df):
    # Création d'une nouvelle colonne "Saison" dans le DataFrame df
    index = df.columns.get_loc(("Contexte", "Date"))
    if not ("Contexte", "Saison") in df.columns:
        print('ajout de la colonne "Saison"')
        df.insert(
            loc=index + 1,
            column=("Contexte", "Saison"),
            value=df[("Contexte", "Date")].dt.month,
        )
        df[("Contexte", "Saison")] = pd.Categorical(
            df[("Contexte", "Saison")], ordered=True
        )

    # Création d'une nouvelle colonne "Région de départ" dans le DataFrame df
    index = df.columns.get_loc(("Contexte", "Gare d'arrivée"))
    if not ("Contexte", "Région de départ") in df.columns:
        print('ajout de la colonne "Région de départ"')
        df.insert(
            loc=index + 1,
            column=("Contexte", "Région de départ"),
            value=df[("Contexte", "Gare de départ")].map(region_mapping),
        )
        df[("Contexte", "Région de départ")] = df[
            ("Contexte", "Région de départ")
        ].astype("category")

    # Création d'une nouvelle colonne "Région d'arrivée" dans le DataFrame df
    if not ("Contexte", "Région d'arrivée") in df.columns:
        print('ajout de la colonne "Région d\'arrivée"')
        df.insert(
            loc=index + 2,
            column=("Contexte", "Région d'arrivée"),
            value=df[("Contexte", "Gare d'arrivée")].map(region_mapping),
        )
        df[("Contexte", "Région d'arrivée")] = df[
            ("Contexte", "Région d'arrivée")
        ].astype("category")

    # Création d'une nouvelle colonne "Correspondance avec aéroport" dans le DataFrame
    index = df.columns.get_loc(("Contexte", "Région d'arrivée"))
    station_with_airport = list(station_to_airport.keys())
    if not ("Contexte", "Correspondance avec aéroport") in df.columns:
        print('ajout de la colonne "Correspondance avec aéroport"')
        df.insert(
            loc=index + 1,
            column=("Contexte", "Correspondance avec aéroport"),
            value=df[("Contexte", "Gare d'arrivée")].isin(station_with_airport),
        )

    # Création d'une nouvelle colonne "Aéroport" dans le DataFrame
    index = df.columns.get_loc(("Contexte", "Correspondance avec aéroport"))
    if not ("Contexte", "Aéroport") in df.columns:
        print('Ajout de la colonne "Aéroport"')
        airport_values = df.apply(
            lambda row: (
                station_to_airport.get(row[("Contexte", "Gare d'arrivée")])
                if row[("Contexte", "Correspondance avec aéroport")]
                else None
            ),
            axis=1,
        )
        df.insert(loc=index + 1, column=("Contexte", "Aéroport"), value=airport_values)


def airport_seasonality(df):
    df_airport = df[df[("Contexte", "Correspondance avec aéroport")] == True]
    df_airport_seasonality = (
        df_airport.groupby(
            [
                ("Contexte", "Saison"),
                ("Contexte", "Gare de départ"),
                ("Contexte", "Gare d'arrivée"),
                ("Contexte", "Aéroport"),
            ]
        )
        .apply(
            lambda df_groupby: pd.Series(
                {
                    "Volume total des circulations prévues": df_groupby[
                        ("Volumes & Annulations", "Nombre de circulations prévues")
                    ].sum(),
                    "Volume total de trains annulés": df_groupby[
                        ("Volumes & Annulations", "Nombre de trains annulés")
                    ].sum(),
                    "Volume total de trains en retard à l'arrivée": df_groupby[
                        ("Arrivée (retard)", "Nombre de trains en retard à l'arrivée")
                    ].sum(),
                    "Retard moyen des trains à l'arrivée": (
                        (
                            df_groupby[
                                (
                                    "Arrivée (retard)",
                                    "Retard moyen des trains en retard à l'arrivée",
                                )
                            ]
                            * df_groupby[
                                (
                                    "Arrivée (retard)",
                                    "Nombre de trains en retard à l'arrivée",
                                )
                            ]
                        ).sum()
                        / df_groupby[
                            (
                                "Arrivée (retard)",
                                "Nombre de trains en retard à l'arrivée",
                            )
                        ].sum()
                        if df_groupby[
                            (
                                "Arrivée (retard)",
                                "Nombre de trains en retard à l'arrivée",
                            )
                        ].sum()
                        != 0
                        else 0
                    ),
                    "Volume total de trains en retard > 15 min": df_groupby[
                        ("Arrivée (retard)", "Nombre trains en retard > 15min")
                    ].sum(),
                    "Volume total de trains en retard > 30 min": df_groupby[
                        ("Arrivée (retard)", "Nombre trains en retard > 30min")
                    ].sum(),
                    "Volume total de trains en retard > 60 min": df_groupby[
                        ("Arrivée (retard)", "Nombre trains en retard > 60min")
                    ].sum(),
                }
            )
        )
        .reset_index()
    )
    return df_airport_seasonality
