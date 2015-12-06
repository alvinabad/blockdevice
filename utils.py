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
import shlex
import subprocess
import logging

# create logger
log = logging.getLogger(__name__)

def run_syscmd(cmd, input=None):
    """
    Run a system command
    Input: cmd, input
    Returns tupple: (returncode, stdoutdata, stderrdata)
    """

    cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdin=subprocess.PIPE)
    (stdoutdata, stderrdata) = p.communicate(input=input)
    return (p.returncode, stdoutdata, stderrdata)

def run_syscall(cmd):
    cmd = shlex.split(cmd)
    error = 1
    try:
        error = subprocess.call(cmd)
    except:
        log.exception("Error running: %s", cmd)

    return error

def get_fullpath(cmd):
    for path in os.environ["PATH"].split(os.pathsep):
        file = os.path.join(path, cmd)
        if os.path.exists(file):
            return file

    return None
