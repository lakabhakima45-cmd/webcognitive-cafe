@echo off
REM Lance le projet WebCognitive : l'API et l'interface, chacune dans sa fenetre.
REM Il suffit de double-cliquer sur ce fichier. Ne fermez pas les deux fenetres noires.

cd /d "%~dp0"

start "API WebCognitive" cmd /k ".venv\Scripts\python.exe -m uvicorn api:app --app-dir src"

REM on attend quelques secondes que l'API demarre
timeout /t 8 /nobreak >nul

start "Interface WebCognitive" cmd /k ".venv\Scripts\python.exe -m streamlit run src\interface.py"
