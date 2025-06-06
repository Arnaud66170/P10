# src/utils/validators.py

def check_column_presence(df, required_cols, df_name) :
    """
    Vérifie que les colonnes attendues sont bien présentes dans un DataFrame.

    Args :
        df (pd.DataFrame) : le DataFrame à vérifier
        required_cols (list) : liste des noms de colonnes attendues
        df_name (str) : nom symbolique du DataFrame (pour message d'erreur)

    Raises :
        ValueError : si une colonne est manquante
    """
    for col in required_cols :
        if col not in df.columns :
            raise ValueError(f"Colonne '{col}' manquante dans {df_name}. Vérifie le schéma.")
