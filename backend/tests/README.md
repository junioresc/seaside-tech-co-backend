# Testing Guide - DRF Testing Patterns

## Overview

This guide documents standard testing patterns for the Seaside Tech Co Backend API. **All API tests must use Django REST Framework (DRF) patterns** to ensure consistency and proper error handling.

## Quick Reference

- **API Client**: Always use `rest_framework.test.APIClient` (NOT Django's test client)
- **Error Format**: Validate DRF error responses: `{"detail": "message"}` or `{"field": ["error"]}`
- **Store Context**: Use `X-Store-ID` header for multi-tenant endpoints
- **Authentication**: Use `force_authenticate()` for authenticated tests
- **Assertions**: Use `DRFTestMixin` helper methods for consistent assertions

## Test Organization

```
backend/tests/
├── conftest.py              # Shared fixtures and DRFTestMixin
├── factories.py             # Factory Boy factories for test data
├── test_drf_patterns.py     # Example DRF testing patterns (reference)
├── test_health.py           # Health endpoint test
└── test_*.py                # Additional test modules
```

## DRF APIClient Usage

### Basic APIClient

```python
from rest_framework.test import APIClient

def test_endpoint(api_client):
    """Use api_client fixture for unauthenticated requests."""
    response = api_client.get('/api/v1/endpoint/')
    assert response.status_code == 200
```

### Authenticated Requests

```python
def test_protected_endpoint(authenticated_api_client):
    """Use authenticated_api_client fixture for protected endpoints."""
    response = authenticated_api_client.get('/api/v1/repairs/')
    assert response.status_code == 200
```

**Manual Authentication:**

```python
def test_custom_auth(api_client, user):
    """Manually authenticate for custom scenarios."""
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/v1/repairs/')
    assert response.status_code == 200
```

### Store Context Header

**All multi-tenant endpoints require `X-Store-ID` header.**

```python
from tests.conftest import DRFTestMixin

class TestRepairs(DRFTestMixin):
    def test_list_repairs(self, authenticated_api_client):
        store = StoreFactory()
        
        # Use helper method to include store context
        response = self.get_with_store(
            authenticated_api_client,
            '/api/v1/repairs/',
            store.id
        )
        assert response.status_code == 200
```

**Available Helper Methods:**
- `get_with_store(client, url, store_id, **kwargs)`
- `post_with_store(client, url, store_id, data=None, **kwargs)`
- `put_with_store(client, url, store_id, data=None, **kwargs)`
- `patch_with_store(client, url, store_id, data=None, **kwargs)`
- `delete_with_store(client, url, store_id, **kwargs)`

### JSON Requests

**APIClient handles JSON automatically with `format='json'`.**

```python
def test_create_repair(authenticated_api_client):
    store = StoreFactory()
    
    data = {
        "device_type": "laptop",
        "issue_description": "Screen cracked",
        "customer_name": "John Doe"
    }
    
    response = self.post_with_store(
        authenticated_api_client,
        '/api/v1/repairs/',
        store.id,
        data=data  # Automatically serialized to JSON
    )
    
    assert response.status_code == 201
    assert response.data["device_type"] == "laptop"  # Automatically deserialized
```

## DRF Error Format Validation

**All API endpoints must return errors in DRF standard format.**

### 404 Not Found

```python
def test_404_error(api_client):
    response = api_client.get('/api/v1/repairs/invalid-uuid/')
    
    assert response.status_code == 404
    assert "detail" in response.data
    assert response.data["detail"] == "Not found."
```

### Validation Errors (400)

```python
def test_validation_error(authenticated_api_client):
    store = StoreFactory()
    
    # Missing required fields
    response = self.post_with_store(
        authenticated_api_client,
        '/api/v1/repairs/',
        store.id,
        data={}
    )
    
    assert response.status_code == 400
    # Field errors are lists
    assert "device_type" in response.data
    assert isinstance(response.data["device_type"], list)
```

### Authentication Errors (401/403)

```python
def test_auth_required(api_client):
    response = api_client.get('/api/v1/repairs/')
    
    assert response.status_code in [401, 403]
    assert "detail" in response.data
```

## Assertion Helpers

**Use `DRFTestMixin` for consistent assertions.**

### assert_drf_error()

```python
class TestMyAPI(DRFTestMixin):
    def test_error_response(self, api_client):
        response = api_client.get('/api/v1/invalid/')
        
        # Assert error with expected status
        self.assert_drf_error(response, 404)
```

### assert_validation_error()

```python
class TestMyAPI(DRFTestMixin):
    def test_invalid_data(self, authenticated_api_client):
        store = StoreFactory()
        
        response = self.post_with_store(
            authenticated_api_client,
            '/api/v1/repairs/',
            store.id,
            data={"device_type": ""}  # Invalid
        )
        
        # Assert validation error on specific field
        self.assert_validation_error(response, field_name="device_type")
```

## Test Data Factories

**Use Factory Boy for test data generation.**

```python
from tests.factories import OrganizationFactory, StoreFactory

def test_with_factories():
    # Create test organization and store
    org = OrganizationFactory(name="Test Org")
    store = StoreFactory(organization=org, name="Test Store")
    
    # Use in tests
    assert store.organization == org
```

**Adding New Factories:**

```python
# tests/factories.py
import factory
from apps.repairs.models import RepairOrder

class RepairOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RepairOrder
    
    store = factory.SubFactory(StoreFactory)
    device_type = factory.Faker("word")
    issue_description = factory.Faker("sentence")
```

## Test Fixtures

### Available Fixtures (conftest.py)

- **`api_client`**: Unauthenticated APIClient
- **`authenticated_api_client`**: Pre-authenticated APIClient
- **`user`**: Test user instance
- **`db`**: Database access (auto-enabled for all tests)

### Custom Fixtures

```python
# conftest.py
@pytest.fixture
def repair_order(authenticated_api_client):
    """Create a repair order for testing."""
    store = StoreFactory()
    return RepairOrderFactory(store=store)
```

## Testing Standards

### Test Pyramid

- **80% Unit Tests**: Model validation, business logic, serializers, utilities
- **15% Integration Tests**: API endpoints, database operations, service integrations
- **5% E2E Tests**: Complete workflows

### Coverage Requirements

- **Minimum**: 80% overall code coverage
- **Critical**: 90%+ for multi-tenancy, auth, payments

### Test Naming

```python
def test_<action>_<expected_result>():
    """
    Pattern: test_action_expectedResult
    Examples:
    - test_create_repair_success()
    - test_list_repairs_requires_auth()
    - test_update_repair_validates_status()
    """
    pass
```

### Test Structure (AAA Pattern)

```python
def test_example():
    # Arrange: Set up test data
    store = StoreFactory()
    user = UserFactory()
    
    # Act: Perform action
    response = api_client.get('/api/v1/repairs/')
    
    # Assert: Verify results
    assert response.status_code == 200
    assert len(response.data) == 0
```

## Running Tests

### Run All Tests

```bash
pytest backend/tests/
```

### Run with Coverage

```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

### Run Specific Test

```bash
pytest backend/tests/test_repairs.py::test_create_repair
```

### Run Tests by Marker

```bash
# Integration tests only
pytest -m integration

# Unit tests only
pytest -m "not integration"
```

## Common Patterns

### Testing Multi-Tenancy

```python
class TestStoreIsolation(DRFTestMixin):
    def test_store_isolation(self, authenticated_api_client):
        store_a = StoreFactory()
        store_b = StoreFactory()
        
        # Create repair in store A
        repair = RepairOrderFactory(store=store_a)
        
        # Request from store B should not see store A data
        response = self.get_with_store(
            authenticated_api_client,
            f'/api/v1/repairs/{repair.id}/',
            store_b.id
        )
        
        # Should return 404 (not found in store B context)
        assert response.status_code == 404
```

### Testing Permissions

```python
def test_permission_required(api_client):
    # Unauthenticated request
    response = api_client.get('/api/v1/repairs/')
    assert response.status_code in [401, 403]
    
    # Authenticated request
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/v1/repairs/')
    assert response.status_code == 200
```

### Testing Validation

```python
def test_field_validation(authenticated_api_client):
    store = StoreFactory()
    
    # Invalid data
    response = self.post_with_store(
        authenticated_api_client,
        '/api/v1/repairs/',
        store.id,
        data={"device_type": "", "issue_description": ""}
    )
    
    assert response.status_code == 400
    assert "device_type" in response.data
    assert "issue_description" in response.data
```

### Testing Status Codes

```python
def test_crud_operations(authenticated_api_client):
    store = StoreFactory()
    
    # Create: 201
    response = self.post_with_store(authenticated_api_client, url, store.id, data={...})
    assert response.status_code == 201
    
    # Read: 200
    response = self.get_with_store(authenticated_api_client, url, store.id)
    assert response.status_code == 200
    
    # Update: 200
    response = self.put_with_store(authenticated_api_client, url, store.id, data={...})
    assert response.status_code == 200
    
    # Delete: 204
    response = self.delete_with_store(authenticated_api_client, url, store.id)
    assert response.status_code == 204
```

## Best Practices

1. **Always use APIClient** for API tests (not Django test client)
2. **Validate DRF error format** in all error cases
3. **Use factory patterns** for test data (not fixtures with hard-coded data)
4. **Test store isolation** for all multi-tenant endpoints
5. **Use helper methods** from DRFTestMixin for consistency
6. **Follow AAA pattern** (Arrange, Act, Assert)
7. **Keep tests focused** - one assertion concept per test
8. **Use descriptive test names** - explain what is being tested
9. **Mark integration tests** with `@pytest.mark.integration`
10. **Mock external services** (Stripe, AWS) in tests

## Examples

See `test_drf_patterns.py` for complete working examples of all patterns documented here.

## CI/CD Integration

Tests run automatically in GitHub Actions CI pipeline:

- **Service Containers**: PostgreSQL 16, Redis 7
- **Coverage Requirement**: 80% minimum
- **Test Execution**: `pytest tests/ --cov=backend --cov-report=xml --cov-fail-under=80`
- **Artifacts**: Coverage reports uploaded for PR review

---

**Last Updated**: 2025-12-03  
**For Questions**: See `test_drf_patterns.py` or contact development team

