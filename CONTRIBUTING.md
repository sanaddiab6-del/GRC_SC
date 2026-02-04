# SICO GRC Platform - Contributing Guide

## Welcome

Thank you for contributing to the SICO GRC Platform! This guide will help you get started.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sonaiso/sanadcom.git
   cd sanadcom
   ```

2. **Backend setup**
   ```bash
   cd src/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   cd src/frontend
   npm install
   ```

4. **Start services**
   ```bash
   # From project root
   docker-compose up -d
   ```

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Emergency fixes

### Creating a Feature

1. Create a branch from `develop`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
   - Write code
   - Add tests
   - Update documentation

3. Commit your changes
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

4. Push and create PR
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/tooling changes

Examples:
```
feat: add PDPL breach register
fix: correct ECC control mapping
docs: update API documentation
```

## Code Standards

### Python (Backend)

- Follow PEP 8
- Use type hints
- Write docstrings
- Run linters:
  ```bash
  black app/
  flake8 app/
  mypy app/
  ```

### TypeScript (Frontend)

- Follow ESLint rules
- Use TypeScript strictly
- Write JSDoc comments
- Run linters:
  ```bash
  npm run lint
  npm run type-check
  ```

## Testing

### Backend Tests

```bash
cd src/backend
pytest
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd src/frontend
npm test
npm run test:coverage
```

### Test Requirements

- All new features must have tests
- Maintain > 80% coverage
- Tests must pass before merging

## Documentation

### Code Documentation

- Add docstrings to all functions/classes
- Include type hints
- Document complex logic
- Add inline comments sparingly

### User Documentation

- Update docs/ when adding features
- Include screenshots for UI changes
- Provide examples
- Keep language simple

### API Documentation

- Use OpenAPI/Swagger annotations
- Document all endpoints
- Include request/response examples
- Note authentication requirements

## Pull Request Process

1. **Before submitting**:
   - Run tests and linters
   - Update documentation
   - Add changelog entry
   - Rebase on latest develop

2. **PR Description**:
   - Describe what changed
   - Explain why
   - Link related issues
   - Add screenshots (UI changes)

3. **Review process**:
   - Address review comments
   - Keep PR focused and small
   - Be responsive to feedback

4. **After approval**:
   - Squash commits if needed
   - Update from develop
   - Merge when CI passes

## Code Review Guidelines

### As a Reviewer

- Be constructive and respectful
- Focus on code quality
- Check for security issues
- Verify tests exist
- Ensure documentation updated

### As an Author

- Respond to all comments
- Ask questions if unclear
- Make requested changes
- Thank reviewers

## Release Process

1. **Version bump**
   - Update version numbers
   - Update CHANGELOG.md
   - Tag release

2. **Testing**
   - Run full test suite
   - Test in staging
   - Verify migrations

3. **Deploy**
   - Deploy to production
   - Monitor for issues
   - Update documentation

## Getting Help

- **Questions**: Open a discussion
- **Bugs**: Create an issue
- **Features**: Create an issue with proposal
- **Security**: Contact team lead directly

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to SICO GRC Platform!
