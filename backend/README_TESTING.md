# Testing و Quality Assurance

راهنمای کامل Testing و Quality Assurance

## Overview

سیستم Testing شامل:
- **Unit Tests**: تست‌های unit برای services و utilities
- **Integration Tests**: تست‌های integration برای API endpoints
- **Frontend Tests**: تست‌های React components
- **Code Quality**: Linting, formatting, type checking
- **CI/CD**: Automated testing در CI/CD pipeline

## Backend Testing

### Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_auth.py          # Authentication tests
│   ├── test_wells.py         # Wells API tests
│   ├── test_sensors.py       # Sensors API tests
│   ├── test_security.py      # Security utilities tests
│   ├── test_services.py      # Service layer tests
│   ├── test_monitoring.py    # Monitoring tests
│   └── test_utils.py          # Test utilities
```

### Running Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with markers
pytest -m unit
pytest -m integration
```

### Test Fixtures

Fixtures در `conftest.py` تعریف شده‌اند:

- `db`: Test database session
- `client`: FastAPI test client
- `test_user`: Test user fixture
- `test_admin_user`: Admin user fixture
- `auth_headers`: Authentication headers
- `admin_auth_headers`: Admin authentication headers
- `test_well`: Test well fixture
- `test_sensor`: Test sensor fixture
- `fake_well_data`: Fake well data generator
- `fake_sensor_data`: Fake sensor data generator

### Example Test

```python
def test_create_well(client, auth_headers, fake_well_data):
    """Test creating a well"""
    response = client.post(
        "/api/v1/wells",
        json=fake_well_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == fake_well_data["name"]
```

### Test Coverage

هدف coverage: **70%**

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Frontend Testing

### Test Structure

```
frontend/
├── src/
│   ├── __tests__/
│   │   ├── components/
│   │   │   └── StatCard.test.tsx
│   │   └── lib/
│   │       └── api.test.ts
```

### Running Tests

```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- StatCard.test.tsx
```

### Testing Library

استفاده از:
- **Jest**: Test runner
- **React Testing Library**: Component testing
- **@testing-library/jest-dom**: DOM matchers

### Example Test

```typescript
import { render, screen } from '@testing-library/react'
import StatCard from '@/components/ui/StatCard'

describe('StatCard', () => {
  it('renders with title and value', () => {
    render(<StatCard title="Test Title" value="100" />)
    
    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })
})
```

## Code Quality

### Backend

#### Black (Code Formatting)

```bash
# Format code
black .

# Check formatting
black --check .
```

#### isort (Import Sorting)

```bash
# Sort imports
isort .

# Check import order
isort --check-only .
```

#### Flake8 (Linting)

```bash
# Run linter
flake8 .

# Run with specific rules
flake8 . --select=E9,F63,F7,F82
```

#### MyPy (Type Checking)

```bash
# Type check
mypy app/
```

### Frontend

#### ESLint

```bash
# Run linter
npm run lint

# Fix issues
npm run lint -- --fix
```

#### TypeScript

```bash
# Type check
npx tsc --noEmit
```

## Test Markers

استفاده از pytest markers برای categorizing tests:

```python
@pytest.mark.unit
def test_password_hashing():
    ...

@pytest.mark.integration
def test_api_endpoint():
    ...

@pytest.mark.slow
def test_heavy_computation():
    ...
```

## CI/CD Integration

### GitHub Actions

Workflow در `.github/workflows/test.yml`:

1. **Backend Tests**:
   - Setup PostgreSQL و Redis
   - Install dependencies
   - Run linters
   - Run tests with coverage
   - Upload coverage

2. **Frontend Tests**:
   - Setup Node.js
   - Install dependencies
   - Run linters
   - Run tests with coverage
   - Upload coverage

### Running Locally

```bash
# Run all quality checks
make lint
make test

# Or individually
cd backend && flake8 . && black --check . && pytest
cd frontend && npm run lint && npm test
```

## Best Practices

### 1. Test Organization

- Group related tests together
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Data

- Use fixtures for common data
- Use factories for generating test data
- Clean up after tests

### 3. Test Coverage

- Aim for 70%+ coverage
- Focus on critical paths
- Test edge cases

### 4. Test Speed

- Use markers for slow tests
- Mock external dependencies
- Use in-memory database for tests

### 5. Test Maintenance

- Keep tests up to date
- Refactor tests when code changes
- Remove obsolete tests

## Test Utilities

### Backend

```python
from tests.test_utils import (
    assert_response_success,
    assert_response_error,
    assert_pagination,
    assert_well_structure,
    assert_sensor_structure
)
```

### Frontend

```typescript
// Mock API responses
jest.mock('@/lib/api', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  }
}))
```

## Continuous Integration

### Pre-commit Hooks

برای اجرای tests قبل از commit:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### Pre-commit Config

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
```

## Performance Testing

برای performance testing:

```python
import time

def test_api_performance(client, auth_headers):
    start = time.time()
    response = client.get("/api/v1/wells", headers=auth_headers)
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 1.0  # Should respond in < 1 second
```

## Security Testing

برای security testing:

```python
def test_sql_injection_protection(client, auth_headers):
    # Attempt SQL injection
    response = client.get(
        "/api/v1/wells",
        params={"well_id": "'; DROP TABLE wells; --"},
        headers=auth_headers
    )
    # Should not cause database error
    assert response.status_code in [200, 400, 404]
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [Jest Documentation](https://jestjs.io/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)

