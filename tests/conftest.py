# Pytest configuration
import sys
import os

os.environ.setdefault("PYTEST_RUNNING", "1")

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))
