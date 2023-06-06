import os
import sys


def convert(f):
    if f.endswith(".py"):
        os.system("yapf --style dev-utils/yapf/yapf.cfg --in-place %s" % f)
        #os.system("autopep8 --max-line-length 120 %s" % f)


fn = sys.argv[1][3:]  #remove git status flags
if fn.endswith("__init__.py"):
    f = open(fn, "rt")
    b = f.read()
    f.close()
    if b:
        convert(fn)
    else:
        os.system("cat %s" % fn)
else:
    convert(fn)
