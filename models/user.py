from .base import SQLModel


class User(SQLModel):

    def __init__(self, form):
        super().__init__(form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def validate_login(self):
        all_users = self.all()
        for user in all_users:
            if self.username == user.username:
                return self.password == user.password
        return False

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2
