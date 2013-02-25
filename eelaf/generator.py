from analysis import Task, Component, System
import argparse
import random
from lxml import etree
from lxml.builder import E

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
                **kargs):

    def rand_comp(component, utils):
        tasks = random.randint(minTasks, maxTasks)
        xutils = [random.uniform(0.2, 0.8) for i in range(tasks)]
        sutils = sum(xutils)
        periods = [random.uniform(minTaskPeriod, maxTaskPeriod) for i in range(tasks)]
        freq = map(lambda x: 1.0/x, periods)
        priorities = list(range(tasks))
        random.shuffle(priorities, random.random)

        rutils = [random.uniform(0.2, 0.8) for i in range(tasks)]
        srutils = sum(rutils)
        utilizations = [(rutils[i]/srutils)*utils for i in range(tasks)]
        sutils = sum(utilizations)
        ssutils = sum(map(lambda x:x/sutils, utilizations))
        utilizations = map(lambda x: utils*x/sutils, utilizations)
        print 'periods', periods
        print 'freq', freq
        print 'utils', utilizations
        exectimes = map(lambda (a,b): a/b, zip(utilizations, freq))
        sfreq = sum(freq)
        print 'exec', exectimes
        print 'utilization', sum(map(lambda c: exectimes[c]*freq[c], range(tasks)))
        print '----------------'

        def resource(task):
            if random.random() <= resources:
                ext = resolution*exectimes[task]
                exr = float(random.randint(5, 20))*ext/100
                sta = random.random()*(ext-exr)
                return (E.Resources(
                    E.rname('R%d' % task),
                    E.start(str(sta)),
                    E.end(str(sta+exr))
                ),)
            return ()

        return [Task(
                'comp%d:task%d' % (component, t),
                resolution*periods[t],
                priorities[t],
                resolution*exectimes[t]) for t in range(tasks)]

    components = random.randint(minComps, maxComps)
    cperiods = [random.uniform(minCompPeriod, maxCompPeriod) for i in range(components)]
    freq = map(lambda x:1.0/x, cperiods)
    cpriorities = list(range(components))
    random.shuffle(cpriorities, random.random)
    utils = utilization
    rutils = [random.uniform(0.2, 0.8) for i in range(components)]
    srutils = sum(rutils)
    utilizations = [(rutils[i]/srutils)*utils for i in range(components)]
    sutils = sum(utilizations)
    # sum(map(freq*budget)) = utilization
    ssutils = sum(map(lambda x:x/sutils, utilizations))
    utilizations = map(lambda x: utils*x/sutils, utilizations)
    print 'periods', cperiods
    print 'freq', freq
    print 'utils', utilizations
    budget = map(lambda (a,b): a/b, zip(utilizations, freq))
    sfreq = sum(freq)
    print 'budget', budget
    print 'utilization', sum(map(lambda c: budget[c]*freq[c], range(components)))
    print '----------------'
    system = System(
        scheduler=globalsched,
        resolution=resolution)
    for c in range(components):
        component = Component(
            "comp%d" % (c,),
            resolution*cperiods[c],
            cpriorities[c],
            resolution*budget[c],
            localsched,
            payback)
        for t in rand_comp(c, utils*utilizations[c]):
            component.addTask(t)
        system.addComponent(component)

    return system


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='System generator.')
    parser.add_argument('-P', '--payback',
                       action='store_true', default=False,
                       help="overrun calculation with or without payback")
    parser.add_argument('-p', '--prefix', nargs='?', dest='prefix', default='component',
                       help='filename prefix')
    parser.add_argument('-u', type=float, dest='utilization', default=0.4,
                       help='system utilization (0.0,1.0)')
    parser.add_argument('-s', type=int, dest='systems', default=1,
                       help='an integer for number of systems')
    parser.add_argument('-r', '--resolution', type=int, dest='resolution', default=1000,
                       help='simulation resolution')
    parser.add_argument('-mc', type=int, dest='minComps', default=1,
                       help='minimal number of components per system')
    parser.add_argument('-Mc', type=int, dest='maxComps', default=2,
                       help='maximal number of components per system')
    parser.add_argument('-mt', type=int, dest='minTasks', default=1,
                       help='minimal number of tasks per component')
    parser.add_argument('-Mt', type=int, dest='maxTasks', default=2,
                       help='maximal number of tasks per component')
    parser.add_argument('-ls', '--localsched', dest='localsched', default='EDF',
                       help='component scheduler (local scheduler)')
    parser.add_argument('-gs', '--globalsched', dest='globalsched', default='FPS',
                       help='system scheduler (global scheduler)')
    parser.add_argument('-R', type=float, dest='resources', default=0.4,
                       help='probability that task has shared resource (0.0,1.0)')

    parser.add_argument('-mcp', type=float, dest='minCompPeriod', default=0.010,
                       help='minimal component period')
    parser.add_argument('-Mcp', type=float, dest='maxCompPeriod', default=0.080,
                       help='maximal component period')
    parser.add_argument('-mtp', type=float, dest='minTaskPeriod', default=0.020,
                       help='minimal task period')
    parser.add_argument('-Mtp', type=float, dest='maxTaskPeriod', default=0.120,
                       help='maximal task period')


    args = parser.parse_args()
    rand_system(**vars(args))

