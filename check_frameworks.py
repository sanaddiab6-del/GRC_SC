import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

import json
from django.test import RequestFactory
from core.views import FrameworkViewSet
from iam.models import User
from rest_framework.test import force_authenticate

user = User.objects.get(email='admin@example.com')
factory = RequestFactory()

# Test provider=NCA
request = factory.get('/api/frameworks/', {'provider': 'NCA'})
force_authenticate(request, user=user)
view = FrameworkViewSet.as_view({'get': 'list'})
response = view(request)
response.render()
data = json.loads(response.content)
print('=== ?provider=NCA ===')
print(f"Status: {response.status_code}, Count: {data.get('count', 'N/A')}")
if 'results' in data:
    for r in data['results']:
        print(f"  {r['name']} - provider: {r['provider']}")

# Test provider=SAMA
request2 = factory.get('/api/frameworks/', {'provider': 'SAMA'})
force_authenticate(request2, user=user)
response2 = view(request2)
response2.render()
data2 = json.loads(response2.content)
print('\n=== ?provider=SAMA ===')
print(f"Status: {response2.status_code}, Count: {data2.get('count', 'N/A')}")
if 'results' in data2:
    for r in data2['results']:
        print(f"  {r['name']} - provider: {r['provider']}")
