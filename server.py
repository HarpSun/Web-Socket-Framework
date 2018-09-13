import socket
import urllib.parse
import _thread
from utils import log
from routes import error
from routes import route_dict


class Request(object):
    def __init__(self, r):
        self.raw_data = r
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f

    def headers_from_request(self):
        r = self.raw_data
        headers = r.split('\r\n\r\n', 1)[0]
        header_list = headers.split('\r\n')
        header_dict = {}
        for args in header_list[1:]:
            k, v = args.split(':')
            header_dict[k] = v
        return header_dict


def parsed_path(path):
    """
    输入: /gua?message=hello&author=gua
    返回
    (/gua, {
        'message': 'hello',
        'author': 'gua',
    })
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        query_string = path[index + 1:]
        p = path[:index]
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return p, query


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了
        if len(r) < buffer_size:
            request = request.decode()
            log('request\n {}'.format(request))
            return request


def response_for_request(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    request.path, request.query = parsed_path(request.path)
    r = route_dict()
    response = r.get(request.path, error)
    return response(request)


def procecss_connection(connection):
    with connection:
        r = request_from_connection(connection)
        # 判断是否是空请求
        if len(r) > 0:
            request = Request(r)
            request.raw_data = r
            header, request.body = r.split('\r\n\r\n', 1)

            h = header.split('\r\n')
            parts = h[0].split()
            request.path = parts[1]
            request.method = parts[0]
            # 获取path 对应的响应内容
            response = response_for_request(request)
            connection.sendall(response)
        else:
            connection.sendall(b'')
            log('接收到了一个空请求')


def run(host, port):
    """
    启动服务器
    """
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('ip <{}>\n'.format(address))
            _thread.start_new_thread(procecss_connection, (connection,))


if __name__ == '__main__':
    config = dict(
        host='localhost',
        port=3000,
    )
    run(**config)
