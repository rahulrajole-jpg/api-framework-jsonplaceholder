from .base_client import BaseClient

class AlbumsAPI(BaseClient):
    def get_albums(self):
        return self.get("/albums")

    def get_albums_by_user(self, user_id):
        return self.get("/albums", params={"userId": user_id})
