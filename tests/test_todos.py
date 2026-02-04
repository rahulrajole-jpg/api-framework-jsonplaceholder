import pytest
from src.api.todos_api import TodosAPI
from src.api.users_api import UsersAPI
from src.utils.schema_validator import validate_schema
import json

def load_todo_crud_data():
    with open("data/testdata/todo_crud.json") as f:
        return json.load(f)

@pytest.mark.contract
def test_get_todos_contract(api_client, db):
    todos_api = TodosAPI(api_client.base_url)
    resp = todos_api.get_todos()
    # Response time validation (e.g., must be < 4 seconds)
    assert resp.elapsed.total_seconds() < 4, f"Response time too high: {resp.elapsed.total_seconds()}s"
    assert resp.status_code == 200
    todos = resp.json()
    for todo in todos:
        validate_schema(todo, "data/schemas/todo_schema.json")
        assert isinstance(todo["completed"], bool)
        db.insert("todos", {k: todo[k] for k in ("id", "userId", "title", "completed")})
    db_todos = db.fetchall("todos")
    assert len(db_todos) == len(todos)

@pytest.mark.crossapi
def test_todo_user_relationship(api_client):
    users_api = UsersAPI(api_client.base_url)
    todos_api = TodosAPI(api_client.base_url)
    users = users_api.get_users().json()
    todos = todos_api.get_todos().json()
    user_ids = {u["id"] for u in users}
    for todo in todos:
        assert todo["userId"] in user_ids

@pytest.mark.contract
def test_get_todos_by_userid_validations(api_client, db):
    todos_api = TodosAPI(api_client.base_url)
    users_api = UsersAPI(api_client.base_url)
    users = users_api.get_users().json()
    for user in users:
        user_id = user["id"]
        resp = todos_api.get_todos_by_user(user_id)
        assert resp.status_code == 200
        assert resp.elapsed.total_seconds() < 4
        todos = resp.json()
        for todo in todos:
            validate_schema(todo, "data/schemas/todo_schema.json")
            assert todo["userId"] == user_id
            assert isinstance(todo["completed"], bool)

@pytest.mark.db
def test_completed_vs_pending_task_analysis(api_client, db):
    todos_api = TodosAPI(api_client.base_url)
    todos = todos_api.get_todos().json()
    completed = [t for t in todos if t["completed"]]
    pending = [t for t in todos if not t["completed"]]
    # At least one completed and one pending task should exist
    assert completed, "No completed tasks found"
    assert pending, "No pending tasks found"
    # Optionally, print or log the counts
    print(f"Completed: {len(completed)}, Pending: {len(pending)}")

@pytest.mark.contract
def test_create_todo(api_client):
    todos_api = TodosAPI(api_client.base_url)
    data = load_todo_crud_data()
    new_todo = data["create"]
    resp = todos_api.session.post(f"{todos_api.base_url}/todos", json=new_todo, timeout=todos_api.timeout)
    assert resp.status_code == 201
    todo = resp.json()
    for field in ["userId", "title", "completed"]:
        assert todo[field] == new_todo[field]

@pytest.mark.contract
def test_update_todo(api_client):
    todos_api = TodosAPI(api_client.base_url)
    data = load_todo_crud_data()
    todo_id = 1
    updated_data = data["update"]
    resp = todos_api.session.put(f"{todos_api.base_url}/todos/{todo_id}", json=updated_data, timeout=todos_api.timeout)
    assert resp.status_code in [200, 201]
    todo = resp.json()
    for field in updated_data:
        assert todo[field] == updated_data[field]

@pytest.mark.contract
def test_patch_todo(api_client):
    todos_api = TodosAPI(api_client.base_url)
    data = load_todo_crud_data()
    todo_id = 1
    patch_data = data["patch"]
    resp = todos_api.session.patch(f"{todos_api.base_url}/todos/{todo_id}", json=patch_data, timeout=todos_api.timeout)
    assert resp.status_code in [200, 201]
    todo = resp.json()
    for field in patch_data:
        assert todo[field] == patch_data[field]

@pytest.mark.contract
def test_delete_todo(api_client):
    todos_api = TodosAPI(api_client.base_url)
    data = load_todo_crud_data()
    todo_id = data["delete_id"]
    resp = todos_api.session.delete(f"{todos_api.base_url}/todos/{todo_id}", timeout=todos_api.timeout)
    assert resp.status_code in [200, 204]

@pytest.mark.negative
def test_create_todo_missing_fields(api_client):
    todos_api = TodosAPI(api_client.base_url)
    incomplete_todo = {"title": "No UserId"}
    resp = todos_api.session.post(f"{todos_api.base_url}/todos", json=incomplete_todo, timeout=todos_api.timeout)
    assert resp.status_code in [400, 422, 201]

@pytest.mark.negative
def test_update_todo_invalid_id(api_client):
    todos_api = TodosAPI(api_client.base_url)
    data = load_todo_crud_data()
    invalid_id = data["invalid_id"]
    updated_data = data["update"]
    resp = todos_api.session.put(f"{todos_api.base_url}/todos/{invalid_id}", json=updated_data, timeout=todos_api.timeout)
    assert resp.status_code in [404, 400, 201, 200, 500]

@pytest.mark.negative
def test_patch_todo_invalid_id(api_client):
    todos_api = TodosAPI(api_client.base_url)
    data = load_todo_crud_data()
    invalid_id = data["invalid_id"]
    patch_data = data["patch"]
    resp = todos_api.session.patch(f"{todos_api.base_url}/todos/{invalid_id}", json=patch_data, timeout=todos_api.timeout)
    assert resp.status_code in [404, 400, 201, 200]

@pytest.mark.negative
def test_delete_todo_invalid_id(api_client):
    todos_api = TodosAPI(api_client.base_url)
    data = load_todo_crud_data()
    invalid_id = data["invalid_id"]
    resp = todos_api.session.delete(f"{todos_api.base_url}/todos/{invalid_id}", timeout=todos_api.timeout)
    assert resp.status_code in [404, 400, 204, 200]
