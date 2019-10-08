"""@timer decorator"""
import sys
import logging
__all__ = ('timer')


def timer(func):
    """@timer decorator
    :TODO: option to shorten args at output
    """
    from functools import wraps
    from time import time

    @wraps(func)  # sets return meta to func meta
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        duration = format((time() - start) * 1000, ".2f")
        log = LogEntry(func, duration, result, *args, **kwargs)
        mode = log.choose_mode()
        if mode == 'test':
            logging.info(log.long(with_result=True))

        elif mode == 'wsgi':
            logging.info(log.short(with_result=False))

        elif mode in ('django', 'main'):
            print(log.long(with_result=True))

        return result
    return wrapper


class LogEntry:
    """Class that represents a Log entry"""
    MODES = ('test', 'wsgi', 'main', 'django')

    def __init__(self, func, duration, result, *args, **kwargs):
        self._func = func
        self._duration = duration
        self.result = result
        self._args = args
        self._kwargs = kwargs

    def short(self, with_result=False):
        """short version of the log message
        Args:
            with_result(bool, optional): append function result to log

        Returns:
            str: log entry
        """
        return self.to_string(short=True, with_result=with_result)

    def long(self, with_result=False):
        """long version of the log message
        Args:
            with_result(bool, optional): append function result to log

        Returns:
            str: log entry
        """
        return self.to_string(short=False, with_result=with_result)

    @property
    def args(self):
        """parse args
        :returns: args as list of strings
        """
        return [str(arg) for arg in self._args]

    @property
    def kwargs_long(self):
        """kwargs as long version"""
        return self.kwargs_list()

    @property
    def kwargs_short(self):
        """kwargs as short version"""
        return self.kwargs_list(short=True)

    def kwargs_list(self, short=False):
        """parse kwargs
        :param truncate: should the output of values be shortened?
        :returns: kwargs as list of strings
        """
        if short:
            return ['{}={}'.format(str(key), self.shorten_string(str(value)))
                    for key, value in self._kwargs.items()]
        return ['{}={}'.format(str(key), str(value))
                for key, value in self._kwargs.items()]

    def to_string(self, short=False, with_result=False):
        """creates the string to enter in logs

        Args:
            short(bool, optional): use short version
            with_result(bool, optional): append result of function call to log

        Returns:
            str: log entry as string
        """
        args_and_kwargs_str = ', '.join(
            self.args +
            self.kwargs_short if short else self.kwargs_long,
            )
        result_string = '{}({}) -> {}ms.'.format(
            self._func.__name__, args_and_kwargs_str, self._duration
            )
        if with_result:
            result_string += '  >>> {} <<<'.format(
                self.shorten_string(str(self.result)) if short else self.result
                )
        return result_string

    @staticmethod
    def choose_mode():
        """possible_modes 'test', 'wsgi', 'main', 'django'
        :returns: mode as string
        """
        mode = None
        if sys.argv[0] == 'mod_wsgi':
            mode = 'wsgi'
        elif sys.argv[0] == 'main.py':
            mode = 'main'
        elif sys.argv[0] == 'run_tests.py' or 'unittest' in sys.argv[0]:
            mode = 'test'
        elif len(sys.argv) >= 2:
            if sys.argv[1] == 'test':  # needed?
                mode = 'test'
            elif sys.argv[1] == 'runserver':
                mode = 'django'
        if not mode:
            raise AttributeError('No mode found')
        return mode

    @staticmethod
    def shorten_string(text_str, max_chars=50, replace=' <...> '):
        """shorten a text string to maximal ammount of chars
        :param text_str: string to shorten
        :param max_chars: (optional) limit text_str to these ammount of chars
        :param replace: (optional) replace cutted with this string
        """
        if not isinstance(text_str, str):
            raise AttributeError(str(text_str) + ' is not a string')
        if len(text_str) > max_chars + len(replace):
            text_str = '{}{}{}'.format(
                text_str[:int(max_chars / 2 + 1.5)-1],
                replace,
                text_str[-int(max_chars / 2):],
                )
        return text_str

    def __str__(self):
        return self.long
