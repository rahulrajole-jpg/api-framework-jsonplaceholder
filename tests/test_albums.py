import pytest
from src.api.albums_api import AlbumsAPI
from src.api.users_api import UsersAPI
from src.utils.schema_validator import validate_schema

@pytest.mark.contract
def test_get_albums_contract(api_client, db):
    albums_api = AlbumsAPI(api_client.base_url)
    resp = albums_api.get_albums()
    # Response time validation (e.g., must be < 12 seconds)
    assert resp.elapsed.total_seconds() < 12, f"Response time too high: {resp.elapsed.total_seconds()}s"
    assert resp.status_code == 200
    albums = resp.json()
    for album in albums:
        validate_schema(album, "data/schemas/album_schema.json")
        db.insert("albums", {k: album[k] for k in ("id", "userId", "title")})
    db_albums = db.fetchall("albums")
    assert len(db_albums) == len(albums)

@pytest.mark.contract
def test_get_albums_by_userid_validations(api_client, db):
    albums_api = AlbumsAPI(api_client.base_url)
    users_api = UsersAPI(api_client.base_url)
    users = users_api.get_users().json()
    for user in users:
        user_id = user["id"]
        resp = albums_api.get_albums_by_user(user_id)
        assert resp.status_code == 200
        assert resp.elapsed.total_seconds() < 16
        albums = resp.json()
        for album in albums:
            validate_schema(album, "data/schemas/album_schema.json")
            assert album["userId"] == user_id

@pytest.mark.crossapi
def test_album_user_relationship(api_client):
    users_api = UsersAPI(api_client.base_url)
    albums_api = AlbumsAPI(api_client.base_url)
    users = users_api.get_users().json()
    albums = albums_api.get_albums().json()
    user_ids = {u["id"] for u in users}
    for album in albums:
        assert album["userId"] in user_ids
