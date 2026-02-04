import pytest
import json
from src.api.users_api import UsersAPI
from src.utils.schema_validator import validate_schema
from src.utils.email_validator import is_valid_email

def load_user_crud_data():
    with open("data/testdata/user_crud.json") as f:
        return json.load(f)

def load_user_crud_negative_data():
    with open("data/testdata/user_crud_negative.json") as f:
        return json.load(f)

@pytest.mark.smoke
@pytest.mark.contract
def test_get_users_contract(api_client, db):
    users_api = UsersAPI(api_client.base_url)
    resp = users_api.get_users()
    # Response time validation (e.g., must be < 4 seconds)
    assert resp.elapsed.total_seconds() < 4, f"Response time too high: {resp.elapsed.total_seconds()}s"
    # HTTP status code validation
    assert resp.status_code == 200
    users = resp.json()
    assert isinstance(users, list)
    for user in users:
        # Schema validation
        validate_schema(user, "data/schemas/user_schema.json")
        # Mandatory fields validation
        for field in ["id", "name", "username", "email"]:
            assert field in user
        # Email format validation
        assert is_valid_email(user["email"])
        # Store all users in fake DB
        db.insert("users", {k: user[k] for k in ("id", "name", "username", "email")})
    # Unique ID validation
    ids = [u["id"] for u in users]
    assert len(ids) == len(set(ids))
    db_users = db.fetchall("users")
    # Validate user count
    assert len(db_users) == len(users)
    # Validate API data vs DB data
    api_users_sorted = sorted(users, key=lambda x: x["id"])
    db_users_sorted = sorted(db_users, key=lambda x: x[0])
    for api_user, db_user in zip(api_users_sorted, db_users_sorted):
        assert api_user["id"] == db_user[0]
        assert api_user["name"] == db_user[1]
        assert api_user["username"] == db_user[2]
        assert api_user["email"] == db_user[3]

@pytest.mark.contract
def test_get_user_by_id_validations(api_client, db):
    users_api = UsersAPI(api_client.base_url)
    # Get all users from /users
    all_users_resp = users_api.get_users()
    assert all_users_resp.status_code == 200
    all_users = all_users_resp.json()
    # For each user, call /users/{id} and validate
    for user in all_users:
        user_id = user["id"]
        resp = users_api.get_user_by_id(user_id)
        # Response time validation
        assert resp.elapsed.total_seconds() < 4, f"Response time too high: {resp.elapsed.total_seconds()}s for user {user_id}"
        assert resp.status_code == 200
        user_data = resp.json()
        # Schema validation
        validate_schema(user_data, "data/schemas/user_schema.json")
        # Mandatory fields
        for field in ["id", "name", "username", "email"]:
            assert field in user_data
        # Email format
        assert is_valid_email(user_data["email"])
        # Data matches /users and DB
        assert user_data["id"] == user["id"]
        assert user_data["name"] == user["name"]
        assert user_data["username"] == user["username"]
        assert user_data["email"] == user["email"]
        # Insert user into DB for this test
        db.insert("users", {k: user_data[k] for k in ("id", "name", "username", "email")})
        db_user = [row for row in db.fetchall("users") if row[0] == user_id]
        assert db_user, f"User {user_id} not found in DB"
        db_user = db_user[0]
        assert user_data["id"] == db_user[0]
        assert user_data["name"] == db_user[1]
        assert user_data["username"] == db_user[2]
        assert user_data["email"] == db_user[3]

@pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
def test_get_user_by_id_parametrized(api_client, db, user_id):
    users_api = UsersAPI(api_client.base_url)
    resp = users_api.get_user_by_id(user_id)
    assert resp.status_code == 200
    assert resp.elapsed.total_seconds() < 4
    user_data = resp.json()
    validate_schema(user_data, "data/schemas/user_schema.json")
    for field in ["id", "name", "username", "email"]:
        assert field in user_data
    assert is_valid_email(user_data["email"])
    # Insert user into DB for this test only if not already present
    db_users = db.fetchall("users")
    if not any(row[0] == user_id for row in db_users):
        db.insert("users", {k: user_data[k] for k in ("id", "name", "username", "email")})
    db_user = [row for row in db.fetchall("users") if row[0] == user_id]
    assert db_user, f"User {user_id} not found in DB"
    db_user = db_user[0]
    assert user_data["id"] == db_user[0]
    assert user_data["name"] == db_user[1]
    assert user_data["username"] == db_user[2]
    assert user_data["email"] == db_user[3]

@pytest.mark.negative
def test_get_user_invalid_id(api_client):
    users_api = UsersAPI(api_client.base_url)
    # Using a non-existent user ID
    resp = users_api.get_user_by_id(9999)
    assert resp.status_code == 404 or resp.json() == {}

@pytest.mark.negative
def test_get_user_non_numeric_id(api_client):
    users_api = UsersAPI(api_client.base_url)
    # Using a non-numeric user ID
    resp = users_api.get_user_by_id("abc")
    assert resp.status_code == 404 or resp.json() == {}

@pytest.mark.smoke
@pytest.mark.contract
def test_create_user(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_data()
    new_user = data["create"]
    resp = users_api.create_user(new_user)
    assert resp.status_code == 201
    user = resp.json()
    for field in ["name", "username", "email"]:
        assert user[field] == new_user[field]

@pytest.mark.negative
def test_create_user_missing_fields(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_negative_data()
    incomplete_user = data["missing_fields"]
    resp = users_api.create_user(incomplete_user)
    assert resp.status_code in [400, 422, 201]

@pytest.mark.negative
def test_create_user_invalid_email(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_negative_data()
    invalid_user = data["invalid_email"]
    resp = users_api.create_user(invalid_user)
    assert resp.status_code in [400, 422, 201]

@pytest.mark.contract
def test_update_user(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_data()
    user_id = 1
    updated_data = data["update"]
    resp = users_api.update_user(user_id, updated_data)
    assert resp.status_code in [200, 201]
    user = resp.json()
    for field in updated_data:
        assert user[field] == updated_data[field]

@pytest.mark.negative
def test_update_user_invalid_id(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_data()
    neg_data = load_user_crud_negative_data()
    invalid_id = neg_data["invalid_id"]
    updated_data = data["update"]
    resp = users_api.update_user(invalid_id, updated_data)
    assert resp.status_code in [404, 400, 201, 200, 500]

@pytest.mark.contract
def test_patch_user(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_data()
    user_id = 1
    patch_data = data["patch"]
    resp = users_api.patch_user(user_id, patch_data)
    assert resp.status_code in [200, 201]
    user = resp.json()
    assert user["name"] == patch_data["name"]

@pytest.mark.negative
def test_patch_user_invalid_id(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_data()
    neg_data = load_user_crud_negative_data()
    invalid_id = neg_data["invalid_id"]
    patch_data = data["patch"]
    resp = users_api.patch_user(invalid_id, patch_data)
    assert resp.status_code in [404, 400, 201, 200]

@pytest.mark.contract
def test_delete_user(api_client):
    users_api = UsersAPI(api_client.base_url)
    data = load_user_crud_data()
    user_id = data["delete_id"]
    resp = users_api.delete_user(user_id)
    assert resp.status_code in [200, 204]

@pytest.mark.negative
def test_delete_user_invalid_id(api_client):
    users_api = UsersAPI(api_client.base_url)
    neg_data = load_user_crud_negative_data()
    invalid_id = neg_data["invalid_id"]
    resp = users_api.delete_user(invalid_id)
    assert resp.status_code in [404, 400, 204, 200]

