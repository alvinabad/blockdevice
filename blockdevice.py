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

import sys
import os
import utils
import tune2fs
import logging
import pprint as pp

# create logger
log = logging.getLogger(__name__)

VALID_DISK_TYPES = ['part', 'lvm', 'crypt']
VALID_FSTYPES = ['ext2', 'ext3', 'ext4', 'swap']

def dd(ifdev, ofdev, bs=None, count=None):
    """
    Run dd on ifdev and ofdev
    Returns (error, stdoutdata, stderrdata)
    """

    if bs:
        BS_OPTION = "bs=%s" % bs
    else:
        BS_OPTION = ""

    if count:
        COUNT_OPTION= "count %s" % count
    else:
        COUNT_OPTION= ""

    cmd = "dd if=%s of=%s %s %s" % (ifdev, ofdev, BS_OPTION, COUNT_OPTION)
    print cmd
    (error, stdoutdata, stderrdata) = utils.run_syscmd(cmd)
    return (error, stdoutdata, stderrdata)

def is_preboot():
    """Check if system is running in pre-boot"""

    cmd = "uname -n"
    (error, stdoutdata, stderrdata) = utils.run_syscmd(cmd)
    if error > 0:
        return True

    nodename = stdoutdata.strip()
    if nodename == '(none)':
        return True

    return False

def get_boot_device():
    """
    Guess the /boot device based on the last mountpoint
    Returns None if it cannot find it.
    """

    for device_path in get_devices():
        last_mountpoint = tune2fs.get_last_mountpoint(device_path)
        if last_mountpoint == '/boot':
            return device_path

    return None

def get_size(device_path):
    block_count = tune2fs.get_info(device_path, 'Block count')
    block_size = tune2fs.get_info(device_path, 'Block size')

    if block_count is None or block_size is None:
        return None

    size = int(block_count) * int(block_size)
    return size

def get_free_blocks(device_path):
    free_blocks = tune2fs.get_info(device_path, 'Free blocks')
    if free_blocks is not None:
        free_blocks = int(free_blocks)

    return free_blocks

def get_free_size(device_path):
    free_blocks = tune2fs.get_info(device_path, 'Free blocks')
    block_size = tune2fs.get_info(device_path, 'Block size')

    if free_blocks is None or block_size is None:
        return None

    size = int(free_blocks) * int(block_size)
    return size

def get_uuid(device_path):
    uuid = tune2fs.get_info(device_path, 'Filesystem UUID')
    return uuid

def get_valid_devices():
    """Get valid devices to be encrypted or decrypted"""

    boot_device = get_boot_device()

    device_paths = []
    for device_path in get_devices():
        disktype = get_info(device_path)['TYPE']
        fstype = get_info(device_path)['FSTYPE']
        last_mountpoint = tune2fs.get_last_mountpoint(device_path)

        if disktype not in VALID_DISK_TYPES:
            continue
        if fstype not in VALID_FSTYPES:
            continue
        if boot_device and boot_device == device_path:
            continue

        device_paths.append(device_path)

    return device_paths

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    uid = os.getuid()
    if uid != 0:
        log.error("Must run as root")
        sys.exit(1)

    if len(sys.argv) == 1:
        devices = get_devices(by='UUID')
        for d in devices:
            print d

        print "=" * 40
        valid_devices = get_valid_devices()
        pp.pprint(valid_devices)
    else:
        device_path = sys.argv[1]
        data = get_info(device_path)
        print len(data)
        pp.pprint(data)

        print "   SIZE     : %s" % get_size(device_path)
        print "   FREE SIZE: %s" % get_free_size(device_path)
        print "   FREE SIZE: %s" % get_free_size(device_path)
        print "   UUID     : %s" % get_uuid(device_path)
        print "   UUID     : %s" % get_info(device_path)['UUID']

        format = "%-30s %-10s %-10s %-10s"
        for device_path in get_valid_devices():
            disktype = get_info(device_path)['TYPE']
            fstype = get_info(device_path)['FSTYPE']
            last_mountpoint = tune2fs.get_last_mountpoint(device_path)

            print format % (device_path, disktype, fstype, last_mountpoint)

        print "IS THIS PREBOOT?", is_preboot()
