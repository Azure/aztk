class CommandBuilder:
    def __init__(self, executable: str):
        self.executable = executable
        self.options = []
        self.arguments = []

    def add_option(self, name: str, value: str, enable: bool=None):
        if enable is None:
            enable = value
        if enable:
            self.options.append(dict(name=name, value=value))
            return True

        return False

    def add_argument(self, arg):
        self.arguments.append(arg)

    def to_str(self):
        option_str = " ".join(["{name} {value}".format(**x)
                               for x in self.options])
        argument_str = " ".join(self.arguments)
        return "{0} {1} {2}".format(self.executable, option_str, argument_str)
