# EELAP

End-to-End Latency Analysis for ProCom

## What is EELAP?

EELAP is a tool for End-to-End latency analysis
of real-time systems. It's intended for getting started very quickly
with analyzing hierarchical component systems using methods
described in following papers:

  * N. Feiertag, K. Richter, J. Nordlander, and J. Jonsson,
    "A Compositional Framework for End-to-End Path Delay Calculation
    of Automotive Systems under Different Path Semantics", In Workshop
    on Compositional Theory and Technology for Real-Time Embedded Systems
    (CRTS'08).

  * R. Inam, J. Maki-Turja, M. Sjodin, and M. Behnam,
    "Hard Real-time Support for Hierarchical Scheduling in FreeRTOS",
    7th annual workshop on Operating Systems Platforms for Embedded Real-Time
    Applications (OSPERT'11). by N. Feiertag, K. Richter, J. Nordlander,
    and J. Jonsson

## Is it ready?

It's not far even 1.0 but we believe that it can be helpful
for certain cases. Please be aware of _FIXME_ parts in the cource code.

## What do I need?

Numpy, lxml, and argparse are recommended for full functionality.
`pip` or `easy_install` will install them for you if you do
`pip install git+git://github.com/jirikuncar/eelap.git`.
We encourage you to use a virtualenv. Check the docs for complete installation
and usage instructions.

## Where are the docs?

Go to https://eelaf.readthedocs.org/en/latest/ for a prebuilt version
of the current documentation.  Otherwise build them yourself
from the sphinx sources in the docs folder.

## Where can I get help?

Either use can contact authors or open a
[ticket](https://github.com/jirikuncar/eelap/issues).

Author: Jiri Kuncar <jiri.kuncar@gmail.com>, Rafia Inam <rafia.inam@mdh.se>, Mikael Sjodin <mikael.sjodin@mdh.se>
