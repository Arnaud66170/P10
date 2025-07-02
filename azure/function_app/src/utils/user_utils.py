# azure/function_app/src/utils/user_utils.py

import os
import json
import pandas as pd
from pathlib import Path

def extract_and_save_user_ids(df_path: str, output_path: str) -> None:
    """
    Extrait les user_id uniques d'un fichier df_light.parquet et les enregistre dans un fichier JSON.

    :param df_path: Chemin vers le fichier Parquet contenant les clics.
    :param output_path: Chemin du fichier JSON de sortie.
    """
    if not os.path.exists(df_path):
        raise FileNotFoundError(f"Fichier introuvable : {df_path}")

    df = pd.read_parquet(df_path)
    user_ids = sorted(df["user_id"].unique().tolist())

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(user_ids, f, indent=2)

    print(f"{len(user_ids)} user_id valides enregistrés dans {output_path}")


if __name__ == "__main__":
    # On remonte depuis utils/ → src/ → function_app/ → azure/ → 2-python/
    ROOT_DIR = Path(__file__).resolve().parents[4]  # <-- bonne racine du projet

    df_path = ROOT_DIR / "outputs" / "df_light.parquet"
    out_path = ROOT_DIR / "outputs" / "user_ids_valid.json"

    extract_and_save_user_ids(str(df_path), str(out_path))

# Commande à exécuter une seule fois après génération des artefacts :
# (venv_azure) python azure/function_app/src/utils/user_utils.py
