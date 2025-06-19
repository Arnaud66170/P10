# ============================================================================
# src/visuals/interactive_alpha.py
# Fonction pour affichage interactif des recommandations hybrides via ipywidgets
# ============================================================================

from IPython.display import clear_output, display
import pandas as pd

def update_recommendations(change,
                           user_id,
                           df,
                           embeddings,
                           article_id_to_index,
                           model_cf,
                           df_articles,
                           output_widget,
                           top_n = 5,
                           get_hybrid_recommendations_func = None):
    """
    Callback pour affichage interactif avec ipywidgets (slider alpha).

    Args:
        change (dict) : événement envoyé par le widget
        user_id (int) : utilisateur ciblé
        df (pd.DataFrame) : DataFrame des interactions
        embeddings (np.ndarray) : matrice des embeddings compressés
        article_id_to_index (dict) : mapping article_id → index
        model_cf : modèle CF entraîné
        df_articles (pd.DataFrame) : DataFrame contenant les métadonnées articles
        output_widget : zone de sortie ipywidgets.Output()
        top_n (int) : nombre d'articles recommandés
        get_hybrid_recommendations_func (function) : fonction à appeler (obligatoire)
    """
    if get_hybrid_recommendations_func is None:
        raise ValueError("⚠️ La fonction 'get_hybrid_recommendations_func' doit être fournie.")

    with output_widget:
        clear_output(wait = True)
        alpha = change["new"]
        print(f"Recommandations hybrides pour alpha = {alpha:.1f} :\n")

        reco_ids = get_hybrid_recommendations_func(user_id = user_id,
                                                   df = df,
                                                   embeddings = embeddings,
                                                   article_id_to_index = article_id_to_index,
                                                   model_cf = model_cf,
                                                   top_n = top_n,
                                                   alpha = alpha)

        df_reco = df_articles[df_articles["article_id"].isin(reco_ids)]

        display(df_reco[["article_id", "category_id", "publisher_id", "words_count", "created_at_ts"]])
