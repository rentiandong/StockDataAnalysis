import subprocess

list_files = subprocess.run(['yapf', '-i', '--style={based_on_style: pep8, column_limit: 120}', 'main.py'], shell=True)
