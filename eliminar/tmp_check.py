from pathlib import Path
p = Path('c:/Users/Juan rodriguez/systemasDiploma/Inventory-Corpus-v2/frontend/src/app/pages/detection/detection.component.scss')
text = p.read_text(encoding='utf-8')
print('file', p)
bal = 0
for i, ch in enumerate(text):
    if ch == '{':
        bal += 1
    elif ch == '}':
        bal -= 1
    if bal < 0:
        print('unmatched closing brace at index', i, 'line', text.count('\n', 0, i) + 1)
        bal = 0
print('final balance', bal)

# print around line 470-520
lines = text.split('\n')
for ln in range(460, 531):
    if ln-1 < len(lines):
        print(f"{ln+1:04d}: {lines[ln]}")
