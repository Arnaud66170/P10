@echo off
:: =============================================================================
:: Script de déploiement Azure Function App en mode .zip (config-zip)
:: =============================================================================

cd /d C:\Users\motar\Desktop\1-openclassrooms\AI_Engineer\1-projets\P10\2-python\azure\function_app

echo ===================================
echo 📦 Nettoyage des anciens __pycache__...
for /r %%i in (__pycache__) do rd /s /q "%%i"

echo ===================================
echo 🔁 Génération du fichier .zip...
powershell Compress-Archive -Path get_recommendations, src, requirements.txt -DestinationPath ../function_app.zip -Force

echo ===================================
echo 🔐 Connexion à Azure...
az login
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur de connexion Azure.
    pause
    exit /b
)

echo ===================================
echo 🚀 Déploiement via az functionapp deployment source config-zip...
az functionapp deployment source config-zip ^
  --resource-group P10ArnaudResourceGroup ^
  --name p10-arnaud-func ^
  --src ../function_app.zip

echo ===================================
echo ✅ Déploiement terminé avec succès.
pause

