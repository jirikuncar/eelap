:orphan:

End-to-End Latency Analysis for ProCom
======================================

.. rubric:: Abstract

This report presents an analysis tool *End-to-End Latency Analyzer for ProCom (EELAP)*
developed to compute different end-to-end latency semantics for
multi-rate components of real-time embedded systems. Procom component
technology implements executable reusable real-time components called
*Runnalbe Virtual Nodes (RVNs)* and supports two different communication
strategies for inter-RVN communication. The tool is developed to evaluate
the two communication strategies for multi-rate server-based components
the ProCom component technology.

In this report we present a user guide for EELAP. We describe the formulas
and corresponding algorithms used to compute end-to-end latency semantics,
and response-times of the tasks executing in a two-level hierarchical
scheduling framework. Further, we provide a detailed description of API's.

Introduction
------------
Here we present a brief introduction to the terminologies required to
understand the tool. We first explain end-to-end delay analysis and then
describe two communication strategies among the ProCom components.

End-to-End Delay Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^
In embedded systems, the realization of a piece of functionality can follow
a flow through many software components. Data may originate at one component
(e.g. a sensor) and passes through various other computational components,
before terminating at the final component (e.g.\ an actuator). Hence, the data
follows a chain of components :math:`(C1, C2, \dots ,Cn)`, each potentially
having its own periodicity and timing properties. The total time taken by
the data/signal to traverse the complete chain is called
*end-to-end latency* :cite:`EndEndPathDelay08`. For an embedded system with
real-time constraints, the end-to-end timing behavior is not only dependent
on the timing properties of its constituent components but also on the
message-chains among those components. In a communication chain, different
executable components (or tasks) are activated at different periods.
Such system is called a *multi-rate system* :cite:`EndEndPathDelay08`.

Communication Strategies among Procom components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In ProCom component model, the RVNs are implemented as servers
(called RVN-server) and the tasks are executed within the servers.
This type of systems are called server-based systems or hierarchical
systems :cite:`InamSEAA12`. The RVN-servers are executed within a two-level
hierarchical scheduling implementation :cite:`InamHSF11`.
To support communication *between* RVNs (also called
*inter-RVN communication*), two different strategies have been
proposed :cite:`InamECRTS12`. The first strategy is called a
*server-based communication*, implemented using a *communication server*.
The communication code is embedded within the communication server, which is
activated periodically.

Another interesting approach is to use a *direct communication strategy*,
where RVNs communicate with each other directly without an intermediate server.
Here the communication code is encapsulated within the RVN to send and receive
the data and/or messages. The details of both communication strategies for
ProCom component model can be found in :cite:`InamECRTS12`.

Both communication strategies for the ProCom technology reveal the multi-rate
systems. According to :cite:`EndEndPathDelay08`, all automotive embedded
systems are multi-rate systems. A system comprising the communication chains
among RVN servers transposes to a multi-rate server-based system.
Four different end-to-end semantics are provided in :cite:`EndEndPathDelay08`
for multi-rate systems. We develop the EELAP tool to compute these semantics
for multi-rate server-based systems using (1) response times of tasks executed
within a server and (2) then end-to-end semantics.

Contributions
^^^^^^^^^^^^^
We implement a tool *End-to-End Latency Analyzer for ProCom (EELAP)* :cite:`KuncarEELAP13`
to evaluate timing behavior of two communication strategies in a multi-rate
server-based real-time embedded components using end-to-end latencies
(or delays). The tool computes end-to-end latencies using the following
two steps:

* First it calculates the response times of all tasks executing in a two-level
  hierarchical scheduling framework by using methods/formulas provided
  in :cite:`InamOSPERT11`,
* And then it calculates different end-to-end latency semantics for both
  communication strategies.

In this report, we present the descriptions of API's of EELAP tool, the
formulas and their implementations in those API, and the algorithms for
schedulability condition, possible paths, path reachability, and generate
paths for different latency semantics.


.. include:: contents.rst.inc

