import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def _enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_client():
    """
    DRF APIClient fixture for API tests.
    Use this instead of Django's test client for REST API testing.
    """
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """
    Pre-authenticated APIClient for testing protected endpoints.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user(django_user_model):
    """
    Test user fixture.
    """
    return django_user_model.objects.create_user(
        username="testuser", email="testuser@example.com", password="testpass123"
    )


class DRFTestMixin:
    """
    Mixin for DRF API tests providing helper methods for common patterns.

    Usage:
        class TestMyAPI(DRFTestMixin):
            def test_endpoint(self, api_client):
                response = self.get_with_store(api_client, '/api/v1/repairs/', store_id)
                self.assert_drf_error(response, 404)
    """

    def get_with_store(self, client, url, store_id, **kwargs):
        """Make GET request with store context header."""
        return client.get(url, HTTP_X_STORE_ID=str(store_id), **kwargs)

    def post_with_store(self, client, url, store_id, data=None, **kwargs):
        """Make POST request with store context header."""
        return client.post(url, data=data, HTTP_X_STORE_ID=str(store_id), format="json", **kwargs)

    def put_with_store(self, client, url, store_id, data=None, **kwargs):
        """Make PUT request with store context header."""
        return client.put(url, data=data, HTTP_X_STORE_ID=str(store_id), format="json", **kwargs)

    def patch_with_store(self, client, url, store_id, data=None, **kwargs):
        """Make PATCH request with store context header."""
        return client.patch(url, data=data, HTTP_X_STORE_ID=str(store_id), format="json", **kwargs)

    def delete_with_store(self, client, url, store_id, **kwargs):
        """Make DELETE request with store context header."""
        return client.delete(url, HTTP_X_STORE_ID=str(store_id), **kwargs)

    def assert_drf_error(self, response, expected_status=400):
        """
        Assert response is a DRF error with expected status.
        Validates DRF error format: {"detail": "message"} or {"field": ["error"]}
        """
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.data}"
        )
        # DRF errors have either "detail" key or field-specific errors
        assert "detail" in response.data or any(
            isinstance(v, list) for v in response.data.values()
        ), f"Response doesn't match DRF error format: {response.data}"

    def assert_validation_error(self, response, field_name=None):
        """
        Assert response is a validation error (400).
        If field_name provided, assert that specific field has errors.
        """
        assert (
            response.status_code == 400
        ), f"Expected validation error (400), got {response.status_code}"
        if field_name:
            assert field_name in response.data, (
                f"Expected field '{field_name}' in validation errors. "
                f"Got: {list(response.data.keys())}"
            )
