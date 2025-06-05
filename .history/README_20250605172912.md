# Projet P10 - Système de recommandation de contenus (My Content)

Ce dépôt contient une application MVP de recommandation d’articles personnalisés.  
Déploiement prévu en serverless via Azure Function.

## Dossiers

- `src/` : scripts IA modulaires
- `notebooks/` : notebooks de prototypage (sans fonction)
- `data/` : fichiers fournis
- `models/` : artefacts entraînés
- `outputs/` : résultats temporaires
- `streamlit_app/` : interface utilisateur
- `azure/` : code de la Function Azure

## Démarrage

```bash
python -m venv venv_p10
venv_p10\Scripts\activate
pip install -r requirements.txt
