"""
DRF Testing Pattern Examples

This test module demonstrates standard DRF testing patterns
for all API endpoints in this project.

NOTE: Most tests are marked as examples (skip) because endpoints don't exist yet.
These serve as reference documentation for future story implementations.
"""

import pytest
from rest_framework import status

from tests.conftest import DRFTestMixin
from tests.factories import StoreFactory


@pytest.mark.skip(reason="Example tests - endpoints don't exist yet")
class TestDRFErrorFormats(DRFTestMixin):
    """
    Test examples demonstrating DRF error response format validation.
    All API endpoints must return errors in DRF standard format.
    """

    def test_404_error_format(self, api_client):
        """404 errors return DRF format: {"detail": "..."}"""
        response = api_client.get("/api/v1/repairs/99999999-9999-9999-9999-999999999999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.data

    def test_validation_error_format(self, authenticated_api_client):
        """
        Validation errors return field-specific errors:
        {"field_name": ["Error message"]}
        """
        store = StoreFactory()

        # Missing required fields
        response = self.post_with_store(
            authenticated_api_client,
            "/api/v1/repairs/",
            store.id,  # type: ignore[attr-defined]
            data={},  # Missing required fields
        )

        # Should return 400 with field errors
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Field errors are lists
        for field, errors in response.data.items():
            assert isinstance(errors, list), f"Field '{field}' errors should be a list"
            assert len(errors) > 0, f"Field '{field}' should have error messages"

    def test_authentication_error_format(self, api_client):
        """Authentication errors return DRF format with detail."""
        store = StoreFactory()

        # Unauthenticated request to protected endpoint
        response = self.get_with_store(
            api_client, "/api/v1/repairs/", store.id  # type: ignore[attr-defined]
        )

        # Should return 401 or 403 with detail
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        assert "detail" in response.data


@pytest.mark.skip(reason="Example tests - endpoints don't exist yet")
class TestDRFAPIClientUsage(DRFTestMixin):
    """
    Test examples demonstrating APIClient usage patterns.
    Always use rest_framework.test.APIClient for API tests.
    """

    def test_authenticated_request_pattern(self, authenticated_api_client):
        """
        Pattern: Use authenticated_api_client fixture for protected endpoints.
        """
        store = StoreFactory()

        # authenticated_api_client has user pre-authenticated
        response = self.get_with_store(
            authenticated_api_client, "/api/v1/repairs/", store.id  # type: ignore[attr-defined]
        )

        # Should succeed (assuming user has permission)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_store_context_header_pattern(self, authenticated_api_client):
        """
        Pattern: Use X-Store-ID header for all requests requiring store context.
        Use helper methods: get_with_store, post_with_store, etc.
        """
        store = StoreFactory()

        # Use helper method to include store context
        response = self.get_with_store(
            authenticated_api_client, "/api/v1/repairs/", store.id  # type: ignore[attr-defined]
        )

        # Store context should be applied
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_json_request_pattern(self, authenticated_api_client):
        """
        Pattern: APIClient automatically handles JSON serialization with format='json'.
        Helper methods include format='json' by default.
        """
        store = StoreFactory()

        # Data is automatically serialized to JSON
        response = self.post_with_store(
            authenticated_api_client,
            "/api/v1/repairs/",
            store.id,  # type: ignore[attr-defined]
            data={"device_type": "laptop", "issue_description": "Test"},
        )

        # Response data is automatically deserialized
        assert isinstance(response.data, dict)


class TestDRFAssertionHelpers(DRFTestMixin):
    """
    Test examples demonstrating assertion helper usage.
    """

    @pytest.mark.skip(reason="Example test - endpoint doesn't exist yet")
    def test_assert_drf_error_helper(self, api_client):
        """
        Pattern: Use assert_drf_error() to validate error responses.
        """
        response = api_client.get("/api/v1/repairs/invalid-uuid/")

        # Assert 404 with DRF error format
        self.assert_drf_error(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.skip(reason="Example test - endpoint doesn't exist yet")
    def test_assert_validation_error_helper(self, authenticated_api_client):
        """
        Pattern: Use assert_validation_error() for validation failures.
        """
        store = StoreFactory()

        response = self.post_with_store(
            authenticated_api_client,
            "/api/v1/repairs/",
            store.id,  # type: ignore[attr-defined]
            data={"device_type": ""},  # Invalid: empty required field
        )

        # Assert validation error on specific field
        self.assert_validation_error(response, field_name="device_type")


class TestHealthEndpoint:
    """
    Real working test demonstrating DRF APIClient usage.
    """

    def test_health_check_with_api_client(self, api_client):
        """Health endpoint works with APIClient."""
        response = api_client.get("/health/")

        assert response.status_code == status.HTTP_200_OK
        # Health endpoint returns JsonResponse, not DRF Response
        # In real DRF endpoints, use response.data
        assert response.json()["status"] == "ok"
