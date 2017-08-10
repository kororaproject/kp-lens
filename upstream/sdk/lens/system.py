#
# Copyright 2012-2017 "Korora Project" <dev@kororaproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the temms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import locale
import os
import re

class System():
    def __init__(self):
        # align to current locale settings
        locale.setlocale(locale.LC_NUMERIC, '')

        # store our base architecture
        arch = os.uname()[4]

        if arch in ['i386', 'i686']:
            self._arch = '32 bit (%s)' % (arch)
        elif arch in ['x86_64']:
            self._arch = '64 bit (%s)' % (arch)
        else:
            self._arch = 'Unknown'

        self._cpu = {
            'model': 'Unknown',
            'sockets': 0,
            'clock':   0,
            'clockMax': 0,
            'clockMin': 0,
            'cores_per_sockets': 0,
            'threads_per_core':  0
        }
        self._build_cpu_info()

        self._current_kernel = os.uname()[2]

        self._distribution = {
            'name':     'Unknown',
            'codename': 'Unknown',
            'desktop':  'Unknown',
            'version':  'Unknown',
            'live':     (os.getenv('LOGNAME') == 'liveuser'),
        }
        self._build_dist_info()

        self._memory = {
            'total':      0,
            'free':       0,
            'available':  0,
            'buffers':    0,
            'cached':     0,
            'swapCached': 0,
            'swapTotal':  0,
            'swapFree':   0,
        }
        self._build_mem_info()

    def _build_cpu_info(self):
        try:
            p = os.popen('lscpu')
            cpuinfo = p.read()
            p.close()
            m = re.search('Model name:\s+(.*)', cpuinfo)
            if m:
                self._cpu['model'] = m.group(1)

            m = re.search('Socket\(s\):\s+(\d+)', cpuinfo)
            if m:
                self._cpu['sockets'] = locale.atoi(m.group(1))

            m = re.search('CPU MHz:\s+(.*)', cpuinfo)
            if m:
                self._cpu['clock'] = int(locale.atof(m.group(1)) * 1e6)

            m = re.search('CPU max MHz:\s+(.*)', cpuinfo)
            if m:
                self._cpu['clockMax'] = int(locale.atof(m.group(1)) * 1e6)

            m = re.search('CPU min MHz:\s+(.*)', cpuinfo)
            if m:
                self._cpu['clockMin'] = int(locale.atof(m.group(1)) * 1e6)

            m = re.search('Core\(s\) per socket:\s+(.*)', cpuinfo)
            if m:
                self._cpu['cores_per_sockets'] = locale.atoi(m.group(1))

            m = re.search('Thread\(s\) per core:\s+(.*)', cpuinfo)
            if m:
                self._cpu['threads_per_core'] = locale.atoi(m.group(1))

        except:
            pass

    def _build_dist_info(self):
        try:
            p = open('/etc/redhat-release', 'r')
            distinfo = p.read()
            p.close()
            m = re.search('(.+) release (\d+) \((.*)\)', distinfo)
            if m:
                self._distribution['name'] =     m.group(1)
                self._distribution['codename'] = m.group(3)
                self._distribution['version'] =  m.group(2)

            # store desktop session
            if 'DESKTOP_SESSION' in os.environ and not 'default' in os.environ['DESKTOP_SESSION'].lower():
                if 'plasma' in os.environ['DESKTOP_SESSION'].lower():
                    self._distribution['desktop'] = 'KDE PLASMA'

                else:
                    self._distribution['desktop'] = os.environ['DESKTOP_SESSION'].upper()

            elif 'GDMSESSION' in os.environ and not 'default' in os.environ['GDMSESSION']:
                self._distribution['desktop'] = os.environ['GDMSESSION'].upper()

            elif 'XDG_CURRENT_DESKTOP' in os.environ and not 'default' in os.environ['XDG_CURRENT_DESKTOP']:
                self._distribution['desktop'] = os.environ['XDG_CURRENT_DESKTOP'].upper()

            # store we are a live CD session
            self._distribution['live'] = (os.getlogin() == 'liveuser')

        except:
            pass

    def _build_mem_info(self):
        try:
            p = open('/proc/meminfo', 'r')
            meminfo = p.read()

            m = re.search('MemTotal:\s+(\d+) kB', meminfo)
            if m:
                self._memory['total'] = locale.atoi(m.group(1)) * 1024

            m = re.search('MemFree:\s+(\d+) kB', meminfo)
            if m:
                self._memory['free'] = locale.atoi(m.group(1)) * 1024

            m = re.search('MemAvailable:\s+(\d+) kB', meminfo)
            if m:
                self._memory['available'] = locale.atoi(m.group(1)) * 1024

            m = re.search('Buffers:\s+(\d+) kB', meminfo)
            if m:
                self._memory['buffers'] = locale.atoi(m.group(1)) * 1024

            m = re.search('Cached:\s+(\d+) kB', meminfo)
            if m:
                self._memory['cached'] = locale.atoi(m.group(1)) * 1024

            m = re.search('SwapCached:\s+(\d+) kB', meminfo)
            if m:
                self._memory['swapCached'] = locale.atoi(m.group(1)) * 1024

            m = re.search('SwapTotal:\s+(\d+) kB', meminfo)
            if m:
                self._memory['swapTotal'] = locale.atoi(m.group(1)) * 1024

            m =re.search('SwapFree:\s+(\d+) kB', meminfo)
            if m:
                self._memory['swapFree'] = locale.atoi(m.group(1)) * 1024

        except:
            pass

    def refresh(self):
        self._build_cpu_info()
        self._build_mem_info()

    def to_dict(self):
        return {
            'arch': self._arch,
            'cpu': self._cpu,
            'distribution': self._distribution,
            'current_kernel': self._current_kernel,
            'memory': self._memory
        }
