About
=====

The Gentoostats project aims to collect and analyse various statistics about
Gentoo systems.

This is an updated version of Gentoostats for GSoC 2012 and is based on the work
of Vikraman Choudhury for his GSoC 2011 project, "Gentoostats".

This repository contains the client application. You can find the server
[here](https://github.com/gg7/gentoostats_server).

What is reported?
=================

You can specify exactly what to report by running

    gentoostats configure

You can also manually edit /etc/gentoostats/payload.cfg after it has been
created.

You can view the submission data by running

    gentoostats submit -vv --pretend

What can be reported
--------------------

* Make.conf variables:
    - ACCEPT\_KEYWORDS
    - ACCEPT\_LICENSE
    - ARCH
    - CFLAGS
    - CHOST
    - CTARGET
    - CXXFLAGS
    - EMERGE\_DEFAULT\_OPTS
    - FEATURES
    - FFLAGS
    - GENTOO\_MIRRORS
    - LDFLAGS
    - MAKEOPTS
    - PORTAGE\_RSYNC\_EXTRA\_OPTS
    - SYNC (rsync server)
* System USE flags (USE)
* Installed Packages
    - Package build time
    - Package keyword
    - Package repository (e.g. "gentoo")
    - Package size
    - Package USE flags (USE, IUSE, PKGUSE)
* Selected Packages (your @world set, plus all selected sets)
* Time of last Portage tree synchronisation (LASTSYNC)
* LANG
* PLATFORM
  (e.g. 'Linux-3.2.1-gentoo-r2-x86\_64-Intel-R-\_Core-TM-\_i3\_CPU\_M\_330\_@\_2.13GHz-with-gentoo-2.0.3')
* PROFILE (e.g. 'default/linux/amd64/10.0/desktop')

Dependencies
============

* Python 2.7+ (including Python 3+)
* Portage
* Gentoolkit

Installation
============

NOTE: Currently there is no official server running, so you can't actually
report any statistics. You are free to experiment with the client though.

To download the unstable client, clone the 'gg7' branch of this repo:

    git clone -b gg7 https://github.com/gg7/gentoostats.git

Configuration
=============

Interactive Configuration
-------------------------

Run

    gentoostats configure

Manual Configuration
--------------------

To create /etc/gentoostats:

    mkdir /etc/gentoostats

To generate /etc/gentoostats/auth.cfg:

    echo -e "[AUTH]\nUUID : $(cat /proc/sys/kernel/random/uuid)\n"         > /etc/gentoostats/auth.cfg
    echo -e "PASSWD : $(cat /dev/urandom | tr -dc a-zA-Z0-9 | head -c16)" >> /etc/gentoostats/auth.cfg

To generate /etc/gentoostats/payload.cfg:

    cp gentoostats/payload.cfg.example /etc/gentoostats/payload.cfg
    $EDITOR /etc/gentoostats/payload.cfg

Usage
=====

To submit your stats, run 'gentoostats submit' (normally no superuser privileges
are required)

Links
=====

GSoC 2011 Project:  http://www.google-melange.com/gsoc/project/google/gsoc2011/vh4x0r/26001  
GSoC 2011 Proposal: http://www.google-melange.com/gsoc/proposal/review/google/gsoc2011/vh4x0r/1  
GSoC 2012 Project:  http://www.google-melange.com/gsoc/project/google/gsoc2012/gg7/28001  
