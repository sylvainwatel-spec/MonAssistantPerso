@echo off
echo ==========================================
echo      Mon Assistant Perso - Setup
echo ==========================================

echo.
echo [1/4] Verification de Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python detecte.
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo Python (py launcher) detecte.
        set PYTHON_CMD=py
    ) else (
        echo ATTENTION: Python ne semble pas etre dans le PATH.
        echo L'installation des dependances pourrait echouer.
        set PYTHON_CMD=python
    )
)

echo.
echo [2/4] Installation des dependances...
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo [3/4] Configuration de Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git n'est pas detecte. Assurez-vous qu'il est installe.
)

if not exist .git (
    echo Initialisation du depot Git...
    git init
    git add .
    git commit -m "Initial commit: Project Setup"
    echo Depot initialise avec succes.
) else (
    echo Le depot Git existe deja.
)

echo.
echo ==========================================
echo      Installation terminee !
echo ==========================================
pause
