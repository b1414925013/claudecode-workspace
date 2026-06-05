import sys
import os
from datetime import datetime

data = sys.stdin.read()
import json
d = json.loads(data) if data else {}
prompt = d.get('prompt', '')

log_file = 'prompt_log.txt'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Create file if not exists
if not os.path.exists(log_file):
    open(log_file, 'w').close()

# Append with timestamp and tab separator
with open(log_file, 'a', encoding='utf-8') as f:
    f.write(f'{timestamp}\t{prompt}\n')