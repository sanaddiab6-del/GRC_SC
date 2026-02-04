# Contributing to SICO GRC Platform

Thank you for your interest in contributing to the SICO GRC Platform! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Merge Conflict Resolution](#merge-conflict-resolution)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Security](#security)
- [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git 2.30+

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sonaiso/sanadcom.git
   cd sanadcom
   ```

2. **Configure Git for optimal merge handling:**
   ```bash
   make git-setup
   ```

3. **Install dependencies:**
   ```bash
   make install
   ```

4. **Start development environment:**
   ```bash
   make dev
   ```

5. **Verify setup:**
   ```bash
   make test
   ```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch from the latest `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes
- `security/` - Security improvements

### 2. Make Your Changes

- Keep commits small and focused
- Write descriptive commit messages
- Follow the code standards (see below)
- Add tests for new functionality

**Good commit message example:**
```
Add bilingual validation to Control model

- Add validation for both Arabic and English fields
- Ensure RTL formatting preserved in Arabic text
- Add unit tests for validation logic

Relates to: #123
```

### 3. Test Your Changes

Before committing:

```bash
# Backend tests
cd src/backend && pytest tests/

# Frontend tests
cd src/frontend && npm test

# Run linters
make lint

# Check for security issues
make security
```

### 4. Check for Conflicts Early

Before creating a PR, check if your branch will have conflicts:

```bash
make check-conflicts
```

If conflicts are detected, resolve them before opening a PR.

### 5. Keep Your Branch Updated

Regularly sync with main to avoid conflicts:

```bash
git checkout main
git pull origin main
git checkout your-branch
git rebase main
```

## Merge Conflict Resolution

We take merge conflicts seriously and have comprehensive tooling to handle them.

### Preventing Conflicts

1. **Keep branches short-lived** (1-3 days maximum)
2. **Rebase frequently** with main
3. **Coordinate with team** when editing the same modules
4. **Use the conflict detection tool** before creating PRs

### Detecting Conflicts

Run before opening a PR:

```bash
# Quick check
make check-conflicts

# Detailed analysis
./scripts/check_conflicts.sh main -v
```

### Resolving Conflicts

See our comprehensive guide:
- **Documentation:** [docs/CONFLICT_RESOLUTION_GUIDE.md](docs/CONFLICT_RESOLUTION_GUIDE.md)
- **Quick reference:** Common scenarios and solutions
- **Automated tools:** Scripts to help with resolution

**Key principles:**
1. Understand both changes before resolving
2. Test thoroughly after resolution
3. Ask the original author if unsure
4. Document non-obvious resolution choices

### Git Configuration

The repository uses a `.gitattributes` file with smart merge strategies:

- **Union merge** for imports and documentation
- **Ours strategy** for lock files
- **Binary handling** for images

Configure your git client:

```bash
make git-setup
```

This sets up:
- `diff3` conflict style (shows common ancestor)
- `rerere` (remembers conflict resolutions)
- Better diff algorithms
- Language-specific diff drivers

## Code Standards

### Python (Backend & AI)

- **Style:** PEP 8 via `black` and `flake8`
- **Type hints:** Required for all functions
- **Docstrings:** Required for public APIs

```python
def validate_control(
    control: Control,
    framework: str
) -> ValidationResult:
    """Validate control against framework requirements.
    
    Args:
        control: Control model to validate
        framework: Target framework (ECC, CCC, PDPL)
        
    Returns:
        ValidationResult with pass/fail and details
        
    Raises:
        ValidationError: If control is malformed
    """
    pass
```

### JavaScript/TypeScript (Frontend)

- **Style:** ESLint + Prettier
- **Types:** TypeScript strict mode
- **Components:** Functional components with hooks

```typescript
interface ControlCardProps {
  control: Control;
  onSelect: (id: string) => void;
}

export const ControlCard: React.FC<ControlCardProps> = ({
  control,
  onSelect
}) => {
  // Component implementation
};
```

### Bilingual Support

All user-facing text must support both Arabic and English:

**✅ Correct:**
```python
# Model
class Control(Base):
    title_en: str
    title_ar: str
    
# Frontend
{t('controls.title')}
```

**❌ Incorrect:**
```python
# Don't hardcode language
title = "Risk Assessment"
```

### Database Conventions

- Use SQLAlchemy 2.0 async style
- Include bilingual columns (`_en`, `_ar`)
- Add timestamps (`created_at`, `updated_at`)
- Use enums for status fields

```python
class Evidence(Base):
    __tablename__ = "evidence"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title_en: Mapped[str]
    title_ar: Mapped[str]
    status: Mapped[EvidenceStatus]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
```

## Testing

### Backend Tests

- Located in `tests/backend/`
- Use `pytest` with async support
- Minimum 80% coverage for new code

```python
@pytest.mark.asyncio
async def test_create_control(db_session):
    """Test control creation with bilingual fields."""
    control = Control(
        control_id="ECC-GV-1",
        title_en="Risk Assessment",
        title_ar="تقييم المخاطر"
    )
    db_session.add(control)
    await db_session.commit()
    
    assert control.id is not None
```

### Frontend Tests

- Located in `tests/frontend/`
- Use Jest + React Testing Library
- Test both Arabic and English modes

```typescript
describe('ControlCard', () => {
  it('renders bilingual content', () => {
    render(<ControlCard control={mockControl} />);
    
    expect(screen.getByText(mockControl.title_en)).toBeInTheDocument();
    expect(screen.getByText(mockControl.title_ar)).toBeInTheDocument();
  });
});
```

### AI/RAG Tests

- Test retrieval accuracy
- Validate citation tracking
- Test bilingual queries

```python
def test_bilingual_query():
    """Test RAG with Arabic and English queries."""
    result_en = retriever.query("risk assessment")
    result_ar = retriever.query("تقييم المخاطر")
    
    assert result_en.relevance_score > 0.7
    assert result_ar.relevance_score > 0.7
```

## Security

### Before Committing

1. **Never commit secrets:**
   - Use `.env` files (gitignored)
   - Use Azure Key Vault for production
   - Scan with `make security`

2. **Run security checks:**
   ```bash
   make security-deps  # Check dependencies
   make security-sast  # Static analysis
   ```

3. **Follow Phase 2.1 remediation guidelines:**
   - See [docs/compliance/PHASE_2.1_REMEDIATION_PLAN.md](docs/compliance/PHASE_2.1_REMEDIATION_PLAN.md)

### Security Scanning

CI/CD automatically runs:
- CodeQL (semantic analysis)
- Bandit (Python SAST)
- Safety (dependency vulnerabilities)
- npm audit (Node.js vulnerabilities)
- Gitleaks (secret scanning)

Results appear in GitHub Security tab.

## Pull Request Process

### 1. Prepare Your PR

```bash
# Update with latest main
git checkout main
git pull origin main
git checkout your-branch
git rebase main

# Check for conflicts
make check-conflicts

# Run tests
make test

# Run security scans
make security

# Check formatting
make lint
```

### 2. Create the PR

1. Push your branch:
   ```bash
   git push origin your-branch
   ```

2. Open PR on GitHub with:
   - **Clear title:** "Add evidence validation for PDPL compliance"
   - **Description:** What and why
   - **References:** Related issues
   - **Testing:** How you tested
   - **Screenshots:** For UI changes

### PR Template

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Changes Made
- Added feature X
- Fixed bug Y
- Updated documentation Z

## Testing
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed
- [ ] Security scans pass
- [ ] No merge conflicts

## Screenshots (if applicable)
[Attach screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Security review completed
- [ ] Bilingual support verified (if applicable)
```

### 3. PR Review Process

**Reviewers will check:**
- Code quality and standards
- Test coverage
- Security implications
- Merge conflict potential
- Documentation completeness
- Bilingual support (if applicable)

**Response times:**
- Initial review: Within 1 business day
- Follow-up reviews: Within 4 hours

### 4. Addressing Feedback

- Make requested changes in new commits
- Don't force-push (preserves review history)
- Respond to each comment
- Re-request review when ready

### 5. Merging

**Requirements:**
- ✅ All CI checks pass
- ✅ At least one approval
- ✅ No unresolved conflicts
- ✅ No outstanding review comments
- ✅ Branch up-to-date with main

**Merge strategy:**
- Use "Squash and merge" for feature branches
- Use "Rebase and merge" for hotfixes
- Delete branch after merge

## Common Issues

### "My tests pass locally but fail in CI"

- Ensure you're using same versions (see requirements.txt)
- Check environment variables in `.github/workflows/`
- Run `make docker-up && make test` to simulate CI

### "I have merge conflicts"

1. Read [docs/CONFLICT_RESOLUTION_GUIDE.md](docs/CONFLICT_RESOLUTION_GUIDE.md)
2. Run `make check-conflicts` for analysis
3. Ask in PR comments if stuck

### "Security scan is failing"

- Review findings in GitHub Security tab
- Fix critical and high severity issues
- Add justification for false positives
- See [docs/SECURITY_PIPELINE.md](docs/SECURITY_PIPELINE.md)

## Getting Help

- **Documentation:** Check `docs/` directory
- **Issues:** Search existing issues on GitHub
- **Discussions:** Use GitHub Discussions for questions
- **Security:** Email security@example.com for sensitive issues

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors are recognized in:
- Release notes
- CONTRIBUTORS.md file
- GitHub contributors graph

Thank you for contributing! 🎉

---

**Last Updated:** 2026-02-04  
**Questions?** Open an issue or discussion on GitHub
