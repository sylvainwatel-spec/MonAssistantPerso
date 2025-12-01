# Guide de Démarrage - Environnement Virtuel

## Problème Résolu
L'erreur `Model.__init__() got an unexpected keyword argument 'thinking'` était causée par des conflits de dépendances entre ScrapeGraphAI et LangChain dans l'environnement global.

## Solution : Environnement Virtuel Dédié

Un environnement virtuel `venv_scrapegraph` a été créé avec des versions compatibles et à jour de toutes les dépendances.

### Configuration Installée
- **Python**: 3.12
- **pip**: 25.3
- **ScrapeGraphAI**: 1.64.0
- **LangChain**: 1.1.0
- **LangChain Core**: 1.1.0
- **LangChain Community**: 0.4.1
- **Playwright**: Dernière version
- Toutes les dépendances du projet (voir `requirements.txt`)

### Activation de l'Environnement Virtuel

#### Windows (PowerShell):
```powershell
.\venv_scrapegraph\Scripts\activate.ps1
```

#### Lancement de l'Application:
```powershell
# Activer l'environnement
.\venv_scrapegraph\Scripts\activate.ps1

# Lancer l'application
python main.py
```

### Tests Disponibles

Les tests suivants ont été validés dans l'environnement virtuel :
- `test_scrapegraph.py` - Import de ScrapeGraphAI ✅
- `test_ai_scraper_simple.py` - Initialisation AIScraper ✅
- `test_encryption.py` - Chiffrement des clés API ✅
- `test_instruction_parser.py` - Parsing des instructions ✅

### Désactivation
```powershell
deactivate
```

### Notes Importantes
- L'environnement virtuel doit être **activé** à chaque session de travail
- Les clés API et configurations sont stockées dans `settings.json` (en dehors du venv)
- Pour installer de nouvelles dépendances : activer le venv puis utiliser `pip install`

### Maintenance
Pour mettre à jour les dépendances :
```powershell
.\venv_scrapegraph\Scripts\activate.ps1
pip install --upgrade scrapegraphai langchain langchain-core
```
