# azure/function_app/add_node_to_path.bat

@echo off
SET "NODE_PATH=C:\Program Files\nodejs"
echo.
echo 📍 Ajout de Node.js au PATH utilisateur temporairement...
setx PATH "%PATH%;%NODE_PATH%"
echo ✅ Terminé. Redémarre ton terminal pour prendre en compte les changements.
pause
