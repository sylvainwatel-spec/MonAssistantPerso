# Guide d'Installation

Ce document décrit la procédure pour installer l'application sur une nouvelle machine Windows disposant déjà de Python et Git.

## 1. Récupération du code source

Ouvrez un terminal (PowerShell ou Invite de commandes) et exécutez les commandes suivantes :

```bash
# Clonez le dépôt (remplacez l'URL par celle de votre dépôt)
git clone <URL_VOTRE_DEPOT_GIT>

# Entrez dans le dossier du projet
cd simple_python_app
```
*(Note : Le nom du dossier `simple_python_app` dépend du nom de votre dépôt).*

## 2. Installation de l'environnement

Il est recommandé d'utiliser un environnement virtuel pour éviter les conflits de versions.

### Création et activation de l'environnement virtuel

```powershell
# Création de l'environnement virtuel nommé ".venv"
python -m venv .venv

# Activation (PowerShell)
.\.venv\Scripts\Activate
```
*Si vous utilisez l'Invite de commandes (cmd), l'activation se fait via `.venv\Scripts\activate.bat`.*

### Installation des dépendances

Une fois l'environnement activé (vous devriez voir `(.venv)` au début de la ligne de commande) :

```bash
# Installation des librairies Python requises
pip install -r requirements.txt

# Installation des navigateurs pour Playwright (nécessaire pour le scraping)
playwright install
```

## 3. Lancement de l'application

Toujours dans l'environnement virtuel activé :

```bash
python main.py
```

## 4. Mise à jour de l'application

Si vous avez déjà installé l'application et souhaitez récupérer la dernière version :

1.  Ouvrez un terminal dans le dossier de l'application.
2.  Exécutez la commande suivante pour télécharger les modifications :
    ```bash
    git pull
    ```
3.  Si des dépendances ont changé, réinstallez-les :
    ```bash
    .\.venv\Scripts\Activate
    pip install -r requirements.txt
    ```
