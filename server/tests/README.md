# Authentication Tests

This directory contains comprehensive tests for the authentication routes of the Study Assistant API.

## Test Structure

```
tests/
├── __init__.py           # Package initialization
├── conftest.py          # Pytest fixtures and configuration
├── test_auth.py         # Authentication route tests
└── README.md            # This file
```

## Test Coverage

### Authentication Routes Tested

1. **Auth Welcome** (`GET /auth/`)
   - Basic endpoint availability

2. **User Registration** (`POST /auth/register`)
   - Successful registration
   - Duplicate email/username handling
   - Invalid email format
   - Missing required fields
   - Empty password validation

3. **User Login** (`POST /auth/login`)
   - Successful login with valid credentials
   - Failed login with wrong password
   - Failed login with non-existent email
   - Missing credentials handling
   - Cookie setting verification

4. **Get Current User** (`GET /auth/me`)
   - Authenticated user access
   - Unauthenticated access denial
   - Invalid token handling

5. **User Logout** (`POST /auth/logout`)
   - Successful logout
   - Cookie clearing
   - Logout when not authenticated

6. **Integration Tests**
   - Complete authentication flow
   - Multiple user registration
   - Concurrent logins
   - Password security verification

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-cov httpx
```

### Run All Tests

```bash
# From the server directory
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test Classes

```bash
# Run only registration tests
pytest tests/test_auth.py::TestUserRegistration

# Run only login tests
pytest tests/test_auth.py::TestUserLogin

# Run only integration tests
pytest tests/test_auth.py::TestAuthenticationFlow
```

### Run Specific Test Functions

```bash
# Run a specific test
pytest tests/test_auth.py::TestUserRegistration::test_register_new_user_success

# Run tests matching a pattern
pytest -k "login"
```

### Run with Different Output Formats

```bash
# Short output
pytest --tb=short

# Detailed output
pytest --tb=long

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

## Test Fixtures

### Available Fixtures (from conftest.py)

- `db_session`: Fresh database session for each test
- `client`: Test client with database override
- `test_user_data`: Sample user data for testing
- `test_user_data_2`: Second sample user data
- `registered_user`: Pre-registered user
- `authenticated_client`: Client with authenticated session

### Using Fixtures

```python
def test_example(client, test_user_data):
    """Example test using fixtures."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
```

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test
- Automatically cleaned up after each test
- Isolated from the production database

## Writing New Tests

### Test Class Structure

```python
class TestFeatureName:
    """Tests for feature description."""
    
    def test_specific_behavior(self, client):
        """Test description."""
        # Arrange
        data = {"key": "value"}
        
        # Act
        response = client.post("/endpoint", json=data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["key"] == "value"
```

### Best Practices

1. **Use descriptive test names**: `test_login_fails_with_wrong_password`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test one thing per test**: Keep tests focused
4. **Use fixtures**: Reuse common setup code
5. **Test edge cases**: Invalid inputs, missing data, etc.
6. **Test security**: Password hashing, token validation, etc.

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd server
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest --cov=app --cov-report=xml
```

## Test Results

After running tests, you'll see output like:

```
tests/test_auth.py::TestUserRegistration::test_register_new_user_success PASSED
tests/test_auth.py::TestUserLogin::test_login_success PASSED
tests/test_auth.py::TestGetCurrentUser::test_get_current_user_authenticated PASSED
...

======================== 25 passed in 2.34s ========================
```

## Coverage Report

Generate HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

View the report by opening `htmlcov/index.html` in your browser.

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the server directory
2. **Database errors**: Check that SQLAlchemy models are properly defined
3. **Fixture errors**: Verify conftest.py is in the tests directory
4. **Module not found**: Install missing dependencies

### Debug Mode

Run tests with debugging:

```bash
# Show print statements and detailed errors
pytest -vv -s

# Drop into debugger on failure
pytest --pdb
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [TestClient Documentation](https://www.starlette.io/testclient/)
