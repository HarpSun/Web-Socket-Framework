import time


def log(*args, **kwargs):
    time_format = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(time_format, value)
    print(dt, *args, **kwargs)
