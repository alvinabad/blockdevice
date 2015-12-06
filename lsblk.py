# The MIT License (MIT)
# 
# Copyright (c) 2015 Alvin Abad
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import stat
import shlex
import utils
import logging

# create logger
log = logging.getLogger(__name__)

LSBLK_ATTR = [
    'NAME',
    'KNAME',
    'MAJ:MIN',
    'FSTYPE',
    'MOUNTPOINT',
    'LABEL',
    'UUID',
    'RA',
    'RO',
    'RM',
    'MODEL',
    'SIZE',
    'STATE',
    'OWNER',
    'GROUP',
    'MODE',
    'ALIGNMENT',
    'MIN-IO',
    'OPT-IO',
    'PHY-SEC',
    'LOG-SEC',
    'ROTA',
    'SCHED',
    'RQ-SIZE',
    'TYPE',
    'DISC-ALN',
    'DISC-GRAN',
    'DISC-MAX',
    'DISC-ZERO',
    ]

class ListBlockDeviceException(Exception):
    pass

def get(device_path=None, by='NAME'):
    """
    Get information about a device
    Returns a dict of all attributes of a device
    """

    if device_path is None:
        devices = _get_devices(by=by)
        return devices

    lsblk_options = ','.join(LSBLK_ATTR)

    cmd = "lsblk -b -d -i -n -P -o %s %s" % (lsblk_options, device_path)
    (error, stdoutdata, stderrdata) = utils.run_syscmd(cmd)
    if error > 0:
        raise ListBlockDeviceException(stderrdata.strip())

    data = {}
    for d in shlex.split(stdoutdata.strip()):
        (key, value) = d.split('=', 1)
        if key in lsblk_options:
            value = value.strip()
            data[key] = value

    return data


def _get_devices(by='NAME'):
    """Get all devices by NAME, LABEL, UUID, or KNAME"""

    devices = []
    if by not in ['NAME', 'LABEL', 'UUID', 'KNAME']:
        raise ListBlockDeviceException("Invalid type")

    cmd = "lsblk -b -a -l -i -n -o %s" % by
    (error, stdoutdata, stderrdata) = utils.run_syscmd(cmd)
    if error > 0:
        raise ListBlockDeviceException(stderrdata.strip())

    for d in stdoutdata.strip().split('\n'):
        d = d.strip()
        if d == '':
            continue

        device_name = d.split()[0]
        d = d.split()[0]

        d_path1 = d_path2 = ''
        if by == 'UUID':
            d_path1 = "/dev/disk/by-uuid/%s" % d
        elif by == 'LABEL':
            d_path1 = "/dev/disk/by-label/%s" % d
        elif by == 'NAME':
            d_path1 = "/dev/%s" % d
            d_path2 = "/dev/mapper/%s" % d
        elif by == 'KNAME':
            d_path1 = "/dev/%s" % d
            d_path2 = "/dev/mapper/%s" % d
        else:
            continue

        if os.path.exists(d_path1):
            devices.append(d_path1)
        elif os.path.exists(d_path2):
            devices.append(d_path2)

    return devices

def is_blockdevice(device):
    """
    Check if device is a block device
    Returns: True or False
    """

    mode = os.stat(device).st_mode
    return stat.S_ISBLK(mode)

if __name__ == '__main__':
    import sys

    try:
        device = sys.argv[1]
    except:
        device = None

    data = get(device)
    if type(data) == type(dict()):
        for k in sorted(data.keys()):
            print k, data[k]
    elif type(data) == type(list()):
        for d in sorted(data):
            print d
    else:
        print data
