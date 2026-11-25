import hashlib
import json
from pathlib import Path

entries = json.loads(Path('/release-input/source-manifest.json').read_text(encoding='utf-8'))
count = 0
overlaid = 0
for item in entries:
    if not item['source'].startswith('backend/'):
        continue
    path = Path('/code') / item['source'].removeprefix('backend/')
    raw = path.read_bytes()
    if item['overlaid']:
        assert hashlib.sha256(raw).hexdigest() == item['sha256'], item['source']
        overlaid += 1
    else:
        normalized = raw.decode('utf-8-sig').replace('\r\n', '\n').encode()
        assert hashlib.sha256(normalized).hexdigest() == item['normalizedSha256'], item['source']
    count += 1
print(json.dumps({'image_source_manifest_verified': True, 'dependency_files_checked': count,
                  'overlaid_backend_files': overlaid}))
