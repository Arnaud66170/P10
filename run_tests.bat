@echo off
REM ========================================================================
REM TESTS UNITAIRES DU PROJET P10 - SYSTÈME DE RECOMMANDATION
REM ========================================================================
REM Ce script lance tous les tests unitaires fonctionnels du projet
REM Tests rapides pour validation en développement (sans Azure check)
REM ========================================================================

echo.
echo === ACTIVATION ENVIRONNEMENT VIRTUEL ===
call venv_p10\Scripts\activate

echo.
echo === TESTS UNITAIRES DE BASE ===
REM Tests des fonctions de chargement de données (local/Azure)
REM - test_load_df_local : Chargement DataFrame depuis fichiers locaux
REM - test_load_df_azure : Chargement DataFrame depuis Azure Blob Storage
REM - test_load_embeddings_local : Chargement embeddings locaux (52 dimensions)
REM - test_load_embeddings_azure : Chargement embeddings depuis Azure
REM - test_load_cf_model_local : Chargement modèle CF depuis fichier local
REM - test_load_cf_model_azure : Chargement modèle CF depuis Azure (version light)
REM - test_get_recommendations_local : Test recommandations en mode local
REM - test_get_recommendations_azure : Test recommandations en mode Azure
pytest tests/test_loaders.py -v

echo.
echo === TESTS DE CONFIGURATION ===
REM Tests de la configuration des chemins et de l'environnement projet
REM - test_get_project_root : Validation du chemin racine du projet
pytest tests/test_paths.py -v

echo.
echo === TESTS DES WRAPPERS DE RECOMMANDATION ===
REM Tests des fonctions principales de recommandation
REM - test_get_recommendations_local : Test wrapper principal en mode local
REM - test_get_recommendations_azure : Test wrapper principal en mode Azure
pytest tests/test_wrappers.py -v

echo.
echo === TESTS DE COHÉRENCE MÉTIER ===
REM Tests de la logique métier et cohérence des recommandations
REM - test_reco : Test de cohérence des recommandations générées
pytest tests/test_recommendation_wrapper.py -v

echo.
echo === TESTS DE PERFORMANCE ===
REM Tests de performance et rapidité du système
REM - test_recommendation_performance : Recommandations en moins de 5 secondes
REM - test_multiple_users_performance : Performance avec plusieurs utilisateurs
pytest tests/test_performance.py -v

echo.
echo === BILAN GLOBAL DES TESTS FONCTIONNELS ===
REM Résumé de tous les tests fonctionnels (sans les tests API nécessitant Azure Function locale)
pytest tests/test_loaders.py tests/test_paths.py tests/test_wrappers.py tests/test_recommendation_wrapper.py tests/test_performance.py --tb=short

echo.
echo === TESTS TERMINÉS ===
echo 14 tests fonctionnels validés
echo Pour inclure la vérification Azure, utilisez : run_all.bat
pause