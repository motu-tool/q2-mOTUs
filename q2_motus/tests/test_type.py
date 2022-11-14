from q2_motus import (
    MotusMergedAbundanceTable, 
    MotusMergedAbundanceDirectoryFormat
)

from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = 'q2_motus.tests'

    def test_metaphlan_semantic_types_registration(self):
        self.assertRegisteredSemanticType(MotusMergedAbundanceTable)
        self.assertSemanticTypeRegisteredToFormat(
            MotusMergedAbundanceTable,
            MotusMergedAbundanceDirectoryFormat)