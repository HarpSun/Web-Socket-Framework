import pymysql

import secret


class SQLModel(object):
    db_name = 'test'

    @classmethod
    def init_connection(cls):
        cls.connection = pymysql.connect(
            host='localhost',
            user='root',
            password=secret.mysql_password,
            db=cls.db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def __init__(self, form):
        self.id = form.get('id', None)

    @classmethod
    def table_name(cls):
        return '`{}`'.format(cls.__name__).lower()

    @classmethod
    def new(cls, form):
        m = cls(form)
        id = cls.insert(m.__dict__)
        m.id = id
        return m

    @classmethod
    def insert(cls, form):
        form.pop('id')
        sql_keys = ', '.join(['`{}`'.format(k) for k in form.keys()])
        sql_values = ', '.join(['%s'] * len(form))
        sql_insert = 'INSERT INTO \n\t{} ({}) \nVALUES \n\t({})'.format(
            cls.table_name(),
            sql_keys,
            sql_values,
        )
        print(sql_insert)

        values = tuple(form.values())

        with cls.connection.cursor() as cursor:
            cursor.execute(sql_insert, values)
            _id = cursor.lastrowid
        cls.connection.commit()

        return _id

    @classmethod
    def delete(cls, id):
        sql_delete = 'DELETE FROM {} WHERE `id`=%s'.format(cls.table_name())
        print(sql_delete)

        with cls.connection.cursor() as cursor:
            cursor.execute(sql_delete, (id,))
        cls.connection.commit()

    @classmethod
    def update(cls, id, **kwargs):
        sql_set = ', '.join(
            ['`{}`=%s'.format(k) for k in kwargs.keys()]
        )
        sql_update = 'UPDATE \n\t{} \nSET \n\t{} \nWHERE `id`=%s'.format(
            cls.table_name(),
            sql_set,
        )
        print(sql_update)

        values = list(kwargs.values())
        values.append(id)
        values = tuple(values)

        with cls.connection.cursor() as cursor:
            cursor.execute(sql_update, values)
        cls.connection.commit()

    @classmethod
    def all(cls, **kwargs):
        sql_where = 'AND'.join(
            ['`{}`=%s'.format(k) for k in kwargs.keys()]
        )
        if sql_where == '':
            sql_select = 'SELECT * FROM \n\t{}'.format(cls.table_name())
        else:
            sql_select = 'SELECT * FROM \n\t{} \n WHERE {}'.format(cls.table_name(), sql_where)
        print('select everything', sql_select)

        values = tuple(kwargs.values())

        ms = []
        with cls.connection.cursor() as cursor:
            cursor.execute(sql_select, values)
            result = cursor.fetchall()
            for row in result:
                m = cls(row)
                ms.append(m)
            return ms

    @classmethod
    def one(cls, **kwargs):
        sql_where = 'AND'.join(
            ['`{}`=%s'.format(k) for k in kwargs.keys()]
        )
        sql_select = 'SELECT * FROM \n\t{} \n WHERE {} \n LIMIT 1'.format(cls.table_name(), sql_where)
        print(sql_select)

        values = tuple(kwargs.values())

        ms = []
        with cls.connection.cursor() as cursor:
            cursor.execute(sql_select, values)
            result = cursor.fetchone()
            if result is None:
                return None
            else:
                return cls(result)

    @classmethod
    def one_for_id(cls, id):
        sql_select = 'SELECT * FROM \n' \
                     '\t{} \n' \
                     'WHERE id=%s \n' \
                     'LIMIT 1'
        sql_select = sql_select.format(
            cls.table_name()
        )

        print(sql_select)

        with cls.connection.cursor() as cursor:
            cursor.execute(sql_select, (id,))
            result = cursor.fetchone()
            if result is None:
                return None
            else:
                return cls(result)

    @classmethod
    def one_for_username_and_password(cls, username, password):
        sql_select = 'SELECT * FROM \n' \
                     '\t{} \n' \
                     'WHERE \n\tusername=%s AND password=%s \n' \
                     'LIMIT 1'
        sql_select = sql_select.format(
            cls.table_name()
        )

        print(sql_select)

        with cls.connection.cursor() as cursor:
            cursor.execute(sql_select, (username, password))
            result = cursor.fetchone()
            if result is None:
                return None
            else:
                return cls(result)

    def __repr__(self):
        name = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(name, s)


class SimpleUser(SQLModel):
    sql_create = '''
    CREATE TABLE `simpleuser` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `username` VARCHAR(45) NOT NULL,
        `password` CHAR(3) NOT NULL,
        `email` VARCHAR(45) NOT NULL,
        PRIMARY KEY (`id`)
    )'''

    def __init__(self, form):
        super().__init__(form)
        self.username = form['username']
        self.password = form['password']
        self.email = form['email']


def recreate_database():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=secret.mysql_password,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        cursor.execute(
            'DROP DATABASE IF EXISTS `{}`'.format(
                SQLModel.db_name
            )
        )
        cursor.execute(
            'CREATE DATABASE `{}` DEFAULT CHARACTER SET utf8mb4'.format(
                SQLModel.db_name
            )
        )
        cursor.execute('USE `{}`'.format(SQLModel.db_name))
        cursor.execute(SimpleUser.sql_create)

    connection.commit()
    connection.close()


def test():
    f = dict(
        username='456',
        password='789',
        email='test',
    )
    u = SimpleUser.new(f)
    print('User.new <{}>'.format(u))
    assert u.username == '456'

    us = SimpleUser.all()
    print('User.all <{}>'.format(us))
    assert len(us) >= 0

    u = SimpleUser.one(username='456', password='789')
    print('User.one <{}>'.format(u))
    assert u.username == '456'

    SimpleUser.update(u.id, username='456', email='789')
    u = SimpleUser.one(username='456', password='789')
    print('User.one <{}>'.format(u))
    assert u.username == '456'

    SimpleUser.delete(u.id)
    u = SimpleUser.one(username='456', password='123')
    print('User.one <{}>'.format(u))
    assert u is None


if __name__ == '__main__':
    recreate_database()
    SQLModel.init_connection()
    test()
