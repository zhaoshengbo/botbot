# Testing Guide

This document provides a comprehensive guide for running and writing tests in the BotBot project.

## Quick Start

### Backend Tests (pytest)

```bash
cd be

# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Frontend Tests (Jest)

```bash
cd fe

# Install test dependencies
npm install

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
open coverage/lcov-report/index.html  # View coverage report
```

## Test Structure

### Backend (`be/tests/`)

```
tests/
├── conftest.py                 # Shared fixtures and test configuration
├── test_security.py           # Security function unit tests
├── test_auth_service.py       # Auth service unit tests
├── test_api_auth.py           # Auth API integration tests
├── test_api_tasks.py          # Tasks API integration tests
├── test_api_bids.py           # Bids API integration tests
└── test_api_ai.py             # AI API integration tests
```

**Key Fixtures (from conftest.py):**
- `test_db` - Clean test database for each test
- `test_user` - Pre-created test user
- `test_admin` - Pre-created admin user
- `auth_token` - Valid JWT token for test user
- `admin_token` - Valid JWT token for admin
- `auth_headers` - Authorization headers with token
- `test_task` - Pre-created test task
- `test_bid` - Pre-created test bid

### Frontend (`fe/src/`)

```
src/
├── components/__tests__/
│   └── Navbar.test.tsx        # Navbar component tests
├── lib/__tests__/
│   └── api.test.ts            # API client tests
└── app/auth/login/__tests__/
    └── page.test.tsx          # Login page tests
```

## Running Specific Tests

### Backend

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run specific test file
pytest tests/test_security.py

# Run specific test class
pytest tests/test_auth_service.py::TestAuthService

# Run specific test function
pytest tests/test_security.py::TestSecurity::test_password_hashing

# Run tests matching pattern
pytest -k "password"

# Show print statements
pytest -v -s
```

### Frontend

```bash
# Run specific test file
npm test -- Navbar.test.tsx

# Run tests matching pattern
npm test -- --testNamePattern="login"

# Update snapshots
npm test -- -u

# Run in debug mode
node --inspect-brk node_modules/.bin/jest --runInBand
```

## Test Coverage

### Current Coverage

**Backend:**
- ✅ Security functions (JWT, password hashing)
- ✅ Authentication service (SMS, verification, login)
- ✅ Auth API endpoints (send code, verify, login, me)
- ✅ Tasks API endpoints (create, read, update, list, cancel)
- ✅ Bids API endpoints (create, list, accept, withdraw)
- ✅ AI API endpoints (analyze, balance, auto-bid, preferences)

**Frontend:**
- ✅ Navbar component (authenticated/unauthenticated states)
- ✅ API client (token management, error handling)
- ✅ Login page (form submission, validation, error handling)

### Coverage Goals

- Backend: Aim for 80%+ coverage on core business logic
- Frontend: Aim for 70%+ coverage on components and pages
- Critical paths (auth, payments, AI) should have 90%+ coverage

## Writing New Tests

### Backend Test Example

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_task(client, auth_headers):
    """Test creating a new task"""
    task_data = {
        "title": "Test Task",
        "description": "Description",
        "budget": 50.0,
    }

    response = await client.post(
        "/api/tasks",
        json=task_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
```

### Frontend Test Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = jest.fn()
    render(<MyComponent onClick={handleClick} />)

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

## Test Database

Backend tests use a separate test database (`botbot_test`) configured in `.env.test`.

**Important:**
- Test database is automatically cleaned before and after each test
- Never use production database credentials in tests
- Test data is isolated per test function

## Mocking External Services

### Backend Mocking

```python
# Mock AI service
with patch('app.services.ai_service.AIService.analyze_task') as mock:
    mock.return_value = {"feasibility_score": 0.85}
    # Test code here

# Mock SMS service
with patch('app.services.auth_service.SMSService') as mock_sms:
    mock_sms_instance = AsyncMock()
    mock_sms_instance.send_verification_code.return_value = True
    mock_sms.return_value = mock_sms_instance
    # Test code here
```

### Frontend Mocking

```typescript
// Mock API client
jest.mock('@/lib/api', () => ({
  apiClient: {
    getCurrentUser: jest.fn(),
  },
}))

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))
```

## Continuous Integration

Tests should be run in CI/CD pipeline:

```bash
# Backend CI
cd be && pytest --cov=app --cov-fail-under=70

# Frontend CI
cd fe && npm test -- --coverage --watchAll=false
```

## Troubleshooting

### Common Issues

1. **MongoDB connection error in tests**
   - Ensure MongoDB is running: `docker-compose up -d mongodb`
   - Check `.env.test` has correct MONGODB_URL

2. **Frontend tests failing with module not found**
   - Run `npm install` to ensure all dependencies are installed
   - Check `jest.config.js` moduleNameMapper is correct

3. **Async test timeouts**
   - Increase timeout: `pytest --timeout=60`
   - Check for unresolved promises in async tests

4. **Import errors**
   - Backend: Ensure PYTHONPATH includes project root
   - Frontend: Check tsconfig.json paths configuration

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External**: Always mock external services (AI, SMS, payments)
5. **Test Edge Cases**: Don't just test happy paths
6. **Keep Tests Fast**: Mock database operations when possible
7. **One Assertion Per Test**: Focus on testing one thing at a time
8. **Clean Up**: Use fixtures to ensure cleanup after tests

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Jest documentation](https://jestjs.io/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Next.js testing guide](https://nextjs.org/docs/app/building-your-application/testing)
