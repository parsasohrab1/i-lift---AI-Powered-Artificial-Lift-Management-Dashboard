# Contributing Guide

از مشارکت شما در IntelliLift AI Dashboard استقبال می‌کنیم!

## Code of Conduct

لطفاً قوانین و اصول اخلاقی پروژه را رعایت کنید.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/i-lift-dashboard.git
cd i-lift-dashboard
```

### 2. Set Up Development Environment

```bash
# Install dependencies
npm run install:all

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### 1. Make Changes

- Write clean, readable code
- Follow coding standards
- Add tests for new features
- Update documentation

### 2. Test Your Changes

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Linting
npm run lint
```

### 3. Commit Your Changes

```bash
git add .
git commit -m "Add: description of changes"
```

**Commit Message Format:**

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `Add`: New feature
- `Fix`: Bug fix
- `Update`: Update existing feature
- `Remove`: Remove feature
- `Docs`: Documentation changes
- `Style`: Code style changes
- `Refactor`: Code refactoring
- `Test`: Test changes
- `Chore`: Maintenance tasks

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

سپس Pull Request را در GitHub ایجاد کنید.

## Coding Standards

### Python (Backend)

- Follow PEP 8
- Use type hints
- Write docstrings
- Maximum line length: 100 characters

```python
def calculate_kpi(well_id: str, hours: int = 24) -> Dict[str, Any]:
    """
    Calculate KPIs for a well.
    
    Args:
        well_id: The well identifier
        hours: Number of hours to look back
        
    Returns:
        Dictionary containing KPI values
    """
    ...
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow ESLint rules
- Use functional components
- Maximum line length: 100 characters

```typescript
interface Well {
  wellId: string;
  name: string;
  location: string;
}

const WellCard: React.FC<{ well: Well }> = ({ well }) => {
  return <div>{well.name}</div>;
};
```

## Testing

### Backend Tests

- Write unit tests for services
- Write integration tests for API endpoints
- Aim for 70%+ coverage
- Use pytest fixtures

```python
def test_create_well(client, auth_headers, fake_well_data):
    """Test creating a well"""
    response = client.post(
        "/api/v1/wells",
        json=fake_well_data,
        headers=auth_headers
    )
    assert response.status_code == 201
```

### Frontend Tests

- Test components with React Testing Library
- Test user interactions
- Mock API calls

```typescript
it('renders well card', () => {
  render(<WellCard well={mockWell} />);
  expect(screen.getByText('Well 1')).toBeInTheDocument();
});
```

## Documentation

### Code Documentation

- Write clear docstrings
- Document complex logic
- Add inline comments where needed

### API Documentation

- Update API documentation for new endpoints
- Add examples
- Document request/response formats

### User Documentation

- Update user guide for new features
- Add screenshots for UI changes
- Update setup guide if needed

## Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages follow format

### 2. PR Description

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test the changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guide
```

### 3. Review Process

- Maintainers will review your PR
- Address any feedback
- Once approved, PR will be merged

## Issue Reporting

### Bug Reports

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]
```

### Feature Requests

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why this feature is needed

**Proposed Solution**
How you think it should work

**Alternatives**
Other solutions considered
```

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and discussions
- **Email**: support@example.com

## Recognition

Contributors will be recognized in:
- README.md
- Release notes
- Project documentation

Thank you for contributing! 🎉

