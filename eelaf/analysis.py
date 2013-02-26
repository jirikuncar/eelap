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

"""Example analysis of EELAF system."""

import copy
import argparse
import numpy as np
from lxml import objectify
from .__init__ import Task, Component, System


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
            system.components[0].period = 6  # cperiod
            system.components[0].budget = 1.5  # cperiod*1.0/4
            P = cperiod  # 80
            system.components[0].tasks[0].period = P  # int(cperiod*2.5)
            system.components[0].tasks[1].period = P  # int(cperiod*2.5)
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
        t = len(ss.tasks)
        t1 = t
        t2 = t + 1
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

        import cairo
        width, height = 1800, 200
        surface = cairo.PDFSurface(name, width, height)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        x = width * 1.0 / (cargs.time + 1)
        y = height * 1.0 / len(s.tasks)
        print x, y
        i = 0
        c_tasks = [0]
        for c in s.components:
            i += len(c.tasks)
            c_tasks += [i]

        for i, c in enumerate(s.components):
            for t in np.arange(0, cargs.time, c.P):
                ctx.set_source_rgb(0, 1, float(c.priority) / len(s.components))
                ctx.rectangle(x * t, y * c_tasks[i], x * c.budget + 0.1,
                              y * len(c.tasks) - 2)
                #print x*t,y*i,x,y-2
                ctx.fill()

        path = [0 for t in s.tasks]

        x = width * 1.0 / (cargs.time + 1)
        y = height * 1.0 / len(s.tasks)
        print x, y
        for i, tsk in enumerate(s.tasks):
            for t in range(cargs.time):
                st = tsk.status(t)

                #if 'R' in [tt.status(t) for tt in tsk.HB]:
                #    continue

                #print [tt.status(t) for C in tsk.component.HPS for tt in C.tasks]
                #    continue

                if st == 'R':
                    if path[i] == tsk.ialpha(t):
                        ctx.set_source_rgb(1, 1, tsk.priority * 1.0 / 5)
                    else:
                        ctx.set_source_rgb(1, 0, tsk.priority * 1.0 / 5)
                    ctx.rectangle(x * t, y * i, x + 0.1, y / 2 - 2)
                    #print x*t,y*i,x,y-2
                    ctx.fill()

        print tp_reach

        for p in tp_reach:
            ctx.set_line_width(2)
            ctx.set_source_rgb(0, 0, 0)
            ctx.move_to(x * (
                s.tasks_in_path[0].alpha(p[0])
                + s.tasks_in_path[0].delta(p[0])
                ), y * s.path[0] + 1)
            for j, i in enumerate(p[1:]):
                ctx.line_to(x * (
                    s.tasks_in_path[j + 1].alpha(p[j + 1])
                    + s.tasks_in_path[j + 1].delta(p[j + 1])
                    ),
                    y * s.path[j + 1] + 0.1)
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
