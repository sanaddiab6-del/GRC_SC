import json
import time
import urllib.error
import urllib.request

last = None
for _ in range(40):
    try:
        request = urllib.request.Request('http://127.0.0.1:8000/api/ai/workforce/assistant/execute/',
                                         data=b'{"instruction":"Find the authorized NCA ECC framework"}',
                                         headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(request, timeout=2)
            raise AssertionError('Anonymous agent request unexpectedly accepted')
        except urllib.error.HTTPError as exc:
            assert exc.code in (401, 403), exc.code
            print(json.dumps({'gunicorn_started': True, 'anonymous_agent_http_status': exc.code}))
            break
    except (urllib.error.URLError, TimeoutError) as exc:
        last = exc
        time.sleep(1)
else:
    raise RuntimeError('Isolated backend failed HTTP startup') from last
