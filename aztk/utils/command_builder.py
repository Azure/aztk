class CommandOption:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class CommandBuilder:
    """
        Helper class to build a command line
    """

    def __init__(self, executable: str):
        """
            :param executable: Path/name of the executable to run
        """
        self.executable = executable
        self.options = []
        self.arguments = []

    def add_option(self, name: str, value: str = None, enable: bool = None):
        """
            Add an option to the command line.

            :param name: Option name (with the dash(es))
            :param value: Value for the option(If null and enable is not provided it won't add the option)
            :param enable: To explicitly add or ignore the option

            Usage:
            >>> command.add_option("--id", myId)               # => Will only add to the command if myId is not null
            >>> command.add_option("--id", myId, enable=False) # => Will not add it to the list
        """
        if enable is None:
            enable = value
        if enable:
            self.options.append(CommandOption(name=name, value=value))
            return True

        return False

    def add_argument(self, arg):
        self.arguments.append(arg)

    def to_array(self):
        cmd = [self.executable]
        for option in self.options:
            cmd.append(option.name)
            if option.value is not None:
                cmd.append(option.value)

        for arg in self.arguments:
            cmd.append(arg)
        return cmd

    def to_str(self):
        cmd = self.to_array()
        return " ".join(cmd)
