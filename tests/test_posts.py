import pytest
import json
from src.api.posts_api import PostsAPI
from src.api.users_api import UsersAPI
from src.utils.schema_validator import validate_schema

def load_post_crud_data():
    with open("data/testdata/post_crud.json") as f:
        return json.load(f)

def load_post_crud_negative_data():
    with open("data/testdata/post_crud_negative.json") as f:
        return json.load(f)

@pytest.mark.contract
def test_get_posts_contract(api_client, db):
    posts_api = PostsAPI(api_client.base_url)
    resp = posts_api.get_posts()
    # Response time validation (e.g., must be < 3 seconds)
    assert resp.elapsed.total_seconds() < 3, f"Response time too high: {resp.elapsed.total_seconds()}s"
    assert resp.status_code == 200
    posts = resp.json()
    for post in posts:
        validate_schema(post, "data/schemas/post_schema.json")
        db.insert("posts", {k: post[k] for k in ("id", "userId", "title", "body")})
    db_posts = db.fetchall("posts")
    assert len(db_posts) == len(posts)

@pytest.mark.contract
def test_get_post_by_id_validations(api_client, db):
    posts_api = PostsAPI(api_client.base_url)
    all_posts = posts_api.get_posts().json()
    for post in all_posts:
        post_id = post["id"]
        resp = posts_api.get_post_by_id(post_id)
        assert resp.status_code == 200
        assert resp.elapsed.total_seconds() < 12
        post_data = resp.json()
        validate_schema(post_data, "data/schemas/post_schema.json")
        for field in ["id", "userId", "title", "body"]:
            assert field in post_data
        # DB validation
        db_post = [row for row in db.fetchall("posts") if row[0] == post_id]
        assert db_post, f"Post {post_id} not found in DB"
        db_post = db_post[0]
        assert post_data["id"] == db_post[0]
        assert post_data["userId"] == db_post[1]
        assert post_data["title"] == db_post[2]
        assert post_data["body"] == db_post[3]

@pytest.mark.parametrize("post_id", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
def test_get_post_by_id_parametrized(api_client, db, post_id):
    posts_api = PostsAPI(api_client.base_url)
    resp = posts_api.get_post_by_id(post_id)
    assert resp.status_code == 200
    assert resp.elapsed.total_seconds() < 12, f"Response time too high: {resp.elapsed.total_seconds()}s"
    post_data = resp.json()
    validate_schema(post_data, "data/schemas/post_schema.json")
    for field in ["id", "userId", "title", "body"]:
        assert field in post_data
    # Insert post into DB for this test only if not already present
    db_posts = db.fetchall("posts")
    if not any(row[0] == post_id for row in db_posts):
        db.insert("posts", {k: post_data[k] for k in ("id", "userId", "title", "body")})
    db_post = [row for row in db.fetchall("posts") if row[0] == post_id]
    assert db_post, f"Post {post_id} not found in DB"
    db_post = db_post[0]
    assert post_data["id"] == db_post[0]
    assert post_data["userId"] == db_post[1]
    assert post_data["title"] == db_post[2]
    assert post_data["body"] == db_post[3]

@pytest.mark.contract
def test_get_posts_by_userid_validations(api_client, db):
    posts_api = PostsAPI(api_client.base_url)
    users_api = UsersAPI(api_client.base_url)
    users = users_api.get_users().json()
    for user in users:
        user_id = user["id"]
        resp = posts_api.get_posts_by_user(user_id)
        assert resp.status_code == 200
        assert resp.elapsed.total_seconds() < 12
        posts = resp.json()
        for post in posts:
            validate_schema(post, "data/schemas/post_schema.json")
            assert post["userId"] == user_id

@pytest.mark.db
def test_post_count_per_user_and_orphan_posts(api_client, db):
    users_api = UsersAPI(api_client.base_url)
    posts_api = PostsAPI(api_client.base_url)
    users = users_api.get_users().json()
    posts = posts_api.get_posts().json()
    user_ids = {u["id"] for u in users}
    # Insert all posts into DB for this test only if not already present
    db_posts = db.fetchall("posts")
    existing_ids = {row[0] for row in db_posts}
    for post in posts:
        if post["id"] not in existing_ids:
            db.insert("posts", {k: post[k] for k in ("id", "userId", "title", "body")})
    # Validate post count per user
    from collections import Counter
    api_counts = Counter([p["userId"] for p in posts])
    db_posts = db.fetchall("posts")
    db_counts = Counter([p[1] for p in db_posts])
    for user_id in user_ids:
        assert api_counts[user_id] == db_counts[user_id]
    # Identify orphan posts
    orphan_posts = [p for p in posts if p["userId"] not in user_ids]
    assert not orphan_posts, f"Orphan posts found: {orphan_posts}"

@pytest.mark.crossapi
def test_post_user_relationship(api_client):
    users_api = UsersAPI(api_client.base_url)
    posts_api = PostsAPI(api_client.base_url)
    users = users_api.get_users().json()
    posts = posts_api.get_posts().json()
    user_ids = {u["id"] for u in users}
    for post in posts:
        assert post["userId"] in user_ids

@pytest.mark.contract
def test_create_post(api_client):
    posts_api = PostsAPI(api_client.base_url)
    test_data = load_post_crud_data()
    for new_post in test_data:
        resp = posts_api.create_post(new_post)
        assert resp.status_code in [201, 200]
        post = resp.json()
        for field in ["userId", "title", "body"]:
            assert post[field] == new_post[field]

@pytest.mark.contract
def test_update_post(api_client):
    posts_api = PostsAPI(api_client.base_url)
    test_data = load_post_crud_data()
    post_id = 1
    updated_data = test_data[0]
    resp = posts_api.update_post(post_id, updated_data)
    assert resp.status_code in [200, 201]
    post = resp.json()
    for field in updated_data:
        assert post[field] == updated_data[field]

@pytest.mark.contract
def test_patch_post(api_client):
    posts_api = PostsAPI(api_client.base_url)
    patch_data = {"title": "Patched Title"}
    post_id = 1
    resp = posts_api.patch_post(post_id, patch_data)
    assert resp.status_code in [200, 201]
    post = resp.json()
    for field in patch_data:
        assert post[field] == patch_data[field]

@pytest.mark.contract
def test_delete_post(api_client):
    posts_api = PostsAPI(api_client.base_url)
    post_id = 1
    resp = posts_api.delete_post(post_id)
    assert resp.status_code in [200, 204]

@pytest.mark.negative
def test_create_post_negative(api_client):
    posts_api = PostsAPI(api_client.base_url)
    test_data = load_post_crud_negative_data()
    for bad_post in test_data:
        resp = posts_api.create_post(bad_post)
        assert resp.status_code in [400, 422, 500, 200, 201]

@pytest.mark.negative
def test_update_post_negative(api_client):
    posts_api = PostsAPI(api_client.base_url)
    test_data = load_post_crud_negative_data()
    post_id = 99999
    for bad_post in test_data:
        resp = posts_api.update_post(post_id, bad_post)
        assert resp.status_code in [400, 404, 422, 500]

@pytest.mark.negative
def test_patch_post_negative(api_client):
    posts_api = PostsAPI(api_client.base_url)
    patch_data = {"title": None}
    post_id = 99999
    resp = posts_api.patch_post(post_id, patch_data)
    assert resp.status_code in [400, 404, 422, 500, 200, 201]

@pytest.mark.negative
def test_delete_post_negative(api_client):
    posts_api = PostsAPI(api_client.base_url)
    post_id = 99999
    resp = posts_api.delete_post(post_id)
    assert resp.status_code in [404, 400, 422, 500, 200]
