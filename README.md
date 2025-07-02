# P10 – Système de recommandation d'articles (My Content)

Ce projet vise à créer un système complet de recommandation d’articles, incluant un moteur hybride, une API Azure Function déployée en mode serverless, et une interface utilisateur via Streamlit.

## 🔧 Structure du projet

```
P10/
├── azure/                    # Fonction Azure déployée
│   └── function_app/
├── data/                     # Données brutes et articles
├── models/                   # Modèles CF enregistrés
├── outputs/                  # Embeddings, df.parquet
├── src/                      # Fonctions IA (CF, CBF, Hybride)
├── streamlit_app/            # Interface utilisateur
├── tests/                    # Tests API et moteur de reco
├── notebooks/                # Explorations & prototypage
└── README.md
```

## 📦 Composants clés

- `src/model_training.py` : entraînement CBF / CF
- `src/recommendation_engine.py` : moteur hybride
- `src/wrappers.py` : fonction unique pour Azure
- `azure/function_app/` : Azure Function HTTP `getRecommendations`
- `streamlit_app/app.py` : interface utilisateur avec appel API

## 🚀 Lancer l’application

### 🔹 Lancer la fonction Azure en local

```bash
cd azure/function_app
func start
```

### 🔹 Lancer l’app Streamlit

```bash
cd streamlit_app
streamlit run app.py
```

## 📊 Exemple de requête API

```
GET /api/getRecommendations?user_id=59021&mode=auto&alpha=0.5&threshold=5&top_n=5
```

## ☁️ Déploiement Azure

- Function App : `https://p10arnaudrecommendcs.azurewebsites.net/api/getRecommendations`
- Artefacts à héberger dans Azure Blob Storage :
  - `df.parquet`
  - `df_articles.parquet`
  - `articles_embeddings_compressed.npz`
  - `model_cf.pkl`

## ✍️ Auteur

Projet réalisé par **Arnaud Caille** dans le cadre du parcours **OpenClassrooms – Ingénieur IA**.

