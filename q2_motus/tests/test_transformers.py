import pandas as pd
from pandas.testing import assert_frame_equal

from qiime2.plugin.testing import TestPluginBase

from q2_motus import (
    MotusMergedAbundanceFormat)

from .._taxonomy import extract_table_tax


class TestMotusFormatTransformers(TestPluginBase):
    package = 'q2_motus.tests'

    def test_motus_merged_abundance_no_ncbi(self):
        exp = pd.DataFrame([
            ['ref_mOTU_v3_00095', 1.0, 0.0],
            ['ref_mOTU_v3_00096', 1.0, 0.0],
            ['ref_mOTU_v3_00855', 0.0, 1.0],
            ['ref_mOTU_v3_02367', 0.0, 1.0],
            ['ref_mOTU_v3_03592', 1.0, 0.0],
            ['ref_mOTU_v3_03928', 0.0, 1.0],
            ['ref_mOTU_v3_04716', 1.0, 1.0],
            ['ref_mOTU_v3_05238', 1.0, 0.0],
            ['meta_mOTU_v3_12805', 1.0, 0.0],
            ['ext_mOTU_v3_26730', 1.0, 0.0],
            ['unassigned', 1.0, 1.0]
        ], columns=['Feature ID', 'sampleA', 'sampleB'])
        exp = exp.set_index('Feature ID').T

        _, obs = self.transform_format(
            MotusMergedAbundanceFormat, pd.DataFrame, filename="expected/paired-end.motus")

        obs_tab, obs_tax = extract_table_tax(obs)

        assert_frame_equal(obs_tab, exp)