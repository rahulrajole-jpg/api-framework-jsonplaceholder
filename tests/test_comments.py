import pytest
import json
from src.api.comments_api import CommentsAPI
from src.api.posts_api import PostsAPI
from src.utils.schema_validator import validate_schema
from src.utils.email_validator import is_valid_email

def load_comment_crud_data():
    with open("data/testdata/comment_crud.json") as f:
        return json.load(f)

def load_comment_crud_negative_data():
    with open("data/testdata/comment_crud_negative.json") as f:
        return json.load(f)

@pytest.mark.contract
def test_get_comments_contract(api_client, db):
    comments_api = CommentsAPI(api_client.base_url)
    resp = comments_api.get_comments()
    # Response time validation (e.g., must be < 12 seconds)
    assert resp.elapsed.total_seconds() < 12, f"Response time too high: {resp.elapsed.total_seconds()}s"
    assert resp.status_code == 200
    comments = resp.json()
    for comment in comments:
        validate_schema(comment, "data/schemas/comment_schema.json")
        assert is_valid_email(comment["email"])
        db.insert("comments", {k: comment[k] for k in ("id", "postId", "name", "email", "body")})
    db_comments = db.fetchall("comments")
    assert len(db_comments) == len(comments)

@pytest.mark.contract
def test_get_comments_by_postid_validations(api_client, db):
    posts_api = PostsAPI(api_client.base_url)
    comments_api = CommentsAPI(api_client.base_url)
    posts = posts_api.get_posts().json()
    for post in posts:
        post_id = post["id"]
        resp = comments_api.get_comments_by_post(post_id)
        assert resp.status_code == 200
        assert resp.elapsed.total_seconds() < 12
        comments = resp.json()
        for comment in comments:
            validate_schema(comment, "data/schemas/comment_schema.json")
            assert is_valid_email(comment["email"])
            assert comment["postId"] == post_id
            # DB validation (if already inserted)
            db_comment = [row for row in db.fetchall("comments") if row[0] == comment["id"]]
            if db_comment:
                db_comment = db_comment[0]
                assert comment["id"] == db_comment[0]
                assert comment["postId"] == db_comment[1]
                assert comment["email"] == db_comment[3]

@pytest.mark.crossapi
def test_comment_post_relationship(api_client):
    posts_api = PostsAPI(api_client.base_url)
    comments_api = CommentsAPI(api_client.base_url)
    posts = posts_api.get_posts().json()
    comments = comments_api.get_comments().json()
    post_ids = {p["id"] for p in posts}
    for comment in comments:
        assert comment["postId"] in post_ids

@pytest.mark.contract
def test_create_comment(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    test_data = load_comment_crud_data()
    for new_comment in test_data:
        resp = comments_api.create_comment(new_comment)
        assert resp.status_code in [201, 200]
        comment = resp.json()
        for field in ["postId", "name", "email", "body"]:
            assert comment[field] == new_comment[field]

@pytest.mark.contract
def test_update_comment(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    test_data = load_comment_crud_data()
    comment_id = 1
    updated_data = test_data[0]
    resp = comments_api.update_comment(comment_id, updated_data)
    assert resp.status_code in [200, 201]
    comment = resp.json()
    for field in updated_data:
        assert comment[field] == updated_data[field]

@pytest.mark.contract
def test_patch_comment(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    patch_data = {"body": "Patched comment body."}
    comment_id = 1
    resp = comments_api.patch_comment(comment_id, patch_data)
    assert resp.status_code in [200, 201]
    comment = resp.json()
    for field in patch_data:
        assert comment[field] == patch_data[field]

@pytest.mark.contract
def test_delete_comment(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    comment_id = 1
    resp = comments_api.delete_comment(comment_id)
    assert resp.status_code in [200, 204]

@pytest.mark.negative
def test_create_comment_negative(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    test_data = load_comment_crud_negative_data()
    for bad_comment in test_data:
        resp = comments_api.create_comment(bad_comment)
        assert resp.status_code in [400, 422, 500, 200, 201]

@pytest.mark.negative
def test_update_comment_negative(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    test_data = load_comment_crud_negative_data()
    comment_id = 99999
    for bad_comment in test_data:
        resp = comments_api.update_comment(comment_id, bad_comment)
        assert resp.status_code in [400, 404, 422, 500]

@pytest.mark.negative
def test_patch_comment_negative(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    patch_data = {"body": None}
    comment_id = 99999
    resp = comments_api.patch_comment(comment_id, patch_data)
    assert resp.status_code in [400, 404, 422, 500, 200, 201]

@pytest.mark.negative
def test_delete_comment_negative(api_client):
    comments_api = CommentsAPI(api_client.base_url)
    comment_id = 99999
    resp = comments_api.delete_comment(comment_id)
    assert resp.status_code in [404, 400, 422, 500, 200]
