import hashlib

from .base import SQLModel


class User(SQLModel):
    sql_create = '''
        CREATE TABLE `user` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `username` VARCHAR(45) NOT NULL,
            `password` CHAR(64) NOT NULL,
            PRIMARY KEY (`id`)
        )'''

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

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        """$!@><?>HUI&DWQa`"""
        salted = password + salt
        hash_ = hashlib.sha256(salted.encode('ascii')).hexdigest()
        return hash_

    @classmethod
    def register(cls, form):
        valid = len(form['username']) > 2 and len(form['password']) > 2
        if valid:
            form['password'] = cls.salted_password(form['password'])
            u = User.new(form)
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
            return u, result
        else:
            result = '用户名或者密码长度必须大于2'
            return result
