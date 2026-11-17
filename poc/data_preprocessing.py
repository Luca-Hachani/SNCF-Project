import pandas as pd
from itertools import permutations
from settings import TRIP_MULTI_COLUMNS, REGION_MAPPING, STATION_TO_AIRPORT


def preprocessing(df, columns_order=TRIP_MULTI_COLUMNS, columns_drop_idx=(7, 11, 17)):
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
            value=df[("Contexte", "Gare de départ")].map(REGION_MAPPING),
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
            value=df[("Contexte", "Gare d'arrivée")].map(REGION_MAPPING),
        )
        df[("Contexte", "Région d'arrivée")] = df[
            ("Contexte", "Région d'arrivée")
        ].astype("category")

    # Création d'une nouvelle colonne "Correspondance avec aéroport" dans le DataFrame
    index = df.columns.get_loc(("Contexte", "Région d'arrivée"))
    station_with_airport = list(STATION_TO_AIRPORT.keys())
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
                STATION_TO_AIRPORT.get(row[("Contexte", "Gare d'arrivée")])
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


def unique_links(df):
    # Extraction de toutes les liaisons uniques (Gare de départ -> Gare d'arrivée)
    unique_links = (
        df[[("Contexte", "Gare de départ"), ("Contexte", "Gare d'arrivée"), ("Contexte", "Durée moyenne du trajet")]]
        .drop_duplicates()
        .reset_index(drop=True)
        )
    unique_links.columns = ["Gare de départ", "Gare d'arrivée", "Durée moyenne du trajet"]

    # Extraction directe et unique des gares d'Île-de-France
    idf_stations = (
        df[df[("Contexte", "Région de départ")] == "Île-de-France"][("Contexte", "Gare de départ")]
        .drop_duplicates()
        .sort_values()
        .tolist()
        )

    # Génération de toutes les liaisons intrarégionale d'île de France 
    idf_pairs = list(permutations(idf_stations, 2))
    idf_links = pd.DataFrame(
        idf_pairs, 
        columns=["Gare de départ", "Gare d'arrivée"]
        )
    idf_links["Durée moyenne du trajet"] = 30

    # Génération des liaisons TOURCOING <-> LILLE
    north_links = pd.DataFrame(
        [("TOURCOING", "LILLE"), ("LILLE", "TOURCOING")], 
        columns=["Gare de départ", "Gare d'arrivée"]
        )
    north_links["Durée moyenne du trajet"] = 30

    # Fusion de idf_links avec north_links
    new_links = (
        pd.concat([idf_links, north_links], ignore_index=True)
        .reset_index(drop=True)
        )

    # Fusion avec unique_links et nettoyage des doublons
    unique_links = (
        pd.concat([unique_links, new_links], ignore_index=True)
        .drop_duplicates(subset=["Gare de départ", "Gare d'arrivée"])
        .reset_index(drop=True)
        )
    
    return unique_links
