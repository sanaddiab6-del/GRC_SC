# SICO GRC Platform - Contributing Guide

Thank you for your interest in contributing to the SICO GRC Platform!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/sanadcom.git
cd sanadcom

# Run setup script
bash scripts/setup.sh

# Create a feature branch
git checkout -b feature/your-feature-name
```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Run `black` for formatting:
  ```bash
  black src/backend/
  ```

### TypeScript (Frontend)
- Follow TypeScript best practices
- Use ESLint for linting:
  ```bash
  npm run lint
  ```
- Use Prettier for formatting

## Testing

### Backend Tests
```bash
cd src/backend
source venv/bin/activate
pytest tests/ -v
```

### Frontend Tests
```bash
cd src/frontend
npm test
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add support for CCC framework mapping
fix: Correct control ID validation
docs: Update API documentation
test: Add tests for control filtering
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update the README if needed
5. Submit your PR with a clear description

## Code Review

- All PRs require review
- Address review comments promptly
- Be respectful and constructive

## Areas for Contribution

- Adding missing controls
- Improving bilingual content
- Writing tests
- Documentation improvements
- UI/UX enhancements
- API features
- Bug fixes

## Questions?

Feel free to open an issue for questions or discussions.

Thank you for contributing!
