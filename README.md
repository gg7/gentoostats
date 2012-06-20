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

You can select what is reported by editing /etc/gentoostats/payload.cfg.

You can view what exactly is going to be reported by running

    gentoostats-send -vv --dryrun

What can be reported
--------------------

* Make.conf variables:
    - ACCEPT_KEYWORDS
    - ARCH
    - CHOST
    - FEATURES
    - CFLAGS
    - CXXFLAGS
    - FFLAGS
    - LDFLAGS
    - GENTOO_MIRRORS
    - SYNC (rsync server)
    - MAKEOPTS
* System USE flags
* Installed Packages
    - Package build time
    - Package Keyword
    - Package repository (e.g. "gentoo")
    - Package size
    - Package USE flags (plus, minus, unset)
* Selected Packages (world file, plus all selected sets)
* Time of last Portage tree synchronisation
* LANG
* PLATFORM
  (e.g. 'Linux-3.2.1-gentoo-r2-x86_64-Intel-R-_Core-TM-_i3_CPU_M_330_@_2.13GHz-with-gentoo-2.0.3')
* PROFILE (e.g. 'default/linux/amd64/10.0/desktop')

Installation
============

Stable
------

To install the stable client, use the ebuild found in the
overlay/app-portage/gentoostats directory.

An UUID and password will be automatically generated and saved in
/etc/gentoostats/auth.cfg

Unstable
--------

To download the unstable client, use this:

    git clone -b gg7 https://github.com/gg7/gentoostats.git

Then generate /etc/gentoostats/auth.cfg

    echo -e "[AUTH]\nUUID : $(cat /proc/sys/kernel/random/uuid)\n"         > /etc/gentoostats/auth.cfg
    echo -e "PASSWD : $(cat /dev/urandom | tr -dc a-zA-Z0-9 | head -c16)" >> /etc/gentoostats/auth.cfg

Finally copy and edit payload.cfg

    cp gentoostats/payload.cfg /etc/gentoostats/payload.cfg
    $EDITOR /etc/gentoostats/payload.cfg

Usage
=====

To submit your stats, run gentoostats-send as root.

To access stats on the command line, use gentoostats-cli (stable only).

Links
=====

GSoC 2011 Project:  http://www.google-melange.com/gsoc/project/google/gsoc2011/vh4x0r/26001  
GSoC 2011 Proposal: http://www.google-melange.com/gsoc/proposal/review/google/gsoc2011/vh4x0r/1  
GSoC 2012 Project:  http://www.google-melange.com/gsoc/project/google/gsoc2012/gg7/28001  