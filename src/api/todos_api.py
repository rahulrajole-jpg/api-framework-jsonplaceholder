from .base_client import BaseClient

class TodosAPI(BaseClient):
    def get_todos(self):
        return self.get("/todos")

    def get_todos_by_user(self, user_id):
        return self.get("/todos", params={"userId": user_id})
