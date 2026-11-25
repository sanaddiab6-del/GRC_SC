"""Image-only source inventory. No Django imports, startup, DB or network calls."""
import hashlib
import json
from pathlib import Path

root = Path('/code')
paths = list((root / 'ai_onboarding').glob('*.py'))
paths += list((root / 'ai_onboarding' / 'migrations').glob('*.py'))
paths += [root / 'ciso_assistant/settings.py', root / 'core/models.py', root / 'iam/models.py']
print(json.dumps({str(p.relative_to(root)): hashlib.sha256(p.read_text(encoding='utf-8').replace('\r\n', '\n').encode()).hexdigest()
                  for p in paths if p.is_file()}, sort_keys=True))
