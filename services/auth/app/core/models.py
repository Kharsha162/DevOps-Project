class User:
    def __init__(self, user_id, username, email, hashed_password, role="user"):
        self.id = user_id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role
        }
