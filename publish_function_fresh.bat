@echo off
:: ============================================================================
:: Script de publication pour nouvelle Function App Azure (p10recommandationfresh)
:: ============================================================================

echo ===================================
echo Publication Function App Fresh - P10 Recommandations
echo ===================================

:: Navigation vers le dossier principal du projet
cd /d C:\Users\motar\Desktop\1-openclassrooms\AI_Engineer\1-projets\P10\2-python

:: Vérification de la connexion Azure
echo Vérification de la connexion Azure...
az account show --query "name" --output tsv
IF %ERRORLEVEL% NEQ 0 (
    echo ERREUR : Connexion Azure requise. Lancement az login...
    az login
    IF %ERRORLEVEL% NEQ 0 (
        echo ERREUR : Impossible de se connecter à Azure.
        pause
        exit /b 1
    )
)

:: Nettoyage des fichiers temporaires
echo Nettoyage des fichiers __pycache__...
for /r azure\function_app %%i in (__pycache__) do rd /s /q "%%i" 2>nul

:: Navigation vers le dossier function_app
cd azure\function_app

:: Vérification de la structure requise
if not exist "get_recommendations\function.json" (
    echo ERREUR : Structure Function App invalide - function.json manquant
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERREUR : requirements.txt manquant
    pause
    exit /b 1
)

:: Publication vers la nouvelle Function App
echo ===================================
echo Publication vers p10recommandationfresh...
echo ===================================
func azure functionapp publish p10recommandationfresh --build remote

:: Vérification du succès
IF %ERRORLEVEL% EQU 0 (
    echo ===================================
    echo Publication réussie !
    echo URL Function App : https://p10recommandationfresh.azurewebsites.net
    echo ===================================
) ELSE (
    echo ===================================
    echo Erreur lors de la publication
    echo ===================================
)

pause