from pathlib import Path
import sys

BANNED = [
    'tannin','tannic','acidity structure','bouquet','palate','finish length',
    'terroir','sommelier','decant','varietal typicity','critic score','oaky'
]

violations = []
for path in Path('app/templates').glob('*.html'):
    text = path.read_text(encoding='utf-8').lower()
    for term in BANNED:
        if term in text:
            violations.append(f"{path}: {term}")

if violations:
    print('Found banned terms:')
    print('\n'.join(violations))
    sys.exit(1)
print('No banned terms found in UI copy.')
