import re
from pathlib import Path
import random
import time

time.sleep(10)

random_number = random.randint(900, 999)

pattern = r'https://www\.loliapi\.com/acg(\?id=(\d+))?'
replacement = f'https://www.loliapi.com/acg?id={random_number}'

path = Path('README.md')
with path.open('r+', encoding='utf-8') as file:
    content = file.read()

    new_content = re.sub(pattern, replacement, content)

    file.seek(0)
    file.write(new_content)
    file.truncate()  
