# -*- coding: utf-8 -*-
##
## This file is part of End-to-End Latency Analysis Framework (EELAF).
## Copyright (C) 2012, 2013 Jiri Kuncar <jiri.kuncar@gmail.com>.
##
## Analysis framework is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Analysis framework is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Helper functions for EELAF."""

from functools import partial


def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """Return lowest common multiple."""
    return a * b // gcd(a, b)


def lcmm(*args):
    """Return lcm of args."""
    return reduce(lcm, args)


##
## The code bellow is borrowed from various sources and under different
## licences. Many thanks to the original authors.
##
## class            | author         | licence
## -----------------+----------------+---------------
## memoize          | Daniel Miller  | MIT
## cached_property  | Dan McGee      | Content Copyright © 2007-2013, Dan McGee
##


class memoize(object):
    """cache the return value of a method

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.

    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:

    class Obj(object):
        @memoize
        def add_to(self, arg):
            return self + arg

    Obj.add_to(1) # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached

    .. codeauthor:: Daniel Miller
    .. seealso:: http://code.activestate.com/recipes/577452-a-memoize-decorator-for-instance-methods/
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)

    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res


class cached_property(object):
    """A read-only @property that is only evaluated once. The value is cached
    on the object itself rather than the function or class; this should prevent
    memory leakage.

    .. codeauthor:: Dan McGee
    .. seealso:: http://www.toofishes.net/blog/python-cached-property-decorator/
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result
