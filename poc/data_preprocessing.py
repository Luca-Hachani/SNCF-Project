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
    ("Arrivée (retard)", "Retard moyen trains en retard > 15 (si liaison concurrencée par vol)"),
    ("Arrivée (retard)", "Nombre trains en retard > 30min"),
    ("Arrivée (retard)", "Nombre trains en retard > 60min"),
    
    # Causes en % (Retard) 
    ("Causes en % (Retard)", "Prct retard pour causes externes"),
    ("Causes en % (Retard)", "Prct retard pour cause infrastructure"),
    ("Causes en % (Retard)", "Prct retard pour cause gestion trafic"),
    ("Causes en % (Retard)", "Prct retard pour cause matériel roulant"),
    ("Causes en % (Retard)", "Prct retard pour cause gestion en gare et réutilisation de matériel"),
    ("Causes en % (Retard)", "Prct retard pour cause prise en compte voyageurs (affluence, gestions PSH, correspondances)")
]


def preprocessing(df, columns_order=multi_columns, columns_drop_idx=(7, 11, 17)):
    df.columns = pd.MultiIndex.from_tuples(columns_order)
    # datetime format
    df[("Contexte", "Date")] = pd.to_datetime(df[("Contexte", "Date")], format='%Y-%m').dt.to_period('M')
    # category format
    df[("Contexte", "Service")] = df[("Contexte", "Service")].astype('category')
    df[("Contexte", "Gare de départ")] = df[("Contexte", "Gare de départ")].astype('category')
    df[("Contexte", "Gare d'arrivée")] = df[("Contexte", "Gare d'arrivée")].astype('category')
    # drop empty/useless columns
    df.drop(columns=[columns_order[i] for i in columns_drop_idx], inplace=True)