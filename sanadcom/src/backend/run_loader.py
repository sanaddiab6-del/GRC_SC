"""Wrapper to run the controls loader against the sanadcom SQLite database."""
import sys
import os
import io

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Point to this backend's source
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///./sico_grc.db')
os.environ.setdefault('SECRET_KEY', 'sico-grc-dev-secret-key-32chars-minimum-safe')

# ---- inline the loader here so __file__ is correct ----
LOADER = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'scripts', 'load_complete_controls.py'
)
loader_path = os.path.normpath(LOADER)
src = io.open(loader_path, encoding='utf-8').read()

# Patch out the sys.path.insert line so it doesn't override our correct path
src = src.replace(
    "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))",
    "pass  # path already correct"
)

globs = {
    '__file__': loader_path,
    '__name__': '__main__',
}
exec(compile(src, loader_path, 'exec'), globs)
