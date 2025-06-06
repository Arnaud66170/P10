# src/utils/utils.py

import pandas as pd
import os

def save_df(df: pd.DataFrame, path: str, format: str = "parquet") -> None:
    """
    Sauvegarde un DataFrame au format parquet ou pickle.

    Args:
        df (pd.DataFrame): DataFrame à sauvegarder
        path (str): Chemin du fichier de sortie
        format (str): Format de sortie : 'parquet' ou 'pkl'
    """
    os.makedirs(os.path.dirname(path), exist_ok = True)

    if format == "parquet":
        df.to_parquet(path, index = False)
    elif format == "pkl":
        df.to_pickle(path)
    else:
        raise ValueError("Format non supporté. Utiliser 'parquet' ou 'pkl'.")


def load_df(path: str) -> pd.DataFrame:
    """
    Charge un DataFrame depuis un fichier .parquet ou .pkl.

    Args:
        path (str): Chemin du fichier

    Returns:
        pd.DataFrame: DataFrame chargé
    """
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    elif path.endswith(".pkl"):
        return pd.read_pickle(path)
    else:
        raise ValueError("Extension non supportée : utiliser .parquet ou .pkl")
