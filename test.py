from models import User
from server import Request


def test_new():
    form = dict(
        username='test',
        password='123',
    )

    u = User.new(form)
    u.save()
    print('test new', u)


def test_all():
    us = User.all()
    print('test all', us)


def test_validate_login():
    # 数据清理
    with open(User.db_path(), 'w') as f:
        f.write('[]')

    # 数据准备
    form = dict(
        username='test2',
        password='123456789',
    )
    u = User.new(form)

    assert u.validate_login() is False

    u.save()
    assert u.validate_login() is True


def test_headers_from_request():
    # 数据准备
    s = 'GET / HTTP/1.1\r\nHost: localhost:3000\r\nContent-Type: text/html\r\n'
    r = Request(s)
    h = r.headers_from_request()

    assert h['Host'] == 'localhost:3000'
    assert h['Content-Type'] == 'text/html'


if __name__ == '__main__':
    test_validate_login()
