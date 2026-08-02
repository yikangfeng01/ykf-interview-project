"""Integration tests for Flask API endpoints using test client."""
import pytest
import json
from app import app
from unittest.mock import patch, MagicMock
from auth.models import User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============ Auth API ============

class TestLoginAPI:
    @patch("app.authenticate")
    def test_login_success(self, mock_auth, client):
        mock_auth.return_value = (True, "test-token-uuid")
        resp = client.post(
            "/api/login",
            data=json.dumps({"username": "admin", "password": "password123"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["token"] == "test-token-uuid"

    @patch("app.authenticate")
    def test_login_wrong_password(self, mock_auth, client):
        mock_auth.return_value = (False, "Invalid username or password")
        resp = client.post(
            "/api/login",
            data=json.dumps({"username": "admin", "password": "wrong"}),
            content_type="application/json",
        )
        assert resp.status_code == 401

    def test_login_invalid_json(self, client):
        resp = client.post("/api/login", data="not json", content_type="application/json")
        assert resp.status_code == 400


class TestVerifyAPI:
    @patch("app.get_current_user")
    def test_verify_valid(self, mock_get_user, client):
        mock_get_user.return_value = User(id=1, username="admin", password_hash="h", token="tok")
        resp = client.post("/api/verify", data=json.dumps({"token": "valid-token"}), content_type="application/json")
        assert resp.status_code == 200
        assert resp.get_json()["username"] == "admin"

    @patch("app.get_current_user")
    def test_verify_invalid(self, mock_get_user, client):
        mock_get_user.return_value = None
        resp = client.post("/api/verify", data=json.dumps({"token": "bad"}), content_type="application/json")
        assert resp.status_code == 401


class TestLogoutAPI:
    @patch("app.auth_logout")
    def test_logout_success(self, mock_logout, client):
        resp = client.post("/api/logout", data=json.dumps({"token": "valid"}), content_type="application/json")
        assert resp.status_code == 200

    def test_logout_missing_token(self, client):
        resp = client.post("/api/logout", data=json.dumps({"token": ""}), content_type="application/json")
        assert resp.status_code == 400


# ============ Projects API ============

class TestProjectsAPI:
    def _mock_user(self):
        return User(id=1, username="admin", password_hash="h", token="tok")

    @patch("app.get_current_user")
    @patch("app.projects.list_by_user")
    def test_list_projects(self, mock_list, mock_get_user, client):
        mock_get_user.return_value = self._mock_user()
        mock_list.return_value = [{"id": 1, "name": "Test", "status": "draft", "created_by": "admin"}]
        resp = client.get("/api/projects?token=valid")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    @patch("app.get_current_user")
    @patch("app.projects.create")
    def test_create_project(self, mock_create, mock_get_user, client):
        mock_get_user.return_value = self._mock_user()
        mock_create.return_value = {"id": 1, "name": "New Project", "status": "draft", "created_by": "admin"}
        resp = client.post(
            "/api/projects",
            data=json.dumps({"token": "valid", "name": "New Project"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    @patch("app.get_current_user")
    def test_create_project_empty_name(self, mock_get_user, client):
        mock_get_user.return_value = self._mock_user()
        resp = client.post(
            "/api/projects",
            data=json.dumps({"token": "valid", "name": ""}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_projects_unauthorized(self, client):
        resp = client.get("/api/projects")
        assert resp.status_code == 401


class TestProjectDetailAPI:
    def _mock_user(self):
        return User(id=1, username="admin", password_hash="h", token="tok")

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    def test_get_project(self, mock_get, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_get.return_value = {"id": 1, "name": "My Project", "status": "draft", "created_by": "admin"}
        resp = client.get("/api/projects/1?token=valid")
        assert resp.status_code == 200

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    def test_get_project_not_found(self, mock_get, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_get.return_value = None
        resp = client.get("/api/projects/999?token=valid")
        assert resp.status_code == 404

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    def test_get_project_forbidden(self, mock_get, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_get.return_value = {"id": 1, "name": "X", "status": "draft", "created_by": "other_user"}
        resp = client.get("/api/projects/1?token=valid")
        assert resp.status_code == 403

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.projects.update")
    def test_put_project(self, mock_update, mock_get, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_get.return_value = {"id": 1, "name": "Old", "status": "draft", "created_by": "admin"}
        mock_update.return_value = {"id": 1, "name": "New Name", "status": "draft", "created_by": "admin"}
        resp = client.put(
            "/api/projects/1",
            data=json.dumps({"token": "valid", "name": "New Name"}),
            content_type="application/json",
        )
        assert resp.status_code == 200

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.projects.delete")
    def test_delete_project(self, mock_delete, mock_get, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_get.return_value = {"id": 1, "name": "X", "status": "draft", "created_by": "admin"}
        mock_delete.return_value = True
        resp = client.delete(
            "/api/projects/1",
            data=json.dumps({"token": "valid"}),
            content_type="application/json",
        )
        assert resp.status_code == 204


# ============ Templates API ============

class TestTemplatesAPI:
    def _mock_user(self):
        return User(id=1, username="admin", password_hash="h", token="tok")

    @patch("app.get_current_user")
    @patch("app.templates.list_all")
    def test_list_templates(self, mock_list, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_list.return_value = [{"id": 1, "name": "T1", "category": "c1"}]
        resp = client.get("/api/templates?token=valid")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    @patch("app.get_current_user")
    @patch("app.templates.list_all")
    def test_filter_by_category(self, mock_list, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_list.return_value = []
        resp = client.get("/api/templates?token=valid&category=share_transfer")
        assert resp.status_code == 200
        mock_list.assert_called_once_with(category="share_transfer")


# ============ Template Selection API ============

class TestSelectTemplateAPI:
    def _mock_user(self):
        return User(id=1, username="admin", password_hash="h", token="tok")

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.templates.get_by_id")
    @patch("app.projects.update")
    def test_select_template(self, mock_update, mock_tmpl, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_tmpl.return_value = {"id": 2, "name": "T1"}
        mock_update.return_value = {"id": 1, "name": "P", "status": "template_selected", "template_id": 2, "created_by": "admin"}
        resp = client.post(
            "/api/projects/1/select-template",
            data=json.dumps({"token": "valid", "template_id": 2}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "template_selected"

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.templates.get_by_id")
    def test_select_nonexistent_template(self, mock_tmpl, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_tmpl.return_value = None
        resp = client.post(
            "/api/projects/1/select-template",
            data=json.dumps({"token": "valid", "template_id": 999}),
            content_type="application/json",
        )
        assert resp.status_code == 404


# ============ Project Templates API ============

class TestProjectTemplatesAPI:
    def _mock_user(self):
        return User(id=1, username="admin", password_hash="h", token="tok")

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.list_all")
    def test_list_project_templates(self, mock_list, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_list.return_value = [{"id": 1, "name": "T1", "category": "IPO", "project_id": 1}]
        resp = client.get("/api/projects/1/templates?token=valid")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.list_all")
    def test_list_project_templates_filter_category(self, mock_list, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_list.return_value = []
        resp = client.get("/api/projects/1/templates?token=valid&category=IPO")
        assert resp.status_code == 200
        mock_list.assert_called_once_with(1, category="IPO")

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    def test_list_project_templates_project_not_found(self, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = None
        resp = client.get("/api/projects/999/templates?token=valid")
        assert resp.status_code == 404

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.get_by_id")
    @patch("app.project_templates.update")
    def test_update_project_template(self, mock_update, mock_get, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_get.return_value = {"id": 1, "name": "Old", "category": "IPO", "project_id": 1}
        mock_update.return_value = {"id": 1, "name": "New", "category": "M&A", "project_id": 1}
        resp = client.put(
            "/api/projects/1/templates/1",
            data=json.dumps({"token": "valid", "name": "New", "category": "M&A"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "New"

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.get_by_id")
    @patch("app.project_templates.delete")
    def test_delete_project_template(self, mock_delete, mock_get, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_get.return_value = {"id": 1, "name": "T1", "category": "IPO", "project_id": 1}
        mock_delete.return_value = {"id": 1, "name": "T1"}
        resp = client.delete(
            "/api/projects/1/templates/1",
            data=json.dumps({"token": "valid"}),
            content_type="application/json",
        )
        assert resp.status_code == 204


# ============ Project Template Variables API ============

class TestProjectVariablesAPI:
    def _mock_user(self):
        return User(id=1, username="admin", password_hash="h", token="tok")

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.get_by_id")
    @patch("app.project_variables.get_by_template_id")
    def test_list_project_variables(self, mock_list, mock_tmpl, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_tmpl.return_value = {"id": 1, "name": "T1", "project_id": 1}
        mock_list.return_value = [{"id": 1, "name": "签名", "var_type": "signature", "template_id": 1}]
        resp = client.get("/api/projects/1/templates/1/variables?token=valid")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.get_by_id")
    @patch("app.project_variables.create")
    def test_create_project_variable(self, mock_create, mock_tmpl, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_tmpl.return_value = {"id": 1, "name": "T1", "project_id": 1}
        mock_create.return_value = {"id": 1, "name": "签名", "var_type": "signature", "template_id": 1}
        resp = client.post(
            "/api/projects/1/templates/1/variables",
            data=json.dumps({"token": "valid", "name": "签名", "var_type": "signature", "page": 1}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.get_by_id")
    @patch("app.project_variables.create")
    def test_create_project_variable_empty_name(self, mock_create, mock_tmpl, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_tmpl.return_value = {"id": 1, "name": "T1", "project_id": 1}
        resp = client.post(
            "/api/projects/1/templates/1/variables",
            data=json.dumps({"token": "valid", "name": ""}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.get_by_id")
    @patch("app.project_variables.get_by_id")
    @patch("app.project_variables.delete")
    def test_delete_project_variable(self, mock_delete, mock_get, mock_tmpl, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_tmpl.return_value = {"id": 1, "name": "T1", "project_id": 1}
        mock_get.return_value = {"id": 1, "name": "签名", "template_id": 1}
        resp = client.delete(
            "/api/projects/1/templates/1/variables/1",
            data=json.dumps({"token": "valid"}),
            content_type="application/json",
        )
        assert resp.status_code == 204

    @patch("app.get_current_user")
    @patch("app.projects.get_by_id")
    @patch("app.project_templates.get_by_id")
    @patch("app.project_variables.get_by_id")
    @patch("app.project_variables.update")
    def test_update_project_variable(self, mock_update, mock_var_get, mock_tmpl, mock_proj, mock_auth, client):
        mock_auth.return_value = self._mock_user()
        mock_proj.return_value = {"id": 1, "name": "P", "status": "draft", "created_by": "admin"}
        mock_tmpl.return_value = {"id": 1, "name": "T1", "project_id": 1}
        mock_var_get.return_value = {"id": 1, "name": "签名", "template_id": 1}
        mock_update.return_value = {"id": 1, "name": "签名", "font_size": 14, "template_id": 1}
        resp = client.put(
            "/api/projects/1/templates/1/variables/1",
            data=json.dumps({"token": "valid", "font_size": 14}),
            content_type="application/json",
        )
        assert resp.status_code == 200


# ============ Static ============

class TestIndex:
    def test_index_serves_spa(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
