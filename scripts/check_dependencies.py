
import os
import ast
import sys
import importlib.util

# Mapping of import names to PyPI package names
IMPORT_TO_PYPI = {
    'PIL': 'Pillow',
    'cv2': 'opencv-python',
    'yaml': 'PyYAML',
    'bs4': 'beautifulsoup4',
    'dotenv': 'python-dotenv',
    'sklearn': 'scikit-learn',
    'skimage': 'scikit-image',
    'telegram': 'python-telegram-bot',
    'playwright': 'playwright',
    'customtkinter': 'customtkinter',
    'cryptography': 'cryptography',
    'OpenAI': 'openai',  # Case insensitive check usually handles this, but good to have
    'google.generativeai': 'google-generativeai',
    'anthropic': 'anthropic',
    'groq': 'groq',
    'mistralai': 'mistralai',
    'openpyxl': 'openpyxl',
    'requests': 'requests',
    'yfinance': 'yfinance',
    'huggingface_hub': 'huggingface_hub',
    'pypdf': 'pypdf',
    'pandas': 'pandas',
    'matplotlib': 'matplotlib',
    'presentation': 'python-pptx',
    'pptx': 'python-pptx',
    'scrapegraphai': 'scrapegraphai',
    'langchain': 'langchain',
    'langchain_core': 'langchain',
    'langchain_community': 'langchain',
    'langchain_community': 'langchain',
    'docx': 'python-docx',
    'playwright_stealth': 'playwright-stealth',
    'scrapegraph_py': 'scrapegraph-py',
    'google': 'google-generativeai',
    'core': 'ignore_local', # Should be handled by logic but hardcoding for safety
}

# Known standard library modules (incomplete list, but covers common ones)
STD_LIB = {
    'os', 'sys', 're', 'json', 'time', 'datetime', 'math', 'random', 'subprocess', 
    'threading', 'multiprocessing', 'typing', 'collections', 'itertools', 'functools',
    'pathlib', 'shutil', 'glob', 'ast', 'platform', 'logging', 'traceback', 'io',
    'base64', 'hashlib', 'uuid', 'copy', 'enum', 'inspect', 'warnings', 'email',
    'http', 'urllib', 'socket', 'sqlite3', 'tkinter', 'unittest', 'abc', 'argparse',
    'contextlib', 'csv', 'ctypes', 'dataclasses', 'decimal', 'difflib', 'distutils',
    'filecmp', 'fnmatch', 'gc', 'getpass', 'gettext', 'gzip', 'heapq', 'hmac',
    'html', 'imageop', 'imaplib', 'imghdr', 'imp', 'importlib', 'ipaddress',
    'keyword', 'linecache', 'locale', 'lzma', 'mailcap', 'marshal', 'mimetypes',
    'mmap', 'modulefinder', 'msilib', 'msvcrt', 'netrc', 'nntplib', 'numbers',
    'operator', 'optparse', 'pickle', 'pipes', 'pkgutil', 'plistlib', 'poplib',
    'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile',
    'pyclbr', 'pydoc', 'queue', 'quopri', 'runpy', 'sched', 'secrets', 'select',
    'selectors', 'shelve', 'shlex', 'signal', 'site', 'smtpd', 'smtplib',
    'sndhdr', 'socketserver', 'spwd', 'ssl', 'stat', 'statistics', 'string',
    'stringprep', 'struct', 'sunau', 'symbol', 'symtable', 'sysconfig',
    'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios',
    'test', 'textwrap', 'this', 'timeit', 'token', 'tokenize', 'trace',
    'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'unicodedata',
    'uu', 'venv', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound',
    'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport',
    'zlib', 'zoneinfo'
}

def get_framework_imports(root_dir):
    """Scan all .py files for imports."""
    imports = set()
    local_modules = set()

    # First pass: identify local modules
    for subdir, _, files in os.walk(root_dir):
        if 'venv' in subdir or '.git' in subdir or '__pycache__' in subdir:
            continue
            
        # Add package name to local modules if __init__.py exists
        if '__init__.py' in files:
            rel_path = os.path.relpath(subdir, root_dir).replace(os.sep, '.')
            if rel_path != '.':
                local_modules.add(rel_path.split('.')[0])
                
        # Also assume any top-level directory is a potential namespace or local module if imported
        if subdir == root_dir:
            for item in os.listdir(root_dir):
                if os.path.isdir(os.path.join(root_dir, item)) and not item.startswith('.'):
                    local_modules.add(item)

        for file in files:
            if file.endswith('.py'):
                module_name = file[:-3]
                local_modules.add(module_name)

    # Second pass: gather imports
    for subdir, _, files in os.walk(root_dir):
        if 'venv' in subdir or '.git' in subdir or '__pycache__' in subdir:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(subdir, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    return imports, local_modules

def check_requirements(requirements_path, imports, local_modules):
    """Compare found imports with requirements.txt."""
    if not os.path.exists(requirements_path):
        print("requirements.txt not found!")
        return

    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = {line.strip().split('==')[0].split('>=')[0].lower() for line in f if line.strip() and not line.startswith('#')}

    missing = []
    
    for imp in imports:
        # Ignore local modules and stdlib
        if imp in local_modules or imp in STD_LIB:
            continue
            
        # Map to PyPI name
        pypi_name = IMPORT_TO_PYPI.get(imp, imp)
        
        # Check against requirements (case insensitive)
        if pypi_name.lower() not in requirements:
            # Special case for modules that might be part of other packages or system libs
            # but usually, valid pypi packages should be listed.
            missing.append((imp, pypi_name))
            
    return missing, requirements

def main():
    root_dir = os.getcwd()
    requirements_path = os.path.join(root_dir, 'requirements.txt')
    
    print(f"Scanning {root_dir}...")
    imports, local_modules = get_framework_imports(root_dir)
    
    # print(f"Local modules found: {local_modules}")
    # print(f"Imports found: {imports}")
    
    missing, requirements = check_requirements(requirements_path, imports, local_modules)
    
    if missing:
        print("\nPossible missing dependencies found:")
        print(f"{'Import':<20} | {'Suggested PyPI Package':<20}")
        print("-" * 45)
        for imp, pkg in missing:
            print(f"{imp:<20} | {pkg:<20}")
    else:
        print("\nNo missing dependencies found! (based on heuristic check)")
        
    print("\nInstallability considerations:")
    if 'playwright' in requirements:
        print("- 'playwright' requires 'playwright install' to download browser binaries.")

if __name__ == "__main__":
    main()
