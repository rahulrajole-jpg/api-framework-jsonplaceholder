from .base_client import BaseClient

# OOP Concept: Inheritance - PostsAPI inherits from BaseClient
class PostsAPI(BaseClient):
    # OOP Concept: Encapsulation - Methods encapsulate post-related API logic
    def get_posts(self):
        return self.get("/posts")

    def get_post_by_id(self, post_id):
        return self.get(f"/posts/{post_id}")

    def get_posts_by_user(self, user_id):
        return self.get("/posts", params={"userId": user_id})

    # OOP Concept: Abstraction - These methods abstract HTTP operations for posts
    # OOP Concept: Polymorphism - Can override BaseClient methods if needed
    def create_post(self, data):
        return self.post("/posts", json=data)

    def update_post(self, post_id, data):
        return self.put(f"/posts/{post_id}", json=data)

    def patch_post(self, post_id, data):
        return self.patch(f"/posts/{post_id}", json=data)

    def delete_post(self, post_id):
        return self.delete(f"/posts/{post_id}")
