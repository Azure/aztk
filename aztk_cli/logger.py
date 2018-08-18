import logging
import platform
import sys

root = logging.getLogger("aztk")

DEFAULT_FORMAT = "%(message)s"
VERBOSE_FORMAT = "[%(asctime)s] [%(filename)s:%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"


def add_coloring_to_emit_windows(fn):
    # add methods we need to the class

    def set_color(self, code):
        import ctypes

        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, "set_color", set_color)

    def new(*args):
        FOREGROUND_BLUE = 0x0001    # text color contains blue.
        FOREGROUND_GREEN = 0x0002    # text color contains green.
        FOREGROUND_RED = 0x0004    # text color contains red.
        FOREGROUND_INTENSITY = 0x0008    # text color is intensified.
        FOREGROUND_WHITE = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED

        # wincon.h
        FOREGROUND_BLUE = 0x0001
        FOREGROUND_GREEN = 0x0002
        FOREGROUND_RED = 0x0004
        FOREGROUND_MAGENTA = 0x0005
        FOREGROUND_YELLOW = 0x0006
        FOREGROUND_INTENSITY = 0x0008    # foreground color is intensified.

        BACKGROUND_YELLOW = 0x0060
        BACKGROUND_INTENSITY = 0x0080    # background color is intensified.

        levelno = args[1].levelno
        if levelno >= 50:
            color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY
        elif levelno >= 40:
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif levelno >= 30:
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif levelno >= 20:
            color = FOREGROUND_GREEN
        elif levelno >= 19:
            color = FOREGROUND_WHITE
        elif levelno >= 10:
            color = FOREGROUND_MAGENTA
        else:
            color = FOREGROUND_WHITE
        args[0].set_color(color)

        ret = fn(*args)
        args[0].set_color(FOREGROUND_WHITE)
        # print "after"
        return ret

    return new


def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if levelno >= 50:
            color = "\x1b[31m"    # red
        elif levelno >= 40:
            color = "\x1b[31m"    # red
        elif levelno >= 30:
            color = "\x1b[33m"    # yellow
        elif levelno >= 20:
            color = "\x1b[32m"    # green
        elif levelno >= 19:
            color = "\x1b[0m"    # normal
        elif levelno >= 10:
            color = "\x1b[35m"    # pink
        else:
            color = "\x1b[0m"    # normal
        args[1].msg = color + args[1].msg + "\x1b[0m"    # normal
        # print "after"
        return fn(*args)

    return new


if platform.system() == "Windows":
    # Windows does not support ANSI escapes and we are using API calls to set the console color
    logging.StreamHandler.emit = add_coloring_to_emit_windows(logging.StreamHandler.emit)
else:
    # all non-Windows platforms are supporting ANSI escapes so we use them
    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

logging.PRINT = 19
logging.addLevelName(logging.PRINT, "PRINT")


# pylint: disable=protected-access
def print_level(self, message, *args, **kwargs):
    self._log(logging.PRINT, message, args, **kwargs)


def setup_logging(verbose=False):
    if verbose:
        root.setLevel(logging.DEBUG)
        logging.basicConfig(format=VERBOSE_FORMAT, datefmt="%Y-%m-%d  %H:%M:%S", stream=sys.stdout)
    else:
        root.setLevel(logging.PRINT)
        logging.basicConfig(format=DEFAULT_FORMAT, stream=sys.stdout)

    # add custom levels
    logging.Logger.print = print_level
