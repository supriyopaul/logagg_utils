import collections
from operator import attrgetter

from six import iteritems
from deeputil import Dummy

DUMMY = Dummy()


def memoize(f):
    # from: https://goo.gl/aXt4Qy
    # TODO: Test cases
    class memodict(dict):
        __slots__ = ()

        def __missing__(self, key):
            self[key] = ret = f(key)
            return ret
    return memodict().__getitem__


@memoize
def load_object(imp_path):
    '''
    Given a python import path, load the object
    For dynamic imports in a program

    >>> isdir = load_object('os.path.isdir')
    >>> isdir('/tmp')
    True

    >>> num = load_object('numbers.Number')
    >>> isinstance('x', num)
    False
    >>> isinstance(777, num)
    True
    '''
    module_name, obj_name = imp_path.split('.', 1)
    module = __import__(module_name)
    obj = attrgetter(obj_name)(module)

    return obj


import traceback

def log_exception(self, __fn__):
    self.log.exception('error_during_run_Continuing', fn=__fn__.__name__,
                tb=repr(traceback.format_exc()))


from threading import Thread

def start_daemon_thread(target, args=()):
    '''
    Starts a deamon thread for a given target function and arguments
    >>> def hello():
    ...     for i in range(5): print('hello world!')
    >>> th = start_daemon_thread(hello).join()
    hello world!
    hello world!
    hello world!
    hello world!
    hello world!
    '''
    th = Thread(target=target, args=args)
    th.daemon = True
    th.start()
    return th


def serialize_dict_keys(d, prefix=""):
    '''
    Returns all the keys in a dictionary.
    >>> from pprint import pprint
    >>> d = {"a": {"b": {"c": 1, "b": 2} } }
    >>> pprint(serialize_dict_keys(d))
    ['a', 'a.b', 'a.b.b', 'a.b.c']
    '''
    keys = []
    for k, v in iteritems(d):
        fqk = '%s%s' % (prefix, k)
        keys.append(fqk)
        if isinstance(v, dict):
            keys.extend(serialize_dict_keys(v, prefix="%s." % fqk))

    return keys


class MarkValue(str): pass

def flatten_dict(d, parent_key='', sep='.',
                    ignore_under_prefixed=True, mark_value=True):
    '''
    For a given dictionary, flattens the structure

    >>> from pprint import pprint
    >>> fd = flatten_dict({"a": {"b": {"c": 1, "b": 2, "__d": 'ignore', "_e": "mark"} } })
    >>> pprint(fd)
    {'a.b._e': "'mark'", 'a.b.b': 2, 'a.b.c': 1}
    '''
    items = {}
    for k in d:
        if ignore_under_prefixed and k.startswith('__'):
            continue
        v = d[k]
        if mark_value and k.startswith('_') and not k.startswith('__'):
            v = MarkValue(repr(v))

        new_key = sep.join((parent_key, k)) if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.update(flatten_dict(v, new_key, sep=sep,
                                        ignore_under_prefixed=True,
                                        mark_value=True)
                            )
        else:
            items[new_key] = v
    return items


import numbers

def is_number(x):
    '''
    >>> is_number('45')
    False
    >>> is_number(45)
    True
    >>> is_number(45.0)
    True
    >>> is_number(45/56)
    True
    '''
    return isinstance(x, numbers.Number)


from re import match

spaces = (' ', '\t', '\n')
def ispartial(x):
    '''
    If log line starts with a space it is recognized as a partial line
    >>> ispartial('<time> <event> <some_log_line>')
    False
    >>> ispartial(' <space> <traceback:> <some_line>')
    True
    >>> ispartial('         <tab> <traceback:> <some_line>')
    True
    >>> ispartial('   <white_space> <traceback:> <some_line>')
    True
    >>> ispartial('')
    False
    '''
    try:
        if x[0] in spaces:
            return True
    except IndexError:
        return False
    else:
        return False

from os import path, makedirs

def ensure_dir(dir_path):
    '''
    >>> import os
    >>> dir = '/tmp/orange/apple/banana'
    >>> os.path.isdir(dir)
    False
    >>> os.path.isdir(dir)
    False
    >>> ensure_dir(dir)
    '/tmp/orange/apple/banana'
    >>> os.path.isdir('/tmp/orange')
    True
    >>> os.path.isdir('/tmp/orange/apple')
    True
    >>> os.path.isdir('/tmp/orange/apple/banana')
    True
    '''
    if not path.exists(dir_path):
        makedirs(dir_path)
    return dir_path
