from aztk.utils.command_builder import CommandBuilder


def test_only_command():
    cmd = CommandBuilder("ssh")
    assert cmd.to_str() == "ssh"


def test_with_option():
    cmd = CommandBuilder("ssh")
    cmd.add_option("-L", "8080:localhost:8080")
    assert cmd.to_str() == "ssh -L 8080:localhost:8080"


def test_with_multiple_options():
    cmd = CommandBuilder("ssh")
    cmd.add_option("-L", "8080:localhost:8080")
    cmd.add_option("-p", "2020")
    assert cmd.to_str() == "ssh -L 8080:localhost:8080 -p 2020"


def test_with_arg_and_option():
    cmd = CommandBuilder("ssh")
    cmd.add_argument("admin@1.2.3.4")
    cmd.add_option("-p", "2020")
    assert cmd.to_str() == "ssh -p 2020 admin@1.2.3.4"


def test_with_disabled_options():
    cmd = CommandBuilder("ssh")

    cmd.add_option("--verbose", enable=True)
    cmd.add_option("-p", None)
    cmd.add_option("-L", "8080:localhost:8080", enable=False)
    assert cmd.to_str() == "ssh --verbose"
