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

## 5. Alternative : Version Portable (Sans installation)

Si vous ne pouvez pas installer Python ou les dépendances sur le poste cible (restrictions de droits), vous pouvez créer un exécutable autonome depuis un poste où vous avez les droits.

### Sur le poste "Source" (avec droits) :
1.  Assurez-vous que tout est installé et fonctionnel.
2.  Lancez la compilation :
    ```bash
    python build_app.py
    ```
3.  Une fois terminé, récupérez le fichier `MonAssistantPerso.exe` dans le dossier `dist/`.

### Sur le poste "Cible" (sans droits) :
1.  Copiez simplement le fichier `MonAssistantPerso.exe`.
2.  Lancez-le.
    *Note : Les fonctionnalités de scraping (navigation web) peuvent nécessiter des navigateurs. Si elles échouent, il faudra peut-être installer les navigateurs Playwright manuellement si possible, ou copier le dossier de cache des navigateurs.*

## 6. Migration depuis un autre PC

Si vous installez l'application sur un nouveau PC et souhaitez récupérer vos assistants et votre configuration (clés API), vous devez copier manuellement certains fichiers depuis votre ancienne installation.

Ces fichiers ne sont pas inclus dans le dépôt Git pour des raisons de sécurité.

### Fichiers à copier :

Copiez les fichiers suivants de la racine du dossier de l'application sur l'ancien PC vers la racine du dossier sur le nouveau PC :

1.  **`assistants.json`** : Contient tous vos assistants créés.
2.  **`settings.json`** : Contient votre configuration (Clés API, modèle par défaut, thème, etc.).
3.  **`.secret.key`** : **IMPORTANT**. C'est la clé qui permet de déchiffrer vos clés API stockées dans `settings.json`. Si vous ne copiez pas ce fichier, votre fichier `settings.json` sera illisible.

### Procédure :
1.  Installez l'application sur le nouveau PC (suivez les étapes 1 et 2 de ce guide).
2.  Copiez/Collez les 3 fichiers ci-dessus dans le dossier de l'application sur le nouveau PC.
3.  Lancez l'application. Vous devriez retrouver tout votre environnement.
