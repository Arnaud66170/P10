# scripts/explore_metadata.py
"""
Script pour explorer les métadonnées réelles des articles
"""
import pandas as pd
import json
from pathlib import Path

def explore_articles_metadata():
    """Explore en détail les métadonnées des articles"""
    
    # Chemin vers les fichiers
    project_root = Path(__file__).parent.parent
    articles_path = project_root / "outputs" / "df_articles_light.parquet"
    user_ids_path = project_root / "outputs" / "user_ids_valid.json"
    
    print("=" * 60)
    print("EXPLORATION DES MÉTADONNÉES P10")
    print("=" * 60)
    
    # 1. Métadonnées des articles
    try:
        df_articles = pd.read_parquet(articles_path)
        
        print(f"\n📄 ARTICLES METADATA ({articles_path})")
        print(f"   Nombre d'articles: {len(df_articles):,}")
        print(f"   Colonnes disponibles: {len(df_articles.columns)}")
        
        print(f"\n📊 STRUCTURE DES DONNÉES:")
        for i, col in enumerate(df_articles.columns, 1):
            dtype = df_articles[col].dtype
            nunique = df_articles[col].nunique()
            null_count = df_articles[col].isnull().sum()
            null_pct = (null_count / len(df_articles)) * 100
            
            print(f"   {i:2d}. {col:<25} | {str(dtype):<10} | {nunique:>8,} uniques | {null_pct:5.1f}% null")
        
        print(f"\n📋 ÉCHANTILLON DE DONNÉES:")
        print(df_articles.head(3).to_string())
        
        print(f"\n🔍 EXEMPLES PAR COLONNE:")
        for col in df_articles.columns:
            if df_articles[col].dtype == 'object':  # Colonnes texte
                examples = df_articles[col].dropna().head(3).tolist()
                print(f"   {col}: {examples}")
            elif df_articles[col].dtype in ['int64', 'float64']:  # Colonnes numériques
                min_val = df_articles[col].min()
                max_val = df_articles[col].max()
                mean_val = df_articles[col].mean()
                print(f"   {col}: min={min_val}, max={max_val}, moyenne={mean_val:.2f}")
    
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {articles_path}")
    except Exception as e:
        print(f"❌ Erreur articles: {e}")
    
    # 2. User IDs valides
    try:
        with open(user_ids_path, 'r', encoding='utf-8') as f:
            user_ids = json.load(f)
        
        print(f"\n👥 USER IDS VALIDES ({user_ids_path})")
        print(f"   Nombre d'utilisateurs: {len(user_ids):,}")
        print(f"   Premier user_id: {min(user_ids)}")
        print(f"   Dernier user_id: {max(user_ids)}")
        print(f"   Exemples: {user_ids[:10]}")
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {user_ids_path}")
    except Exception as e:
        print(f"❌ Erreur user_ids: {e}")
    
    print(f"\n" + "=" * 60)
    print("EXPLORATION TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    explore_articles_metadata()

# Lancement depuis P10/2-python/ avec venv_p10 activé:
# python scripts/explore_metadata.py