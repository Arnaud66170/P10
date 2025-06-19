@echo off
REM Active l'environnement virtuel et exécute les tests Pytest

cd /d %~dp0
call venv_p10\Scripts\activate.bat

echo -----------------------------------------
echo Lancement des tests avec Pytest...
echo -----------------------------------------

pytest tests

echo -----------------------------------------
echo Tests terminés. Appuie sur une touche pour fermer.
echo -----------------------------------------
pause
