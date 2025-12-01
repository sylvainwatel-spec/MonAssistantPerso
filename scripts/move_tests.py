import os, shutil

project_root = os.path.abspath(os.path.dirname(__file__))
src_dir = project_root

test_files = [f for f in os.listdir(src_dir) if f.startswith('test_') and f.endswith('.py')]

tests_dir = os.path.join(src_dir, 'tests')
os.makedirs(tests_dir, exist_ok=True)

for fname in test_files:
    src_path = os.path.join(src_dir, fname)
    dst_path = os.path.join(tests_dir, fname)
    # Move file
    shutil.move(src_path, dst_path)
    # Write warning placeholder back to original location
    with open(src_path, 'w', encoding='utf-8') as f:
        f.write(f"# NOTE: Ce fichier a été déplacé vers le répertoire tests/. Le code original se trouve désormais dans tests/{fname}\n")

print('Déplacement terminé.')
