# -*- coding: utf-8 -*-
##
## This file is part of End-to-End Latency Analyzer for ProCom (EELAP).
## Copyright (C) 2012, 2013 Jiri Kuncar <jiri.kuncar@gmail.com>.
##
## EELAP is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## EELAP is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Generator of random systems for EELAP."""

import sys
import argparse
import random
from eelap import Task, Component, System
from eelap.analysis import add_server

__all__ = ['main', 'rand_system']


def rand_system(minTasks=1,
                maxTasks=1,
                minTaskPeriod=0.04,
                maxTaskPeriod=0.12,
                resources=0,
                resolution=1000,
                minComps=1,
                maxComps=1,
                minCompPeriod=0.01,
                maxCompPeriod=0.02,
                utilization=0.2,
                globalsched='FPS',
                localsched='EDF',
                payback=False,
                verbose=False,
                **kargs):
    ## FIXME: improve balance of Component and Task utilizations

    def rand_comp(component, utils):
        tasks = random.randint(minTasks, maxTasks)
        xutils = [random.uniform(0.2, 0.8) for i in range(tasks)]
        sutils = sum(xutils)
        periods = [random.uniform(minTaskPeriod, maxTaskPeriod) for i in range(tasks)]
        freq = map(lambda x: 1.0 / x, periods)
        priorities = list(range(tasks))
        random.shuffle(priorities, random.random)

        rutils = [random.uniform(0.2, 0.8) for i in range(tasks)]
        srutils = sum(rutils)
        utilizations = [(rutils[i] / srutils) * utils for i in range(tasks)]
        sutils = sum(utilizations)
        utilizations = map(lambda x: utils * x / sutils, utilizations)
        exectimes = map(lambda (a, b): a / b, zip(utilizations, freq))

        if verbose:
            print 'Component'
            print '================'
            print 'periods', periods
            print 'freq', freq
            print 'utils', utilizations
            print 'exec', exectimes
            print 'utilization', sum(map(lambda c: exectimes[c] * freq[c],
                                         range(tasks)))
            print '----------------'

        return [Task(
                'comp%d:task%d' % (component, t),
                resolution * periods[t],
                priorities[t],
                resolution * exectimes[t]) for t in range(tasks)]

    components = random.randint(minComps, maxComps)
    cperiods = [random.uniform(minCompPeriod, maxCompPeriod)
                for i in range(components)]
    freq = map(lambda x: 1.0 / x, cperiods)
    cpriorities = list(range(components))
    random.shuffle(cpriorities, random.random)
    utils = utilization
    rutils = [random.uniform(0.2, 0.8) for i in range(components)]
    srutils = sum(rutils)
    utilizations = [(rutils[i] / srutils) * utils for i in range(components)]
    sutils = sum(utilizations)
    # sum(map(freq*budget)) = utilization
    utilizations = map(lambda x: utils * x / sutils, utilizations)
    budget = map(lambda (a, b): a / b, zip(utilizations, freq))

    if verbose:
        print 'System'
        print '================'
        print 'periods:', cperiods
        print 'freq:', freq
        print 'utils:', utilizations
        print 'budget:', budget
        print 'utilization:', sum(map(lambda c: budget[c] * freq[c],
                                      range(components)))
        print '----------------'

    system = System(
        scheduler=globalsched,
        resolution=resolution)
    for c in range(components):
        component = Component(
            "comp%d" % (c,),
            resolution * cperiods[c],
            cpriorities[c],
            resolution * budget[c],
            localsched,
            payback)
        for t in rand_comp(c, utils * utilizations[c]):
            component.addTask(t)
        system.addComponent(component)

    return system


def main():
    """
    EELAP generator command line interface.

    .. program-output:: eelap_generator -h

    """
    # python -m 'eelap.generator' -h | fold -w 60
    parser = argparse.ArgumentParser(description='System generator for EELAP.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False,
                        help="verbose output")

    subparsers = parser.add_subparsers(help='Actions', dest='action')
    import_parser = subparsers.add_parser('import',
                                          help='Import existing system file')
    import_parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
                               default=sys.stdin)

    generator_group = subparsers.add_parser('generate',
                                            help='Random system generator options')
    generator_group.add_argument('-P', '--payback',
                                 action='store_true', default=False,
                                 help="overrun calculation with or without payback")
    generator_group.add_argument('-u', type=float, dest='utilization', default=0.4,
                                 help='system utilization (0.0,1.0)')
    generator_group.add_argument('-s', type=int, dest='systems', default=1,
                                 help='an integer for number of systems')
    generator_group.add_argument('-r', '--resolution', type=int, dest='resolution',
                                 default=1000, help='simulation resolution')
    generator_group.add_argument('-mc', type=int, dest='minComps', default=1,
                                 help='minimal number of components per system')
    generator_group.add_argument('-Mc', type=int, dest='maxComps', default=2,
                                 help='maximal number of components per system')
    generator_group.add_argument('-mt', type=int, dest='minTasks', default=1,
                                 help='minimal number of tasks per component')
    generator_group.add_argument('-Mt', type=int, dest='maxTasks', default=2,
                                 help='maximal number of tasks per component')
    generator_group.add_argument('-ls', '--localsched', dest='localsched', default='EDF',
                                 help='component scheduler (local scheduler)')
    generator_group.add_argument('-gs', '--globalsched', dest='globalsched', default='FPS',
                                 help='system scheduler (global scheduler)')
    generator_group.add_argument('-R', type=float, dest='resources', default=0.4,
                                 help='probability that task has shared resource (0.0,1.0)')

    generator_group.add_argument('-mcp', type=float, dest='minCompPeriod', default=0.010,
                                 help='minimal component period')
    generator_group.add_argument('-Mcp', type=float, dest='maxCompPeriod', default=0.080,
                                 help='maximal component period')
    generator_group.add_argument('-mtp', type=float, dest='minTaskPeriod', default=0.020,
                                 help='minimal task period')
    generator_group.add_argument('-Mtp', type=float, dest='maxTaskPeriod', default=0.120,
                                 help='maximal task period')

    parser.add_argument('--reachability',
                        action='store_true', default=False,
                        help="print reachability results")

    cs_group = parser.add_argument_group('Communication Server')

    cs_group.add_argument('--with-communication-server',
                          dest='communication_server',
                          action='store_true', default=False,
                          help="add communication server to copy of each system")

    cs_group.add_argument('-csP', '--communication-server-period',
                          dest='communication_server_period',
                          type=float, default=0.010, metavar='t',
                          help="communication server period")

    cs_group.add_argument('-csQ', '--communication-server-budget',
                          dest='communication_server_budget',
                          type=float, default=0.002, metavar='t',
                          help="communication server budget")

    cs_group.add_argument('-csp', '--communication-server-priority',
                          dest='communication_server_priority',
                          type=int, default=None, metavar='p',
                          help="communication server priority - not specified (None) = highest")

    cs_group.add_argument('-t', '--communication-server-tasks',
                          dest='communication_server_tasks',
                          nargs=4, action='append', metavar=('name', 'P', 'p', 'X'),
                          help="component task definition")

    parser.add_argument('--path', metavar='Ti', type=int, nargs='*',
                        help='define indexes of tasks as a data flow path')

    args = parser.parse_args()

    check_system = lambda system: system.schedulability and \
        all(map(lambda c: c.schedulability, system.components))

    make_task_from_list = lambda (name, P, p, X): dict(name=name,
                                                       period=float(P),
                                                       priority=int(p),
                                                       exetime=float(X))

    tasks = None
    if args.communication_server_tasks:
        tasks = map(make_task_from_list, args.communication_server_tasks)

    def generate_systems():
        for s in range(args.systems):
            for i in range(1000):
                system = rand_system(**vars(args))
                ## assign system data path
                if args.path:
                    system.path = args.path
                ## add communication server to copy of the system
                if args.communication_server:
                    copy_system = add_server(
                        system,
                        component_period=args.communication_server_period,
                        component_priority=args.communication_server_priority,
                        component_budget=args.communication_server_budget,
                        tasks=tasks)

                ## check system and its copy if communication server is added
                if check_system(system) and (not args.communication_server or
                                             check_system(copy_system)):
                    yield system
                    if args.communication_server:
                        yield copy_system
                    break

                if args.verbose:
                    print i, ' ...'

    def create_system_from_xml(input_file):
        """
        Reads system configuration from param:`xml_system`
        and returns cls:`System` instances.
        """
        from lxml import objectify
        root = objectify.fromstring(input_file.read())
        for s in root.iterfind('system'):
            system = System(**dict(s.items()))
            for c in s.iterfind('component'):
                component = Component(**dict(c.items()))
                for t in c.iterfind('task'):
                    task = Task(**dict(t.items()))
                    component.addTask(task)
                system.addComponent(component)
                if args.path:
                    system.path = args.path
            yield system
            if args.communication_server:
                yield add_server(
                    system,
                    component_period=args.communication_server_period,
                    component_priority=args.communication_server_priority,
                    component_budget=args.communication_server_budget,
                    tasks=tasks)

    if args.action == 'generate':
        systems = list(generate_systems())
    else:
        systems = list(create_system_from_xml(args.input))

    print '<root>\n' + '\n'.join(map(str, systems)) + '\n</root>'

    if args.reachability:
        from eelap.analysis import reachability
        map(lambda s: reachability(s, time=360), systems)


if __name__ == "__main__":
    main()
