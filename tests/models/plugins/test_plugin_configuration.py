from aztk.models.plugins import PluginConfiguration, PluginPort, PluginRunTarget


def test_create_basic_plugin():
    plugin = PluginConfiguration(
        name="abc", files=["file.sh"], execute="file.sh")
    assert plugin.name == "abc"
    assert plugin.files == ["file.sh"]
    assert plugin.execute == "file.sh"
    assert plugin.args == []
    assert plugin.run_on == PluginRunTarget.Master


def test_create_with_args():
    plugin = PluginConfiguration(
        name="abc", args=["arg1", "arg2"])
    assert plugin.name == "abc"
    assert len(plugin.args) == 2
    assert plugin.args == ["arg1", "arg2"]


def test_plugin_with_internal_port():
    plugin = PluginConfiguration(name="abc", ports=[PluginPort(internal=1234)])
    assert plugin.name == "abc"
    assert len(plugin.ports) == 1
    port = plugin.ports[0]
    assert port.internal == 1234
    assert port.expose_publicly == False
    assert port.public_port == None

def test_plugin_with_auto_public_port():
    plugin = PluginConfiguration(name="abc", ports=[PluginPort(internal=1234, public=True)])
    assert plugin.name == "abc"
    assert len(plugin.ports) == 1
    port = plugin.ports[0]
    assert port.internal == 1234
    assert port.expose_publicly == True
    assert port.public_port == 1234

def test_plugin_with_specified_public_port():
    plugin = PluginConfiguration(name="abc", ports=[PluginPort(internal=1234, public=4321)])
    assert plugin.name == "abc"
    assert len(plugin.ports) == 1
    port = plugin.ports[0]
    assert port.internal == 1234
    assert port.expose_publicly == True
    assert port.public_port == 4321
