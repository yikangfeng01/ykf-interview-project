"""Unit tests for auth module with PostgreSQL backend."""
import pytest
import bcrypt
import uuid
from unittest.mock import patch, MagicMock
from auth.service import hash_password, verify_password, authenticate, get_current_user, logout
from auth.models import User


class TestPasswordHashing:
    def test_hash_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)
        assert result != "mypassword"

    def test_verify_correct_password(self):
        hashed = hash_password("secure123")
        assert verify_password("secure123", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("secure123")
        assert verify_password("wrong", hashed) is False

    def test_hash_is_salted(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # different salts


class TestAuthenticate:
    def setup_method(self):
        self.mock_store = MagicMock()
        self.valid_user = User(
            id=1,
            username="admin",
            password_hash=bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode(),
            token=None,
        )

    def test_successful_login(self):
        self.mock_store.find_by_username.return_value = self.valid_user
        success, token = authenticate("admin", "password123", store=self.mock_store)
        assert success is True
        assert isinstance(token, str)
        self.mock_store.update_token.assert_called_once_with("admin", token)

    def test_wrong_password(self):
        self.mock_store.find_by_username.return_value = self.valid_user
        success, msg = authenticate("admin", "wrong", store=self.mock_store)
        assert success is False
        assert "Invalid username or password" in msg

    def test_nonexistent_user(self):
        self.mock_store.find_by_username.return_value = None
        success, msg = authenticate("nobody", "any", store=self.mock_store)
        assert success is False
        assert "Invalid username or password" in msg

    def test_missing_username(self):
        success, msg = authenticate("", "password", store=self.mock_store)
        assert success is False
        assert "Username is required" in msg

    def test_missing_password(self):
        success, msg = authenticate("admin", "", store=self.mock_store)
        assert success is False
        assert "Password is required" in msg


class TestGetCurrentUser:
    def test_valid_token_returns_user(self):
        mock_store = MagicMock()
        expected_user = User(id=1, username="admin", password_hash="hash", token="abc-123")
        mock_store.find_by_token.return_value = expected_user

        user = get_current_user("abc-123", store=mock_store)
        assert user is not None
        assert user.username == "admin"

    def test_invalid_token_returns_none(self):
        mock_store = MagicMock()
        mock_store.find_by_token.return_value = None

        user = get_current_user("bad-token", store=mock_store)
        assert user is None


class TestLogout:
    def test_logout_calls_clear_token(self):
        mock_store = MagicMock()
        logout("abc-123", store=mock_store)
        mock_store.clear_token.assert_called_once_with("abc-123")

    def test_logout_empty_token_raises(self):
        with pytest.raises(ValueError, match="Token is required"):
            logout("")
