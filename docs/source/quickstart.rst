.. _quickstart:

Quickstart
==========

Eager to get started? This page gives a good introduction how the End-to-End
Latency Analysis Framework works and how you can benefit from it. It assumes
you already have it installed. If you do not, head over to the
:ref:`installation` section.


Finding possible execution paths
------------------------------------

The whole simulation is dependend on quick and effective algorithm for finding
possible exectution paths of tasks in all system components. All latency types
are calculated on specified data flow path that contains identifiers of tasks
in analyzed system.

Our generator :meth:`~analysis.System.generate_paths` returns tuples with
activation indexes of tasks accordingly to the analyzed execution path.
The algorithm starts with finding closest activation indexes of the first
task in path for defined interval. Following pseudocode shows simplified
version of our algorithm using methods :meth:`~analysis.Task.alpha` and
:meth:`~analysis.Task.ialpha` defined on :class:`~analysis.Task`.

.. code-block:: none
   :linenos:

    function generate_paths(start, stop, tasks_in_path):
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
    end function



