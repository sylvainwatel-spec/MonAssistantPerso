# Organisation du Projet

## Structure des Répertoires

### 📁 `tests/`
Contient **tous les fichiers de test** du projet.

**Convention de nommage** : `test_*.py`

**Fichiers** :
- Tests unitaires
- Tests d'intégration
- Tests de connecteurs LLM
- Scripts de diagnostic pour les tests

**Exemples** :
- `test_api_keys.py` - Tests de gestion des clés API
- `test_chat_logic.py` - Tests de la logique de chat
- `test_hf_token.py` - Tests du token Hugging Face
- `test_encryption.py` - Tests de cryptage/décryptage

### 📁 `scripts/`
Contient **tous les scripts utilitaires** et outils de développement.

**Convention de nommage** : `check_*.py`, `debug_*.py`, `diagnostic_*.py`

**Fichiers** :
- Scripts de vérification
- Scripts de debug
- Scripts de diagnostic
- Outils de développement

**Exemples** :
- `check_parsers.py` - Vérification des parsers
- `debug_langchain.py` - Debug de LangChain
- `diagnostic_huggingface.py` - Diagnostic Hugging Face
- `debug_gemini.py` - Debug de l'API Gemini

### 📁 `pages/`
Contient les **pages de l'interface utilisateur** (Tkinter/CustomTkinter).

### 📁 `utils/`
Contient les **modules utilitaires** et helpers.

### 📁 `resultats/`
Contient les **résultats de scraping** au format JSON.

---

## Principe d'Organisation

⚠️ **IMPORTANT** : Respecter cette organisation pour maintenir un projet propre et structuré.

### Règles

1. **Tests** → `tests/`
   - Tout fichier commençant par `test_`
   - Tout script de test ou diagnostic lié aux tests

2. **Scripts** → `scripts/`
   - Scripts de vérification (`check_*`)
   - Scripts de debug (`debug_*`)
   - Scripts de diagnostic (`diagnostic_*`)
   - Outils de développement

3. **Racine du projet** → Fichiers principaux uniquement
   - `main.py` - Point d'entrée de l'application
   - `requirements.txt` - Dépendances
   - `README.md` - Documentation
   - Fichiers de configuration (`.gitignore`, etc.)

### Avantages

✅ **Clarté** : Structure claire et prévisible
✅ **Maintenabilité** : Facile de trouver les fichiers
✅ **Professionnalisme** : Organisation standard
✅ **Collaboration** : Facilite le travail en équipe

---

## Déplacements Effectués (5 Décembre 2025)

### Tests déplacés vers `tests/`

**Fichiers Python (.py)** :
- ✅ `test_button.py`
- ✅ `test_auto_create.py`
- ✅ `test_gui_button.py`
- ✅ `test_hf_token.py`
- ✅ `test_hf_app_context.py`

**Fichiers de sortie de test (.txt)** :
- ✅ `test_admin_output.txt`
- ✅ `test_admin_output_fixed.txt`
- ✅ `test_admin_output_fixed_2.txt`
- ✅ `test_admin_output_fixed_3.txt`
- ✅ `test_chat_output.txt`
- ✅ `test_chat_output_fixed.txt`

### Scripts déplacés vers `scripts/`
- ✅ `check_parsers.py`
- ✅ `check_parsers_content.py`
- ✅ `check_prompts.py`
- ✅ `debug_langchain.py`
- ✅ `diagnostic_huggingface.py`

**Total** : 16 fichiers déplacés (5 tests .py + 6 tests .txt + 5 scripts)

---

## Commandes Utiles

### Lancer tous les tests
```bash
python -m pytest tests/
```

### Lancer un test spécifique
```bash
python -m pytest tests/test_api_keys.py
```

### Exécuter un script
```bash
python scripts/diagnostic_huggingface.py
```

---

**Dernière mise à jour** : 5 Décembre 2025
