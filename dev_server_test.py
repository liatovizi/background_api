from natapp.app import create_app
import code
import traceback
import signal
from urllib.parse import urlparse
import os
import sys


def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d = {'_frame': frame}  # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)


def break_to_pdb(sig, frame):
    import pdb
    pdb.set_trace()


def listen():
    signal.signal(signal.SIGUSR1, break_to_pdb)  # Register handler


def load_test_config():
    result = dict()
    for f in ('testconfig.py', 'instance/testconfig.py'):
        pf = os.path.splitext(os.path.basename(f))[0]
        d = os.path.dirname(f)
        sys.path.insert(0, d)
        m = __import__(pf)
        sys.path.remove(d)
        for k, v in m.__dict__.items():
            if not k.startswith("__") or not k.endswith("__"):
                result[k] = v
        del sys.modules[pf]

    return result


if __name__ == '__main__':
    listen()

    test_config = load_test_config()

    app = create_app(test_config)

    url = urlparse(app.config['API_ENDPOINT'])
    if url.port is None:
        port = 5019
    else:
        port = url.port

    if url.scheme == 'https':
        ssl_context = (app.config['SSL_CERTIFICATE'], app.config['SSL_PRIVATE_KEY'])
    else:
        ssl_context = None

    app.run(port=port, host='0.0.0.0', ssl_context=ssl_context, threaded=False)
