import unittest

from q2_motus.plugin_setup import plugin as motus_plugin


class PluginSetupTests(unittest.TestCase):

    def test_plugin_setup(self):
        self.assertEqual(motus_plugin.name, 'motus')