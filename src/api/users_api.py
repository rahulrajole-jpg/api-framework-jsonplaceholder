from .base_client import BaseClient

class UsersAPI(BaseClient):

    def get_users(self):
        return self.get("/users")

    def get_user_by_id(self, user_id):
        return self.get(f"/users/{user_id}")

    def create_user(self, user_data):
        return self.session.post(f"{self.base_url}/users", json=user_data, timeout=self.timeout)

    def update_user(self, user_id, user_data):
        return self.session.put(f"{self.base_url}/users/{user_id}", json=user_data, timeout=self.timeout)

    def patch_user(self, user_id, user_data):
        return self.session.patch(f"{self.base_url}/users/{user_id}", json=user_data, timeout=self.timeout)

    def delete_user(self, user_id):
        return self.session.delete(f"{self.base_url}/users/{user_id}", timeout=self.timeout)
