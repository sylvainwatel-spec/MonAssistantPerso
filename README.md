# Mon Assistant Perso - Workbench

Une application modulaire d'assistants IA avec capacités extensibles.

## 🏗 Architecture "Workbench"

L'application suit une nouvelle architecture modulaire où chaque grande fonctionnalité est un **Module** indépendant dans le dossier `modules/`.

### Modules Actuels
- **Assistants** (`modules/assistants/`): Gestion des assistants de chat personnalisés.
- **Paramètres** (`modules/settings/`): Administration centrale et configuration des clés API.
- **Studio Image** (`modules/image_gen/`): Génération d'images via DALL-E.
- **Analyse Docs** (`modules/doc_analyst/`): Analyse de documents PDF/TXT (RAG léger).

### Core
Le dossier `core/` contient les services transverses :
- `core/services/llm_service.py` : Passerelle unique pour tous les appels LLM (Chat, Embedding, Image).

## 🚀 Installation & Lancement

1. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

2. **Lancer l'application :**
   ```bash
   python main.py
   ```

3. **Lancer les tests :**
   ```bash
   python -m unittest discover tests
   ```

## ⚙️ Configuration
Toutes les clés API (OpenAI, Anthropic, etc.) et les préférences se configurent via l'interface graphique :
**Menu Principal > Administration > ⚙️**

Les paramètres sont sauvegardés chiffrés dans `settings.json`.
