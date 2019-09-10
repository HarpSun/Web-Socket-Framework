from .base import SQLModel


class Message(SQLModel):

    def __init__(self, form):
        super().__init__(form)
        self.message = form.get('message', '')
        self.author = form.get('author', '')
