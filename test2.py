from time import sleep


def timer(func):
    """@timer decorator"""
    from functools import wraps
    from time import time

    @wraps(func)  # sets return meta to fn meta
    def wrapper(*args, **kwargs):
        start = time()
        ret = func(*args, **kwargs)
        dur = format((time() - start) * 1000, ".2f")
        arg_str = ', '.join([str(arg) for arg in args]
                            + [k+"="+v for k, v in kwargs.items()])
        print('%s(%s) -> %sms.' % (func.__name__, arg_str, dur))
        return ret
    return wrapper


class Head:
    from_addr = None
    from_name = None
    to_addr = None
    to_name = None

if __name__ == '__main__':
    head = Head()
    head.from_addr = "Bla"
    print(head.from_addr)
