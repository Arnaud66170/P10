@echo off
:: Aller à la racine du projet
cd /d C:\Users\motar\Desktop\1-openclassrooms\AI_Engineer\1-projets\P10\2-python

echo ===============================
echo Activation de l'environnement venv_streamlit_azure...
echo ===============================
IF EXIST streamlit_app\venv_streamlit_azure\Scripts\activate.bat (
    call streamlit_app\venv_streamlit_azure\Scripts\activate.bat
) ELSE (
    echo Le dossier streamlit_app\venv_streamlit_azure est introuvable !
    pause
    exit /b
)

echo ===============================
echo Lancement de Streamlit...
echo ===============================
cd streamlit_app
streamlit run app.py
pause
