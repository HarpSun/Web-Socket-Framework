from .base import SQLModel


class Message(SQLModel):
    sql_create = '''
        CREATE TABLE `message` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `message` VARCHAR(200) NOT NULL,
            `author` VARCHAR(60) NOT NULL,
            PRIMARY KEY (`id`)
        )'''

    def __init__(self, form):
        super().__init__(form)
        self.message = form.get('message', '')
        self.author = form.get('author', '')
