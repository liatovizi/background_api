import os
import sys


def convert(f):
    os.system("yapf --style dev-utils/yapf/yapf.cfg --in-place %s" % f)
    #os.system("autopep8 --max-line-length 120 %s" % f)


if sys.argv[1].endswith("__init__.py"):
    f = open(sys.argv[1], "rt")
    b = f.read()
    f.close()
    if b:
        convert(sys.argv[1])
    else:
        os.system("cat %s" % sys.argv[1])
else:
    convert(sys.argv[1])
