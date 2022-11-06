import os
import unittest
from warnings import filterwarnings

import biom
import numpy as np
import pandas as pd
import qiime2
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugins import motus
from .._taxonomy import load_table_extract_tax


filterwarnings('ignore', category=UserWarning)
filterwarnings('ignore', category=RuntimeWarning)


class TestMotus(TestPluginBase):
    package = 'q2_motus.tests'

    def setUp(self):
        super().setUp()

        def _load(fp: str) -> qiime2.Artifact:
            return qiime2.Artifact.load(self.get_data_path(fp))

        def _load_expected(fp):
            df = pd.read_csv(self.get_data_path(fp), sep='\t', index_col=0, skiprows=2)
            df = df.replace({0 : np.nan})
            df = df.dropna(axis=0, thresh=df.shape[1] - 1)
            df = df.fillna(0).T
            return df 
        
        self.paired_end_sequences = _load('paired-end.qza')
        self.single_end_sequences = _load('single-end.qza')
        self.expected_paired = load_table_extract_tax(self.get_data_path(os.path.join('expected', 
                                                                                      'paired-end.motus')))
        self.expected_single = load_table_extract_tax(self.get_data_path(os.path.join('expected', 
                                                                                      'single-end.motus')),
                                                      ncbi=True)

    def test_paired_end(self):
        paired_result = motus.actions.profile(samples=self.paired_end_sequences, 
                                              threads=4, jobs=2)

        observed_taxa_table = paired_result.table.view(pd.DataFrame)

        assert observed_taxa_table.equals(self.expected_paired[0])

    def test_single_end(self):
        single_result = motus.actions.profile(samples=self.single_end_sequences, 
                                              threads=4,
                                              ncbi_taxonomy = True,
                                              mode='insert.raw_counts')

        observed_tax = single_result.taxonomy.view(pd.DataFrame)

        assert observed_tax.equals(self.expected_single[1])


if __name__ == '__main__':
    unittest.main()