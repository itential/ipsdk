# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from enum import Enum

import pytest

from ipsdk import enums


class TestHTTPStatus:
    """Test cases for the HTTPStatus enumeration."""

    def test_http_status_is_enum(self):
        """Test that HTTPStatus is an Enum class."""
        assert issubclass(enums.HTTPStatus, Enum)

    def test_informational_status_codes(self):
        """Test 1xx informational status codes."""
        assert enums.HTTPStatus.CONTINUE.value == 100
        assert enums.HTTPStatus.SWITCHING_PROTOCOLS.value == 101
        assert enums.HTTPStatus.PROCESSING.value == 102
        assert enums.HTTPStatus.EARLY_HINTS.value == 103

    def test_success_status_codes(self):
        """Test 2xx success status codes."""
        assert enums.HTTPStatus.OK.value == 200
        assert enums.HTTPStatus.CREATED.value == 201
        assert enums.HTTPStatus.ACCEPTED.value == 202
        assert enums.HTTPStatus.NON_AUTHORITATIVE_INFORMATION.value == 203
        assert enums.HTTPStatus.NO_CONTENT.value == 204
        assert enums.HTTPStatus.RESET_CONTENT.value == 205
        assert enums.HTTPStatus.PARTIAL_CONTENT.value == 206
        assert enums.HTTPStatus.MULTI_STATUS.value == 207
        assert enums.HTTPStatus.ALREADY_REPORTED.value == 208
        assert enums.HTTPStatus.IM_USED.value == 226

    def test_redirection_status_codes(self):
        """Test 3xx redirection status codes."""
        assert enums.HTTPStatus.MULTIPLE_CHOICES.value == 300
        assert enums.HTTPStatus.MOVED_PERMANENTLY.value == 301
        assert enums.HTTPStatus.FOUND.value == 302
        assert enums.HTTPStatus.SEE_OTHER.value == 303
        assert enums.HTTPStatus.NOT_MODIFIED.value == 304
        assert enums.HTTPStatus.USE_PROXY.value == 305
        assert enums.HTTPStatus.TEMPORARY_REDIRECT.value == 307
        assert enums.HTTPStatus.PERMANENT_REDIRECT.value == 308

    def test_client_error_status_codes(self):
        """Test 4xx client error status codes."""
        assert enums.HTTPStatus.BAD_REQUEST.value == 400
        assert enums.HTTPStatus.UNAUTHORIZED.value == 401
        assert enums.HTTPStatus.PAYMENT_REQUIRED.value == 402
        assert enums.HTTPStatus.FORBIDDEN.value == 403
        assert enums.HTTPStatus.NOT_FOUND.value == 404
        assert enums.HTTPStatus.METHOD_NOT_ALLOWED.value == 405
        assert enums.HTTPStatus.NOT_ACCEPTABLE.value == 406
        assert enums.HTTPStatus.PROXY_AUTHENTICATION_REQUIRED.value == 407
        assert enums.HTTPStatus.REQUEST_TIMEOUT.value == 408
        assert enums.HTTPStatus.CONFLICT.value == 409
        assert enums.HTTPStatus.GONE.value == 410
        assert enums.HTTPStatus.LENGTH_REQUIRED.value == 411
        assert enums.HTTPStatus.PRECONDITION_FAILED.value == 412
        assert enums.HTTPStatus.PAYLOAD_TOO_LARGE.value == 413
        assert enums.HTTPStatus.URI_TOO_LONG.value == 414
        assert enums.HTTPStatus.UNSUPPORTED_MEDIA_TYPE.value == 415
        assert enums.HTTPStatus.RANGE_NOT_SATISFIABLE.value == 416
        assert enums.HTTPStatus.EXPECTATION_FAILED.value == 417
        assert enums.HTTPStatus.IM_A_TEAPOT.value == 418
        assert enums.HTTPStatus.MISDIRECTED_REQUEST.value == 421
        assert enums.HTTPStatus.UNPROCESSABLE_ENTITY.value == 422
        assert enums.HTTPStatus.LOCKED.value == 423
        assert enums.HTTPStatus.FAILED_DEPENDENCY.value == 424
        assert enums.HTTPStatus.TOO_EARLY.value == 425
        assert enums.HTTPStatus.UPGRADE_REQUIRED.value == 426
        assert enums.HTTPStatus.PRECONDITION_REQUIRED.value == 428
        assert enums.HTTPStatus.TOO_MANY_REQUESTS.value == 429
        assert enums.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE.value == 431
        assert enums.HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS.value == 451

    def test_server_error_status_codes(self):
        """Test 5xx server error status codes."""
        assert enums.HTTPStatus.INTERNAL_SERVER_ERROR.value == 500
        assert enums.HTTPStatus.NOT_IMPLEMENTED.value == 501
        assert enums.HTTPStatus.BAD_GATEWAY.value == 502
        assert enums.HTTPStatus.SERVICE_UNAVAILABLE.value == 503
        assert enums.HTTPStatus.GATEWAY_TIMEOUT.value == 504
        assert enums.HTTPStatus.HTTP_VERSION_NOT_SUPPORTED.value == 505
        assert enums.HTTPStatus.VARIANT_ALSO_NEGOTIATES.value == 506
        assert enums.HTTPStatus.INSUFFICIENT_STORAGE.value == 507
        assert enums.HTTPStatus.LOOP_DETECTED.value == 508
        assert enums.HTTPStatus.NOT_EXTENDED.value == 510
        assert enums.HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED.value == 511

    def test_status_code_by_name(self):
        """Test accessing status codes by name."""
        assert enums.HTTPStatus["OK"].value == 200
        assert enums.HTTPStatus["NOT_FOUND"].value == 404
        assert enums.HTTPStatus["INTERNAL_SERVER_ERROR"].value == 500

    def test_status_code_by_value(self):
        """Test accessing status codes by value."""
        assert enums.HTTPStatus(200) == enums.HTTPStatus.OK
        assert enums.HTTPStatus(404) == enums.HTTPStatus.NOT_FOUND
        assert enums.HTTPStatus(500) == enums.HTTPStatus.INTERNAL_SERVER_ERROR

    def test_status_code_comparison(self):
        """Test comparing status codes."""
        assert enums.HTTPStatus.OK.value < enums.HTTPStatus.NOT_FOUND.value
        assert (
            enums.HTTPStatus.NOT_FOUND.value
            < enums.HTTPStatus.INTERNAL_SERVER_ERROR.value
        )
        assert enums.HTTPStatus.OK == enums.HTTPStatus.OK
        assert enums.HTTPStatus.OK != enums.HTTPStatus.CREATED

    def test_status_code_iteration(self):
        """Test iterating over all status codes."""
        all_statuses = list(enums.HTTPStatus)
        assert len(all_statuses) > 0
        assert enums.HTTPStatus.OK in all_statuses
        assert enums.HTTPStatus.NOT_FOUND in all_statuses
        assert enums.HTTPStatus.INTERNAL_SERVER_ERROR in all_statuses

    def test_status_code_membership(self):
        """Test membership testing for status codes."""
        assert enums.HTTPStatus.OK in enums.HTTPStatus
        assert enums.HTTPStatus.NOT_FOUND in enums.HTTPStatus
        assert enums.HTTPStatus.INTERNAL_SERVER_ERROR in enums.HTTPStatus

    def test_status_code_names(self):
        """Test that status code names match expected values."""
        assert enums.HTTPStatus.OK.name == "OK"
        assert enums.HTTPStatus.NOT_FOUND.name == "NOT_FOUND"
        assert enums.HTTPStatus.INTERNAL_SERVER_ERROR.name == "INTERNAL_SERVER_ERROR"

    def test_status_code_uniqueness(self):
        """Test that all status code values are unique."""
        values = [status.value for status in enums.HTTPStatus]
        assert len(values) == len(set(values))

    def test_commonly_used_status_codes(self):
        """Test commonly used status codes are present."""
        # Most common success codes
        assert enums.HTTPStatus.OK.value == 200
        assert enums.HTTPStatus.CREATED.value == 201
        assert enums.HTTPStatus.NO_CONTENT.value == 204

        # Most common client error codes
        assert enums.HTTPStatus.BAD_REQUEST.value == 400
        assert enums.HTTPStatus.UNAUTHORIZED.value == 401
        assert enums.HTTPStatus.FORBIDDEN.value == 403
        assert enums.HTTPStatus.NOT_FOUND.value == 404

        # Most common server error codes
        assert enums.HTTPStatus.INTERNAL_SERVER_ERROR.value == 500
        assert enums.HTTPStatus.BAD_GATEWAY.value == 502
        assert enums.HTTPStatus.SERVICE_UNAVAILABLE.value == 503

    def test_status_code_ranges(self):
        """Test that status codes are in correct ranges."""
        for status in enums.HTTPStatus:
            if status.name.startswith(("CONTINUE", "SWITCHING", "PROCESSING", "EARLY")):
                assert 100 <= status.value < 200
            elif status.name in (
                "OK",
                "CREATED",
                "ACCEPTED",
                "NON_AUTHORITATIVE_INFORMATION",
                "NO_CONTENT",
                "RESET_CONTENT",
                "PARTIAL_CONTENT",
                "MULTI_STATUS",
                "ALREADY_REPORTED",
                "IM_USED",
            ):
                assert 200 <= status.value < 300
            elif status.name in (
                "MULTIPLE_CHOICES",
                "MOVED_PERMANENTLY",
                "FOUND",
                "SEE_OTHER",
                "NOT_MODIFIED",
                "USE_PROXY",
                "TEMPORARY_REDIRECT",
                "PERMANENT_REDIRECT",
            ):
                assert 300 <= status.value < 400

    def test_invalid_status_code_raises_error(self):
        """Test that accessing non-existent status code raises ValueError."""
        with pytest.raises(ValueError):
            enums.HTTPStatus(999)

    def test_status_code_string_representation(self):
        """Test string representation of status codes."""
        assert "HTTPStatus.OK" in str(enums.HTTPStatus.OK)
        assert "HTTPStatus.NOT_FOUND" in str(enums.HTTPStatus.NOT_FOUND)


class TestHTTPMethod:
    """Test cases for the HTTPMethod enumeration."""

    def test_http_method_is_enum(self):
        """Test that HTTPMethod is an Enum class."""
        assert issubclass(enums.HTTPMethod, Enum)

    def test_standard_http_methods(self):
        """Test standard HTTP methods are defined."""
        assert enums.HTTPMethod.GET.value == "GET"
        assert enums.HTTPMethod.POST.value == "POST"
        assert enums.HTTPMethod.PUT.value == "PUT"
        assert enums.HTTPMethod.DELETE.value == "DELETE"
        assert enums.HTTPMethod.PATCH.value == "PATCH"
        assert enums.HTTPMethod.HEAD.value == "HEAD"
        assert enums.HTTPMethod.OPTIONS.value == "OPTIONS"
        assert enums.HTTPMethod.TRACE.value == "TRACE"
        assert enums.HTTPMethod.CONNECT.value == "CONNECT"

    def test_method_by_name(self):
        """Test accessing methods by name."""
        assert enums.HTTPMethod["GET"].value == "GET"
        assert enums.HTTPMethod["POST"].value == "POST"
        assert enums.HTTPMethod["DELETE"].value == "DELETE"

    def test_method_by_value(self):
        """Test accessing methods by value."""
        assert enums.HTTPMethod("GET") == enums.HTTPMethod.GET
        assert enums.HTTPMethod("POST") == enums.HTTPMethod.POST
        assert enums.HTTPMethod("DELETE") == enums.HTTPMethod.DELETE

    def test_method_comparison(self):
        """Test comparing HTTP methods."""
        assert enums.HTTPMethod.GET == enums.HTTPMethod.GET
        assert enums.HTTPMethod.GET != enums.HTTPMethod.POST
        assert enums.HTTPMethod.PUT != enums.HTTPMethod.PATCH

    def test_method_iteration(self):
        """Test iterating over all HTTP methods."""
        all_methods = list(enums.HTTPMethod)
        assert len(all_methods) == 9
        assert enums.HTTPMethod.GET in all_methods
        assert enums.HTTPMethod.POST in all_methods
        assert enums.HTTPMethod.DELETE in all_methods

    def test_method_membership(self):
        """Test membership testing for HTTP methods."""
        assert enums.HTTPMethod.GET in enums.HTTPMethod
        assert enums.HTTPMethod.POST in enums.HTTPMethod
        assert enums.HTTPMethod.DELETE in enums.HTTPMethod

    def test_method_names(self):
        """Test that method names match expected values."""
        assert enums.HTTPMethod.GET.name == "GET"
        assert enums.HTTPMethod.POST.name == "POST"
        assert enums.HTTPMethod.DELETE.name == "DELETE"

    def test_method_values_are_strings(self):
        """Test that all method values are strings."""
        for method in enums.HTTPMethod:
            assert isinstance(method.value, str)
            assert method.value.isupper()

    def test_method_uniqueness(self):
        """Test that all method values are unique."""
        values = [method.value for method in enums.HTTPMethod]
        assert len(values) == len(set(values))

    def test_commonly_used_methods(self):
        """Test commonly used HTTP methods are present."""
        # CRUD operations
        assert enums.HTTPMethod.GET.value == "GET"  # Read
        assert enums.HTTPMethod.POST.value == "POST"  # Create
        assert enums.HTTPMethod.PUT.value == "PUT"  # Update/Replace
        assert enums.HTTPMethod.PATCH.value == "PATCH"  # Partial Update
        assert enums.HTTPMethod.DELETE.value == "DELETE"  # Delete

        # Other common methods
        assert enums.HTTPMethod.HEAD.value == "HEAD"
        assert enums.HTTPMethod.OPTIONS.value == "OPTIONS"

    def test_invalid_method_raises_error(self):
        """Test that accessing non-existent method raises ValueError."""
        with pytest.raises(ValueError):
            enums.HTTPMethod("INVALID")

    def test_method_string_representation(self):
        """Test string representation of HTTP methods."""
        assert "HTTPMethod.GET" in str(enums.HTTPMethod.GET)
        assert "HTTPMethod.POST" in str(enums.HTTPMethod.POST)

    def test_method_value_matches_name(self):
        """Test that method values match their names."""
        for method in enums.HTTPMethod:
            assert method.value == method.name

    def test_safe_vs_unsafe_methods(self):
        """Test categorization of safe vs unsafe HTTP methods."""
        # Safe methods (should not modify resources)
        safe_methods = {
            enums.HTTPMethod.GET,
            enums.HTTPMethod.HEAD,
            enums.HTTPMethod.OPTIONS,
        }

        # Unsafe methods (may modify resources)
        unsafe_methods = {
            enums.HTTPMethod.POST,
            enums.HTTPMethod.PUT,
            enums.HTTPMethod.DELETE,
            enums.HTTPMethod.PATCH,
        }

        # Note: TRACE and CONNECT are special cases not categorized here

        for method in safe_methods:
            assert method.value in ["GET", "HEAD", "OPTIONS"]

        for method in unsafe_methods:
            assert method.value in ["POST", "PUT", "DELETE", "PATCH"]

    def test_idempotent_methods(self):
        """Test identification of idempotent HTTP methods."""
        # Idempotent methods (multiple identical requests same as single request)
        idempotent = {
            enums.HTTPMethod.GET,
            enums.HTTPMethod.HEAD,
            enums.HTTPMethod.PUT,
            enums.HTTPMethod.DELETE,
            enums.HTTPMethod.OPTIONS,
        }

        # Non-idempotent methods
        non_idempotent = {enums.HTTPMethod.POST, enums.HTTPMethod.PATCH}

        for method in idempotent:
            assert method.value in ["GET", "HEAD", "PUT", "DELETE", "OPTIONS"]

        for method in non_idempotent:
            assert method.value in ["POST", "PATCH"]


class TestEnumsModule:
    """Test cases for the enums module as a whole."""

    def test_module_exports(self):
        """Test that module exports expected enumerations."""
        assert hasattr(enums, "HTTPStatus")
        assert hasattr(enums, "HTTPMethod")

    def test_module_all_attribute(self):
        """Test that __all__ is properly defined."""
        assert hasattr(enums, "__all__")
        assert "HTTPStatus" in enums.__all__
        assert "HTTPMethod" in enums.__all__
        assert isinstance(enums.__all__, tuple)

    def test_enum_types_are_different(self):
        """Test that HTTPStatus and HTTPMethod are different types."""
        assert enums.HTTPStatus is not enums.HTTPMethod
        assert type(enums.HTTPStatus.OK) is not type(enums.HTTPMethod.GET)

    def test_no_value_collision_between_enums(self):
        """Test that HTTPStatus and HTTPMethod don't share values."""
        status_values = {status.value for status in enums.HTTPStatus}
        method_values = {method.value for method in enums.HTTPMethod}

        # No overlap between status codes (integers) and methods (strings)
        assert not status_values.intersection(method_values)

    def test_enum_immutability(self):
        """Test that enum values cannot be modified."""
        with pytest.raises(AttributeError):
            enums.HTTPStatus.OK = 201

        with pytest.raises(AttributeError):
            enums.HTTPMethod.GET = "POST"

    def test_enum_members_cannot_be_deleted(self):
        """Test that enum members cannot be deleted."""
        # Enums don't allow deleting members
        with pytest.raises(AttributeError):
            del enums.HTTPStatus.OK


class TestHTTPStatusEdgeCases:
    """Test edge cases and special scenarios for HTTPStatus."""

    def test_teapot_status_code(self):
        """Test the humorous 418 I'm a teapot status code."""
        assert enums.HTTPStatus.IM_A_TEAPOT.value == 418

    def test_status_code_with_underscores(self):
        """Test status codes with long names containing underscores."""
        assert enums.HTTPStatus.NON_AUTHORITATIVE_INFORMATION.value == 203
        assert enums.HTTPStatus.PROXY_AUTHENTICATION_REQUIRED.value == 407
        assert enums.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE.value == 431

    def test_multiple_ways_to_access_same_status(self):
        """Test accessing the same status code in different ways."""
        # By name
        status1 = enums.HTTPStatus.OK

        # By value
        status2 = enums.HTTPStatus(200)

        # By string name
        status3 = enums.HTTPStatus["OK"]

        assert status1 == status2 == status3
        assert status1 is status2 is status3

    def test_status_code_hash_consistency(self):
        """Test that enum members have consistent hashes."""
        status1 = enums.HTTPStatus.OK
        status2 = enums.HTTPStatus.OK

        assert hash(status1) == hash(status2)
        assert status1 is status2

    def test_status_code_in_dict_keys(self):
        """Test using status codes as dictionary keys."""
        status_dict = {
            enums.HTTPStatus.OK: "Success",
            enums.HTTPStatus.NOT_FOUND: "Not Found",
            enums.HTTPStatus.INTERNAL_SERVER_ERROR: "Server Error",
        }

        assert status_dict[enums.HTTPStatus.OK] == "Success"
        assert status_dict[enums.HTTPStatus(404)] == "Not Found"
        assert status_dict[enums.HTTPStatus["INTERNAL_SERVER_ERROR"]] == "Server Error"

    def test_status_code_in_set(self):
        """Test using status codes in sets."""
        success_codes = {
            enums.HTTPStatus.OK,
            enums.HTTPStatus.CREATED,
            enums.HTTPStatus.NO_CONTENT,
        }

        assert enums.HTTPStatus.OK in success_codes
        assert enums.HTTPStatus.NOT_FOUND not in success_codes
        assert len(success_codes) == 3


class TestHTTPMethodEdgeCases:
    """Test edge cases and special scenarios for HTTPMethod."""

    def test_multiple_ways_to_access_same_method(self):
        """Test accessing the same method in different ways."""
        # By name
        method1 = enums.HTTPMethod.GET

        # By value
        method2 = enums.HTTPMethod("GET")

        # By string name
        method3 = enums.HTTPMethod["GET"]

        assert method1 == method2 == method3
        assert method1 is method2 is method3

    def test_method_hash_consistency(self):
        """Test that enum members have consistent hashes."""
        method1 = enums.HTTPMethod.GET
        method2 = enums.HTTPMethod.GET

        assert hash(method1) == hash(method2)
        assert method1 is method2

    def test_method_in_dict_keys(self):
        """Test using methods as dictionary keys."""
        method_dict = {
            enums.HTTPMethod.GET: "Retrieve",
            enums.HTTPMethod.POST: "Create",
            enums.HTTPMethod.DELETE: "Remove",
        }

        assert method_dict[enums.HTTPMethod.GET] == "Retrieve"
        assert method_dict[enums.HTTPMethod("POST")] == "Create"
        assert method_dict[enums.HTTPMethod["DELETE"]] == "Remove"

    def test_method_in_set(self):
        """Test using methods in sets."""
        crud_methods = {
            enums.HTTPMethod.GET,
            enums.HTTPMethod.POST,
            enums.HTTPMethod.PUT,
            enums.HTTPMethod.DELETE,
        }

        assert enums.HTTPMethod.GET in crud_methods
        assert enums.HTTPMethod.OPTIONS not in crud_methods
        assert len(crud_methods) == 4

    def test_method_case_sensitivity(self):
        """Test that method values are case-sensitive."""
        assert enums.HTTPMethod.GET.value == "GET"

        # Lowercase version should raise ValueError
        with pytest.raises(ValueError):
            enums.HTTPMethod("get")


class TestEnumsIntegration:
    """Integration tests for enums with realistic use cases."""

    def test_status_code_and_method_combination(self):
        """Test combining status codes and methods in realistic scenarios."""
        # Successful GET request
        method = enums.HTTPMethod.GET
        status = enums.HTTPStatus.OK
        assert method.value == "GET"
        assert status.value == 200

        # Resource creation with POST
        method = enums.HTTPMethod.POST
        status = enums.HTTPStatus.CREATED
        assert method.value == "POST"
        assert status.value == 201

        # Resource not found with GET
        method = enums.HTTPMethod.GET
        status = enums.HTTPStatus.NOT_FOUND
        assert method.value == "GET"
        assert status.value == 404

    def test_building_http_response_mapping(self):
        """Test building a response mapping with enums."""
        response_map = {
            (enums.HTTPMethod.GET, enums.HTTPStatus.OK): (
                "Resource retrieved successfully"
            ),
            (enums.HTTPMethod.POST, enums.HTTPStatus.CREATED): (
                "Resource created successfully"
            ),
            (enums.HTTPMethod.DELETE, enums.HTTPStatus.NO_CONTENT): (
                "Resource deleted successfully"
            ),
            (enums.HTTPMethod.GET, enums.HTTPStatus.NOT_FOUND): "Resource not found",
        }

        # Test accessing the map
        key1 = (enums.HTTPMethod.GET, enums.HTTPStatus.OK)
        assert response_map[key1] == "Resource retrieved successfully"

        key2 = (enums.HTTPMethod.POST, enums.HTTPStatus.CREATED)
        assert response_map[key2] == "Resource created successfully"

    def test_http_method_routing(self):
        """Test using HTTP methods for routing logic."""
        allowed_methods = {
            enums.HTTPMethod.GET,
            enums.HTTPMethod.POST,
            enums.HTTPMethod.PUT,
        }

        assert enums.HTTPMethod.GET in allowed_methods
        assert enums.HTTPMethod.DELETE not in allowed_methods

    def test_status_code_categorization(self):
        """Test categorizing status codes by type."""

        def is_success(status: enums.HTTPStatus) -> bool:
            return 200 <= status.value < 300

        def is_client_error(status: enums.HTTPStatus) -> bool:
            return 400 <= status.value < 500

        def is_server_error(status: enums.HTTPStatus) -> bool:
            return 500 <= status.value < 600

        assert is_success(enums.HTTPStatus.OK)
        assert is_success(enums.HTTPStatus.CREATED)
        assert not is_success(enums.HTTPStatus.NOT_FOUND)

        assert is_client_error(enums.HTTPStatus.BAD_REQUEST)
        assert is_client_error(enums.HTTPStatus.UNAUTHORIZED)
        assert not is_client_error(enums.HTTPStatus.OK)

        assert is_server_error(enums.HTTPStatus.INTERNAL_SERVER_ERROR)
        assert is_server_error(enums.HTTPStatus.BAD_GATEWAY)
        assert not is_server_error(enums.HTTPStatus.NOT_FOUND)
