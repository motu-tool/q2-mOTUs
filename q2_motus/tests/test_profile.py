import os
import unittest
from warnings import filterwarnings

import pandas as pd
from pandas.testing import assert_frame_equal

import qiime2
from qiime2.plugin.testing import TestPluginBase
from q2_motus import MotusMergedAbundanceTable
from qiime2.plugins import motus
from .._taxonomy import load_motus_table, extract_table_tax
from .._utils import reformat_taxonomy

filterwarnings('ignore', category=UserWarning)
filterwarnings('ignore', category=RuntimeWarning)
filterwarnings('ignore', category=DeprecationWarning)


class TestMotus(TestPluginBase):
    package = 'q2_motus.tests'

    def setUp(self):
        super().setUp()

        def _load(fp: str) -> qiime2.Artifact:
            return qiime2.Artifact.load(self.get_data_path(fp))

        def _load_expected(fp):
            df = load_motus_table(self.get_data_path(fp))
            tab, tax = extract_table_tax(df)
            tax = reformat_taxonomy(tax, ref_col_name="Feature ID")
            return tab, tax

        self.paired_end_sequences = _load('paired-end.qza')
        self.single_end_sequences = _load('single-end.qza')
        self.expected_paired = _load_expected(os.path.join('expected', 'paired-end.motus'))
        self.expected_tax_single = _load_expected(os.path.join('expected', 'single-end.motus'))[1]


    def test_proifle_paired_end(self):
        paired_result = motus.actions.profile(samples=self.paired_end_sequences,
                                              threads=4, jobs=2)

        observed_taxa_table = paired_result.table.view(pd.DataFrame)
        observed_taxa_table.columns.name = 'Feature ID'

        assert_frame_equal(observed_taxa_table, self.expected_paired[0])

    def test_profile_single_end(self):
        single_result = motus.actions.profile(samples=self.single_end_sequences,
                                              threads=4,
                                              mode='insert.raw_counts')

        observed_tax = single_result.taxonomy.view(pd.DataFrame)

        assert_frame_equal(observed_tax, self.expected_tax_single)

    def test_import_table(self):
        input = qiime2.Artifact.import_data(MotusMergedAbundanceTable, self.get_data_path('expected/paired-end.motus'))
        result = motus.actions.import_table(input)
        observed_taxa_table = result.table.view(pd.DataFrame)
        observed_taxa_table.columns.name = 'Feature ID'

        assert_frame_equal(observed_taxa_table, self.expected_paired[0])


if __name__ == '__main__':
    unittest.main()