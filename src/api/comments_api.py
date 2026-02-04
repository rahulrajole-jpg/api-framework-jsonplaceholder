from .base_client import BaseClient

# OOP Concept: Inheritance - CommentsAPI inherits from BaseClient
class CommentsAPI(BaseClient):
    # OOP Concept: Encapsulation - Methods encapsulate comment-related API logic
    def get_comments(self):
        return self.get("/comments")

    def get_comments_by_post(self, post_id):
        return self.get("/comments", params={"postId": post_id})

    # OOP Concept: Abstraction - These methods abstract HTTP operations for comments
    # OOP Concept: Polymorphism - Can override BaseClient methods if needed
    def create_comment(self, data):
        return self.post("/comments", json=data)

    def update_comment(self, comment_id, data):
        return self.put(f"/comments/{comment_id}", json=data)

    def patch_comment(self, comment_id, data):
        return self.patch(f"/comments/{comment_id}", json=data)

    def delete_comment(self, comment_id):
        return self.delete(f"/comments/{comment_id}")
