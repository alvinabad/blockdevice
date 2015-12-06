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

import logging
import utils

# create logger
log = logging.getLogger(__name__)

class Tune2fsException(Exception):
    pass

def get(device_path, attribute=None):
    """Get Information about device
       Returns dictionary of properties
    """

    cmd = "tune2fs -l %s" % device_path
    (error, stdoutdata, stderrdata) = utils.run_syscmd(cmd)
    if error > 0:
        raise Tune2fsException(stderrdata.strip())

    data = {}
    for d in stdoutdata.strip().split('\n'):
        try:
            (key, value) = d.split(':', 1)
        except ValueError:
            continue

        data[key] = value.strip()

    if attribute:
        if attribute in data:
            data = data[attribute]
        else:
            data = None

    return data

if __name__ == '__main__':
    import sys

    device_path = sys.argv[1]
    data = get(device_path)
    for key in sorted(data.keys()):
        print "%-25s = %s" % (key, data[key])
