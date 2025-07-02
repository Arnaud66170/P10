@echo off
echo ===================================
echo Connexion à Azure...
echo ===================================
az login
IF %ERRORLEVEL% NEQ 0 (
    echo ERREUR : Impossible de se connecter à Azure.
    pause
    exit /b
)

echo ===================================
echo Vérification de la souscription...
echo ===================================
az account show
IF %ERRORLEVEL% NEQ 0 (
    echo ERREUR : Aucune souscription détectée.
    pause
    exit /b
)

echo ===================================
echo Publication de la Function App...
echo ===================================
cd C:\Users\motar\Desktop\1-openclassrooms\AI_Engineer\1-projets\P10\2-python\azure\function_app
func azure functionapp publish p10arnaudrecommendcs

echo ===================================
echo Terminé.
pause
