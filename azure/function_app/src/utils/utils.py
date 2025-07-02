# azure\function_app\src\utils\utils.py

import os
import pandas as pd

def save_df(df: pd.DataFrame, path: str, format: str = "parquet") -> None:
    """
    Sauvegarde un DataFrame au format Parquet ou Pickle.

    Args:
        df (pd.DataFrame): DataFrame à sauvegarder.
        path (str): Chemin complet du fichier de sortie (incluant le nom et l’extension).
        format (str): Format de sortie : 'parquet' pour Parquet ou 'pkl' pour Pickle.
    """
    # Création du dossier si nécessaire (evite les erreurs si le répertoire n'existe pas)
    os.makedirs(os.path.dirname(path), exist_ok = True)

    if format == "parquet":
        # Sauvegarde au format Parquet avec compression Snappy par défaut.
        # Le format Parquet est optimisé pour les lectures/écritures rapides et les grandes volumétries.
        # Documentation : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html
        df.to_parquet(path, index = False, compression = "snappy")
    elif format == "pkl":
        # Sauvegarde au format Pickle (.pkl). Utile pour des chargements plus rapides en Python pur.
        # Documentation : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_pickle.html
        df.to_pickle(path)
    else:
        # Si l’utilisateur demande un format autre que 'parquet' ou 'pkl', on lève une erreur explicite.
        raise ValueError("Format non supporté. Utiliser 'parquet' ou 'pkl'.")


def load_df(path: str) -> pd.DataFrame:
    """
    Charge un DataFrame depuis un fichier .parquet ou .pkl.

    Args:
        path (str): Chemin complet du fichier à charger (doit se terminer par .parquet ou .pkl).

    Returns:
        pd.DataFrame: DataFrame chargé depuis le fichier.

    Raises:
        ValueError: Si l’extension du fichier n’est ni .parquet ni .pkl.
    """
    # On détecte l’extension du fichier pour utiliser la méthode adéquate de pandas.
    if path.endswith(".parquet"):
        # Lecture du fichier Parquet (nécessite pyarrow ou fastparquet).
        # Documentation : https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html
        return pd.read_parquet(path)
    elif path.endswith(".pkl"):
        # Lecture du fichier Pickle
        # Documentation : https://pandas.pydata.org/docs/reference/api/pandas.read_pickle.html
        return pd.read_pickle(path)
    else:
        # On précise le format attendu si ce n’est pas un fichier .parquet ou .pkl.
        raise ValueError("Extension non supportée : utiliser .parquet ou .pkl.")
