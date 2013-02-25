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

"""End-to-End Latency Analysis Framework

.. moduleauthor:: Jiri Kuncar <jiri.kuncar@gmail.com>
.. moduleauthor:: Rafia Inam <rafia.inam@mdh.se>
"""

__version__ = '0.2'
__release__ = '0.2-alpha'

from math import ceil
import copy
import numpy as np
from functools import partial


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
    .. seealso: http://www.toofishes.net/blog/python-cached-property-decorator/
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


class System(object):
    """Models a physical system with instances of :class:`~analysis.Component`."""

    def __init__(self, scheduler='FPS', resolution=1000, components=None):
        self.components = []
        if components is not None:
            for c in components:
                self.addComponent(c)
        self.resolution = resolution
        self.scheduler = scheduler
        self.path = None

    def __str__(self):
        return "<System '%s' \n\t%s\n>" % (self.scheduler,
            '\n\t'.join(map(str, self.components)))

    def __deepcopy__(self, memo):
        dup = System(copy.copy(self.scheduler), copy.copy(self.resolution))
        memo[self] = dup
        for c in self.components:
            dup.addComponent(copy.deepcopy(c))
        return dup

    def t(self, i):
        """Get `i`-th :class:`~analysis.Task` instance (:math:`t_i`).

        :param i: The index of system task starting from 0.
        :returns: Instance of :class:`~analysis.Task`.
        """
        if self.path is None:
            return self.tasks[i]
        else:
            return self.tasks[self.path[i]]

    def addComponent(self, component):
        """Adds new :class:`~analysis.Component` instance to the system.

        It stores reference of the system to added component.

        :param component: New system subsystem.
        :type component: :class:`Component`
        """
        if component in self.components:
            raise Exception('Component already exists in the system')
        self.components.append(component)
        component.system = self

    @cached_property
    #@property
    def tasks(self):
        """All system tasks."""
        #for c in self.components:
        #    for t in c.tasks:
        #        yield t
        return [t for c in self.components for t in c.tasks]

    @cached_property
    #@property
    def tasks_in_path(self):
        """List of tasks in data path."""
        if self.path is None:
            return self.tasks
        else:
            return [self.t(i) for i in range(len(self.path))]

    def B(self, t):
        """
        Blocking time left at given `time`.

        .. warning::
            Currently always returns 0.
        """
        #FIXME add blocking time calculation
        t = t
        return 0

    @memoize
    def att(self, w, i, r, j):
        """It returns `True` if "activation time travel" occurs
        (:math:`att( t_w (i) \\rightarrow t_r (j))`).

        The activation time travel occurs when the reader is
        activated before the writer (:math:`\\alpha_r(i)` is equivalent to
        :meth:`~analysis.Task.alpha` on :meth:`~analysis.System.t`).

        .. math::
            att( t_w (i) \\rightarrow t_r (j)) = \\alpha_r (j) < \\alpha_w (i)

        :param w: Index of writer task in data path.
        :param i: Activation index of writer task.
        :param r: Index of reader task in data path.
        :param j: Activation index of reader task.

        .. seealso::
            [Feiertag:08]_ formula (3)
        """
        return self.t(r).alpha(j) < self.t(w).alpha(i)

    @memoize
    def crit(self, w, i, r, j):
        """The "critical function" determines if writer and reader
        overlap in execution even in case of non-activation time travel
        (:math:`crit( t_w (i) \\rightarrow t_r (j))`).

        .. math::
            crit( t_w (i) \\rightarrow t_r (j)) = \\alpha_r (j) < \\alpha_w (i) + \\delta_w (i)

        :param w: Index of writer task in data path.
        :param i: Activation index of writer task.
        :param r: Index of reader task in data path.
        :param j: Activation index of reader task.

        .. seealso::
            [Feiertag:08]_ formula (4) """
        return self.t(r).alpha(j) < self.t(w).alpha(i) + self.t(w).delta(i)

    @memoize
    def wait(self, w, i, r, j):
        """It determines if the writer finishes first, because the reader has
        to wait due to its priority in case of overlapped but not time-traveling
        execution (:math:`wait( t_w (i) \\rightarrow t_r (j))`).

        .. math::
            wait( t_w (i) \\rightarrow t_r (j)) = p(t_r) < p(t_w)

        :param w: Index of writer task in data path.
        :param i: Activation index of writer task.
        :param r: Index of reader task in data path.
        :param j: Activation index of reader task.

        .. seealso::
            [Feiertag:08]_ formula (5)
        """
        i, j = i, j
        return self.t(r).priority < self.t(w).priority

    @memoize
    def forw(self, w, i, r, j):
        """It determines the forward reachability of the two
        task instances :math:`t_w` and :math:`t_r`.

        .. math::

            forw( t_w (i) \\rightarrow t_r (j)) = \\neg att( t_w (i)
            \\rightarrow t_r (j)) \\wedge
            ( \\neg crit( t_w (i) \\rightarrow t_r (j)) \\lor
            wait( t_w (i) \\rightarrow t_r (j)))

        :param w: Index of writer task in data path.
        :param i: Activation index of writer task.
        :param r: Index of reader task in data path.
        :param j: Activation index of reader task.

        .. seealso::
            [Feiertag:08]_ formula (6)
        """
        return (not self.att(w, i, r, j)) and \
               (not self.crit(w, i, r, j) or self.wait(w, i, r, j))

    @memoize
    def reach(self, w, i, r, j):
        """The output of an instance :math:`t_w (i)` is overwritten
        by instance :math:`t_w (i+1)` when both instances can forward
        reach the same reading task instance :math:`t_r (j)`.
        In other words, :math:`t_w (i)` can reach :math:`t_r (j)`
        if and only if the following function returns `True`:

        .. math::
            reach( t_w (i) \\rightarrow t_r (j)) = (forw(t_w (i) -> t_r (j)) \\land \\neg forw(t_w (i+1) -> t_r (j)))

        :param w: Index of writer task in data path.
        :param i: Activation index of writer task.
        :param r: Index of reader task in data path.
        :param j: Activation index of reader task.

        .. seealso::
            [Feiertag:08]_ formula (7).
        """
        return self.forw(w, i, r, j) and \
               not self.forw(w, i + 1, r, j)

    @memoize
    def reach_path(self, path):
        """Check `path` rechability.

        .. code-block:: none

            path_length <- length(path)
            for i in [0..path_length-1):
                tp_i  <- path[i]
                tp_i1 <- path[i+1]
                if reach(t_w(tpi) -> t_{w+1}(tp_i1)):
                    return False
                end if
            end for
            return True

        .. seealso::
            [Feiertag:08]_ formula (8).
        """
        for w, path_i in enumerate(path[:-1]):
            if not self.reach(w, path_i, w + 1, path[w + 1]):
                return False
        return True

    def delta_path(self, path):
        """Calculate end-to-end `path` delay.

        .. math::
            \\Delta(path) = \\alpha_n(path_n) + \\delta_n(path_n) - \\alpha_1(path_1)

        .. seealso::
            [Feiertag:08]_ formula (2).
        """
        return self.t(-1).alpha(path[-1]) + self.t(-1).delta(path[-1]) \
               - self.t(0).alpha(path[0])

    def delta_LL_path(self, path):
        """Calculate Last-to-Last `path` delay using :meth:`~System.delta_path`."""
        return self.delta_path(path)

    @memoize
    def TP_reach(self, possible_paths):
        """It obtains the set of all paths and returns only
        all reachable timed path (:math:`\\mathbb{TP}^{reach}`).

        .. code-block:: none

            out <- list()
            for all path in possible_paths:
                if reach_path(path):
                    out.append(path)
                end if
            end for
            return out

        .. seealso::
            [Feiertag:08]_ formula (9).
        """
        #return [l for l in possible_paths if self.reach_path(l)]
        return filter(self.reach_path, possible_paths)

    @memoize
    def delta_LL(self, possible_paths):
        """Returns maximum latency over all reachable paths (:meth:`~analysis.System.TP_reach`).

        .. math::
            \\Delta^{LL}(possible_paths) = max\\{\\Delta(path) \\mid path \\in \\mathbb{TP}^{reach}\\}

        .. code-block:: none

            # map .. calls function for each element in list
            # max .. returns maximal element from list
            return max(map(delta_path, TP_reach(possible_paths)))

        .. seealso::
            [Feiertag:08]_ formula (10).
        """
        #return max([self.delta_path(p) for p in self.TP_reach(possible_paths)])
        return max(map(self.delta_path, self.TP_reach(possible_paths)))

    @memoize
    def TP_first(self, possible_paths):
        """
        Set of all non-duplicate, reachable timed paths,
        for which no timed path exists that shares the same
        start instance of the first task and has an earlier
        end instance of the last task.

        .. math::

            \\mathbb{TP}^{first} = \\{ \\vec{tp} \\in \\mathbb{TP}^{reach}
            \\mid \\neg \\exists \\vec{tp}' \\in \\mathbb{TP}^{reach} :
            tp'_1 = tp_1 \\land tp'_n < tp_n
            \\}

        .. code-block:: none

            function earlier(tp, tp'):
                # index -1 gets last element in array
                return tp'[0] == tp[0] and tp'[-1] < tp[-1]
            end function

            out <- list()
            TP_reach_paths <- TP_reach(possible_paths)
            for tp in TP_reach_paths:
                if not any(map(partial(earlier, tp), TP_reach_paths))):
                    out.append(tp)
                end if
            end for
            return out

        .. seealso::
            [Feiertag:08]_ formula (11).
        """
        from functools import partial
        tp_reach = self.TP_reach(possible_paths)

        def earlier(path, path2):
            return path2[0] == path[0] and path2[-1] < path[-1]

        return tuple(tp for tp in tp_reach
            if not any(map(partial(earlier, tp), tp_reach)))

    @memoize
    def delta_LF(self, ls):
        """The maximum "Last-to-First" timed path delay.

        .. math::
            \\Delta^{LF}(p) = max\\{ \\Delta(\\vec(tp)) \\mid \\vec(tp) \\in \\mathbb{TP}^{first} \\}

        .. seealso::
            [Feiertag:08]_ formula (12).
        """
        out = [self.delta_path(p) for p in self.TP_first(ls)]
        return max(out) if out else 9999

    def pred(self, path, tp_reach):
        """Temporal distance to the start of the latest previous
        "last-to-x" path.

        .. seealso::
            [Feiertag:08]_ formula (13).
        """
        def last_to_x(x):
            return len(filter(lambda p: p[0] == x, tp_reach)) > 0
        out = [m for m in range(0, path[0]) if last_to_x(m)]
        return max(out) if out else 0

    def delta_FL_path(self, path, tp_reach):
        """Calculate First-to-Last path delay (uses :meth:`~analysis.System.pred`).

        .. math::
            \\Delta^{FL}(\\vec{tp}) = \\Delta^{LL}(\\vec{tp}) + \\alpha_1(tp_1) - \\alpha_1(pred(\\vec(tp)))

        :param path: Array with task activation numbers.
        :param tp_reach: List of reachable paths.

        :fixme: remove dependency on `tp_reach` parameter.

        .. seealso::
            [Feiertag:08]_ formula (14).
        """
        return self.delta_LL_path(path) + self.t(0).alpha(path[0]) - \
            self.t(0).alpha(self.pred(path, tp_reach))

    def delta_FL(self, ls):
        """Find maximum of First-to-Last path delays.

        .. seealso::
            [Feiertag:08]_ formula (15).
        """
        tp_reach = self.TP_reach(ls)
        out = [self.delta_FL_path(p, tp_reach) for p in tp_reach]
        return max(out) if out else 9999

    def delta_FF_path(self, path, tp_reach):
        """Calculate First-to-First path delay.

        .. math::
            \\Delta^{FF}(\\vec{tp}) = \\Delta^{LF}(\\vec{tp}) + \\alpha_1(tp_1) - \\alpha_1(pred(\\vec(tp)))

        :param path: Array with task activation numbers.
        :param tp_reach: List of reachable paths.

        :fixme: remove dependency on `tp_reach` parameter.

        .. seealso::
            [Feiertag:08]_ formula (16).
        """
        return self.delta_LF((path, )) + self.t(0).alpha(path[0]) - \
            self.t(0).alpha(self.pred(path, tp_reach))

    def delta_FF(self, ls):
        """Find maximum of First-to-First path delays.

        .. seealso::
            [Feiertag:08]_ formula (17).
        """
        tp_reach = self.TP_reach(ls)
        out = [self.delta_FF_path(p, tp_reach) for p in self.TP_first(ls)]
        return max(out) if out else 9999

    @property
    def schedulability(self):
        """This method checks the global schedulability condition.

        .. code-block:: none

            for C in components:
                # P(C) .. period of component C
                schedulable <- False
                for t in [0..P(C)]:
                    if RBF(C, t) <= t:
                        schedulable <- True
                        break
                    end if
                end for
                if not schedulable:
                    return False
                end if
            end for
            return True

        .. seealso::
            [Inam2548:2011]_ formula (8).
        """
        for C in self.components:
            for t in range(int(C.period + 0.5)):
                if C.RBF(t) <= t:
                    break
            else:
                return False
        return True

    @property
    def utilization_of_components(self):
        return [c.utilization for c in self.components]

    @property
    def utilization(self):
        """
        Returns system utilization calculated as sum of component utilizations.
        """
        return sum(self.utilization_of_components)

    def generate_paths(self, index, start, stop):
        """
        Generator of possible paths for given task in path.

        It yields tuples with task activation index starting from `index`th
        task in defined path.

        .. code-block:: none

            paths <- list()
            task <- tasks_in_path.pop(0)  # assign and remove first task from the path
            loop i from task.ialpha(start) to task.ialpha(stop):
                # find a time range for next task
                if length(tasks_in_path) > 0:
                    time <- task.alpha(i)
                    next_task <- tasks_in_path[0]  # next task in path
                    j <- next_task.ialpha(time)  # closest activation index
                    new_start <- next_tasks.alpha(j)  # closest activation time
                    # find posible paths for next task in path from new start.
                    for all path in generate_paths(new_start, stop, tasks_in_path):
                        # join current activation index with found tuple
                        paths.append( path.prepend(i) )
                    end for
                else:
                    paths.append( list(i) )  # list with only one index
                end if
            end loop
            return paths

        """
        tsk = self.tasks_in_path[index]
        for i in range(tsk.ialpha(start), tsk.ialpha(stop)):
            # find a time range for next task
            if index + 1 < len(self.tasks_in_path):
                t = tsk.alpha(i)
                next_tsk = self.tasks_in_path[index + 1]
                j = next_tsk.ialpha(t)
                new_start = next_tsk.alpha(j)
                for path in self.generate_paths(index + 1, new_start, stop):
                    yield (i, ) + path
            else:
                yield (i, )


class Component(object):
    """
    System servers / components.
    """

    def __init__(self, name, period, priority, budget, scheduler='EDF',
                 payback=False):
        self.name = name
        self.period = period
        self.priority = priority
        self.budget = budget
        self.scheduler = scheduler
        self.tasks = []
        self.payback = payback
        self.system = None

    def __str__(self):
        return "<Component %s, period=%f, priority=%d, budget=%f, \n\t\t%s\n\t>" % \
            (self.name, self.period, self.priority, self.budget,
            '\n\t\t'.join(map(str, self.tasks)))

    def __deepcopy__(self, memo):
        dup = Component(
            copy.copy(self.name),
            copy.copy(self.period),
            copy.copy(self.priority),
            copy.copy(self.budget),
            copy.copy(self.scheduler),
            copy.copy(self.payback)
            )
        memo[self] = dup
        for t in self.tasks:
            dup.addTask(copy.copy(t))
        return dup

    @property
    def X(self):
        """The maximum execution-time that any subsystem-internal task may
        lock a shared global resource.

        .. warning::
            Currently always returns 0.
        """
        return 0

    @property
    def P(self):
        """Alias for :class:`~analysis.Component` period."""
        return self.period

    @property
    def Q(self):
        """Alias for :class:`~analysis.Component` budget."""
        return self.budget

    @property
    def deadline(self):
        """The function returns :class:`~analysis.Component` deadline.

        Currently the `self.deadline==self.period`.
        """
        return self.period

    def addTask(self, task):
        self.tasks.append(task)
        task.component = self

    @property
    def freq(self):
        """The function calculates :class:`~analysis.Component` frequency."""
        return 1.0 / self.period

    def f1(self, t):
        """Implementation of helper formula `f1`.

        :param t: time

        .. seealso::
            [Inam2548:2011]_ formula (5).
        """
        k = max(ceil(float(t - (self.P - self.Q) - self.X) / self.P), 1)
        w_k = (k + 1) * self.P - 2 * self.Q + self.X
        if w_k <= t and t <= w_k + self.Q:
            return t - (k + 1) * (self.P - self.Q) - self.X
        else:
            return (k - 1) * self.Q

    def f2(self, t):
        """Implementation of helper formula `f2`.

        :param t: time

        .. seealso::
            [Inam2548:2011]_ formula (6).
        """
        k = max(ceil(float(t - (self.P - self.Q)) / self.P), 1)
        Vk_min = 2 * self.P - 2 * self.Q
        Vk_max = 2 * self.P - self.Q - self.X
        Zk = (k + 2) * self.P - 2 * self.Q
        if Vk_min <= t and t <= Vk_max:
            return t - 2 * (self.P - self.Q)
        elif Zk <= t and t <= Zk + self.Q:
            return t - (k + 1) * (self.P - self.Q) - self.X
        else:
            return (k - 1) * self.Q - self.X

    @memoize
    def sbf(self, t):
        """Supply Bound Function.

        If `payback` is `True` then this method depends on
        :meth:`~analysis.Component.f1` and :meth:`~analysis.Component.f2`::

            return max(min(f1(t), f2(t)), 0)

        :param t: time

        .. seealso::
            [Inam2548:2011]_ formula (3) and (4).

        """

        if self.payback:
            result = max(min(self.f1(t), self.f2(t)), 0)
        else:
            #k = max(ceil(float(t-(self.deadline -\
            #    self.budget))/self.period), 1)
            #Vk = k*self.period + self.deadline - 2*self.budget
            #if Vk <= t and t <= Vk+self.budget:
            #    result = t-(k+1)*(self.period-self.budget)+\
            #       (self.period-self.deadline)
            #else:
            #    result = (k-1)*self.budget
            k = max(ceil(float(t - (self.P - self.Q)) / self.P), 1)
            w_k = (k + 1) * self.P - 2 * self.Q
            if w_k <= t and t <= w_k + self.Q:
                result = t - (k + 1) * (self.P - self.Q)
            else:
                result = (k - 1) * self.Q
        return result

    @cached_property
    def HPS(self):
        """Set of subsystems of :class:`~analysis.System` `S` with priority higher
        than itself (:math:`S_s`).

        .. math::
            HSP(s) = \\{ S_k \\in S \\mid P(k) > P(s) \\}

        .. seealso::
            Used in formula (9) in [Inam2548:2011]_.
        """
        return [C for C in self.system.components if C.P > self.P]

    @cached_property
    def LPS(self):
        """Set of subsystems of :class:`~analysis.System` `S` with priority lower
        than itself (:math:`S_s`).

        .. math::
            LSP(s) = \\{ S_k \\in S \\mid P(k) < P(s) \\}

        .. seealso::
            Used in formula (10) in [Inam2548:2011]_.
        """
        return [C for C in self.system.components if C.P < self.P]

    @cached_property
    def Bl(self):
        """
        The maximum blocking imposed to a this subsystem.

        .. math::
            Bl(s) = max\\{ X(k) \\mid S_k \\in LPS(s) \\}

        .. seealso::
            [Inam2548:2011]_ formula (10).
        """
        out = [C.X for C in self.LPS]
        return max(out) if len(out) else 0

    def RBF(self, t):
        """Request Bound Function

        .. seealso::
            [Inam2548:2011]_ formula (9) and (11).
        """
        if self.payback:
            out = (self.Q + self.X + self.Bl) + sum(
                [(float(t) / C.P) * (C.Q) + C.X for C in self.HPS])
        else:
            #FIXME ceil
            out = (self.Q + self.X + self.Bl) + sum(
                [(float(t) / C.P) * (C.Q + C.X) for C in self.HPS])
        return out

    @cached_property
    def schedulability(self):
        """:class:`~analysis.Component` schedulability condition.

        .. code-block:: none

            for t in C_{tasks}:
                schedulable <- False
                for i in [1..P(t)]:
                    if rbf_t(i) <= sbf_C(i):
                        schedulable <- True
                        break
                    end if
                end for
                if not schedulable:
                    return False
                end if
            end for
            return True

        .. seealso::
            [Inam2548:2011]_ formula (13).
        """
        for task in self.tasks:
            for i in range(1, task.period + 1):
                t = i * 1.0
                if task.rbf(t) <= self.sbf(t):
                    break
            else:
                return False
        return True

    @property
    def utilization(self):
        """Returns :class:`~analysis.Component` utilization as product of its
        frequency and budget.
        """
        return self.freq * self.budget


class Task(object):
    """System task."""

    def __init__(self, name, period, priority, exetime):
        self.name = name
        self.period = int(period)
        self.priority = priority
        self.exetime = exetime
        self.component = None
        self.start = 0

    def __repr__(self):
        return "<Task %s, priority=%d, exetime=%f, period=%f>" % \
            (self.name, self.priority, self.exetime, self.period)

    def __str__(self):
        return self.__repr__()

    @property
    def p(self):
        """Alias for task :math:`t_i` priority (:math:`p(i)`)."""
        return self.priority

    @property
    def P(self):
        """Alias for task :math:`t_i` period (:math:`P(i)`)."""
        return self.period

    @property
    def C(self):
        """Alias for task :math:`t_i` execution time (:math:`C_i`)."""
        return self.exetime

    @property
    def freq(self):
        """Task frequency :math:`f(t_i) = 1/P(t_i)`."""
        return 1.0 / self.period

    @property
    def deadline(self):
        """Task deadline.

        .. note::
            Currently `deadline==period`.
        """
        return self.period

    @property
    def utilization(self):
        """Calculates utilization."""
        return float(self.exetime) / self.period

    @property
    def HB(self):
        """Set of tasks belonging to same :class:`Component` `C` with
        priorities higher than itself one.

        .. math::
            HB(s) = \\{ T_k \\in C \\mid P(k) > P(s) \\}

        """
        return [T for T in self.component.tasks \
            if T.priority > self.priority]

    @cached_property
    def blocking_time(self):
        """Task deadline (:math:`b_i`).

        .. warning::
            Currently always returns 0.
        """
        #FIXME not working correctly. needs deeper understanding
        #b = (0.005 + 0.005 * random.random()) * self.exetime
        #return b
        return 0

    @memoize
    def rbf(self, t):
        """The request bound function.

        It computes the maximum cumulative execution requests
        that could be generated from the time that
        task is released up to time `t`.

        .. math::

            rbf_i(t) = C_i + b_i + \\sum_{\\tau_k \\in HP(i)} {t\\over{T_k}} * C_k

        :param t: Time limit for execution requests.

        .. seealso::
            [Inam2548:2011]_ formula (2).
        """
        return self.exetime + self.blocking_time + sum([T.exetime * ceil(
            float(t) / T.period) for T in self.HB])

    @cached_property
    def response_time(self):
        """Task response time.

        .. math::

            RS(i) = t \\mid \\exists t : 0 < t <= D_i , rbf_i(t) <= sbf_C(t)

        """
        for i in range(1000 * self.period):
            t = i * 1.0 / 100
            if self.rbf(t) <= self.component.sbf(t):
                return t

    def status(self, time):
        """Returns textual representation of task status at given `time`."""
        return 'R' if (time - self.start) % self.period < self.response_time \
                else '_'

    def plan(self, time):
        """Returns True if the task should be scheduled at given `time`."""
        return (time - self.start) % self.period == 0

    @memoize
    def alpha(self, i):
        """Calculate time of `i`-th activation.

        .. math::

            \\alpha_r(i) = r_{start} + i * P(r)

        :param i: Activation number.
        :returns: Activation time.
        """
        return self.start + i * self.period

    @memoize
    def ialpha(self, t):
        """Calculate previous activation for given time.

        .. math::

            \\alpha^{-1}_r(t) = \\lfloor {t - r_{start}\\over{P(r)}} \\rfloor

        :param t: Current time.
        :returns: int -- activation number.
        """
        return int((t - self.start) * 1.0 / self.period)

    @memoize
    def delta(self, i):
        """Calculate response time of `i`-th activation.

        :param i: Activation number.
        :returns: Response time of `i`-th activation.

        .. note::
            In our case we always return task response time.

        .. seealso::
            :func:`~analysis.Task.response_time`
        """
        i = i
        return self.response_time


def reachability(s, verbose=2):
    ls = tuple(s.generate_paths(0, 0, cargs.time))
    tp_reach = s.TP_reach(ls)
    if verbose > -1:
        print 'Data path:', s.path
        print 'Tasks in data path', s.tasks_in_path
    if verbose > 0:
        print "Number or path:", len(ls)
    if verbose > 1:
        print 'Reach paths:\n', '\n'.join(map(str, tp_reach))
        print 'First paths:\n', '\n'.join(map(str, s.TP_first(ls)))

    FF = s.delta_FF(ls)
    FL = s.delta_FL(ls)
    LF = s.delta_LF(ls)
    LL = s.delta_LL(ls)

    if verbose > -1:
        print 'First-to-First delay:', str(FF)
        print 'First-to-Last delay:', str(FL)
        print 'Last-to-First delay:', str(LF)
        print 'Last-to-Last delay:', str(LL)

    #print FL, ' == ', FF + LL - LF

    if verbose > 1:
        print 'FF', map(lambda p: (p, s.delta_FF_path(p, ls)), tp_reach)
        print 'FL', map(lambda p: (p, s.delta_FL_path(p, ls)), tp_reach)
        print 'LF', map(lambda p: (p, s.delta_path(p)), tp_reach)
        print 'LL', map(lambda p: (p, s.delta_LL_path(p)), tp_reach)
    if verbose > 0:
        system_path = np.array(s.path)
        for i, p in enumerate(tp_reach[:7]):
            print 'Path', p
            for r, tsk in enumerate(s.tasks):
                print tsk.name, ': ',
                p_i = np.where(system_path == r)[0]
                atimes = map(lambda i: p[i], p_i)
                for t in range(0, 800, 10):
                    j = tsk.ialpha(t)
                    show = (j in atimes) and \
                           (t - tsk.alpha(j) <= tsk.response_time)
                    print i if show else tsk.status(t),
                print '|'

    print 'Utilizations:', s.utilization, '=', s.utilization_of_components
    #print [sum([t.freq*t.exetime for t in c.tasks]) for c in s.components]
    print 'Local schedulability:', [c.schedulability for c in s.components]
    print 'Global schedulability:', s.schedulability
    print 'Tasks (period, response time):',
    print [(t.period, t.response_time) for t in s.tasks]


if __name__ == "__main__":
    import argparse
    from lxml import objectify
    parser = argparse.ArgumentParser(description='System generator.')
    parser.add_argument('-t', '--time', metavar='time', default=1000, type=int,
                        help="time interval for analysis")
    parser.add_argument('-p', '--payback',
                        action='store_true', default=False,
                        help="overrun calculation with or without payback")
    parser.add_argument('-f', '--file', metavar='file', required=True,
                        type=argparse.FileType('r'),
                        help='file to process (defaults to component.xml)')
    parser.add_argument('path', metavar='N', type=int, nargs='*',
                        help='define indexes of tasks as a data flow path')

    cargs = parser.parse_args()

    def create_system_from_xml(xml_system, output=True):
        """
        Reads system configuration from param:`xml_system`
        and returns cls:`System` instance.
        """
        system = System(scheduler=xml_system.global_sched,
                        resolution=xml_system.resolution)

        for c in xml_system.iterfind('component'):
            component = Component(c.cname, c.cperiod, c.cpriority,
                                  float(str(c.budget).replace(',', '.')),
                                  c.localsched, cargs.payback)
            system.addComponent(component)
            if output:
                print 'Component:'
                print 'name', 'period', 'budget', 'priority'
                print c.cname, c.cperiod, c.budget, c.cpriority
                print 'Tasks:'
                print 'name', 'period', 'priority', 'execution time'
            for t in c.iterfind('task'):
                if output:
                    print t.tname, t.tperiod, t.tpriority, t.texetime
                component.addTask(Task(t.tname,
                                       float(str(t.tperiod).replace(',', '.')),
                                       int(t.tpriority),
                                       float(str(t.texetime).\
                                            replace(',', '.'))))
            if output:
                print '------------------------------------'

        system.path = cargs.path if len(cargs.path) > 0 \
                                 else range(len(system.tasks))
        return system



    text = (' '.join(cargs.file.readlines())).\
            replace('\r\n', '').replace(' ', '').\
            replace(',', '.')
    xml_sys = objectify.fromstring(text)
    def print_main():
        system = create_system_from_xml(xml_sys)
        reachability(system, verbose=0)

    def print_system():
        for cperiod in range(10, 100):
            system = create_system_from_xml(xml_sys, output=False)
            system.components[0].period = 6 #cperiod
            system.components[0].budget = 1.5 #cperiod*1.0/4
            P = cperiod #80
            system.components[0].tasks[0].period = P #int(cperiod*2.5)
            system.components[0].tasks[1].period = P #int(cperiod*2.5)
            system.components[0].tasks[0].exetime = 0.5
            #cperiod*1.0/8 #system.components[0].budget/4
            system.components[0].tasks[1].exetime = 0.5
            #cperiod*1.0/8 #system.components[0].budget/4

            #ls = tuple(system.generate_paths(0, 0, cargs.time))
            #tp_reach = tuple(system.TP_reach(ls))
            #ss = system.schedulability and \
            #      (False not in [c.schedulability for c in system.components])
            #print cperiod, system.components[0].name
            #print '------------------'
            #if not ss:
            #    continue
            print 'D', cperiod
            reachability(system, verbose=2)
            del system


    def add_server(system, P=20, Pt=80, B=3.0, Bt=1.0):
        ss = copy.deepcopy(system)
        c = len(ss.components)
        t = len(ss.tasks)
        t1 = t
        t2 = t+1
        component = Component('System server', P, 99, B)
        component.addTask(Task('sender', Pt, 2, Bt))
        component.addTask(Task('receiver', Pt, 1, Bt))
        ss.addComponent(component)
        ss.path = sum([[i, t1, t2] for i in system.path[:-1]], []) + \
                    [system.path[-1]]
        return ss


    def print_added_server():
        """Adds new comunication server."""
        system = create_system_from_xml(xml_sys)
        P = 20
        Pt = 80
        B = 3.0
        Bt = 1.0

        system = add_server(system, P, Pt, B, Bt)
        reachability(system, verbose=0)



    def draw_cairo(s, name='tasks.pdf'):
        ls = tuple(s.generate_paths(0, 0, cargs.time))
        tp_reach = s.TP_reach(ls)
        #tp_reach = s.TP_first(ls)

        import math,cairo
        width, height = 1800,200
        surface = cairo.PDFSurface(name, width, height)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0,0,width,height)
        ctx.fill()

        x = width*1.0/(cargs.time+1)
        y = height*1.0/len(s.tasks)
        print x,y
        i = 0
        c_tasks = [0]
        for c in s.components:
            i += len(c.tasks)
            c_tasks += [i]

        for i,c in enumerate(s.components):
            for t in np.arange(0, cargs.time, c.P):
                ctx.set_source_rgb(0,1,float(c.priority)/len(s.components))
                ctx.rectangle(x*t,y*c_tasks[i],x*c.budget+0.1,y*len(c.tasks)-2)
                #print x*t,y*i,x,y-2
                ctx.fill()


        path=[0 for t in s.tasks]

        x = width*1.0/(cargs.time+1)
        y = height*1.0/len(s.tasks)
        print x,y
        for i,tsk in enumerate(s.tasks):
            for t in range(cargs.time):
                st = tsk.status(t)

                #if 'R' in [tt.status(t) for tt in tsk.HB]:
                #    continue

                #print [tt.status(t) for C in tsk.component.HPS for tt in C.tasks]
                #    continue

                if st=='R':
                    if path[i] == tsk.ialpha(t):
                        ctx.set_source_rgb(1,1,tsk.priority*1.0/5)
                    else:
                        ctx.set_source_rgb(1,0,tsk.priority*1.0/5)
                    ctx.rectangle(x*t,y*i,x+0.1,y/2-2)
                    #print x*t,y*i,x,y-2
                    ctx.fill()

        print tp_reach

        for p in tp_reach:
            ctx.set_line_width(2)
            ctx.set_source_rgb(0, 0, 0)
            ctx.move_to(x*(
                s.tasks_in_path[0].alpha(p[0])
                + s.tasks_in_path[0].delta(p[0])
                ), y*s.path[0]+1)
            for j,i in enumerate(p[1:]):
                ctx.line_to(x*(
                    s.tasks_in_path[j+1].alpha(p[j+1])
                    + s.tasks_in_path[j+1].delta(p[j+1])
                    ),
                    y*s.path[j+1]+ 0.1)
            ctx.stroke()

        surface.finish()

    #print 'Name: (delay)', cargs.file

    print_main()
    #print_system()
    #print_added_server()

def aaa():
    from generator import rand_system

    #system = create_system_from_xml(xml_sys, output=False)
    system_settings = dict(
        minTasks=2, maxTasks=2,
        minComps=2, maxComps=2,
        utilization=0.1
        )
    system = rand_system(**system_settings)
    system.path = cargs.path

    system2 = add_server(system, P=5, Pt=10, B=3, Bt=1)
    print system, system2, system2.tasks, system2.path
    #print system.schedulability and not (False in [c.schedulability for c in
    #                                    system.components])
    #print system2.schedulability and not (False in [c.schedulability for c in
    #                                    system2.components])
    #
    reachability(system, verbose=0)
    draw_cairo(system)
    reachability(system2, verbose=0)
    draw_cairo(system2, 'tasks2.pdf')

