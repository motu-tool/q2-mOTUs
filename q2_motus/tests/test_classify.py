import os
import unittest
from warnings import filterwarnings

import biom
import numpy as np
import pandas as pd
import qiime2
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugins import motus

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
        self.expected_paired = _load_expected(os.path.join('expected', 'paired-end.motus'))
        self.expected_single = _load_expected(os.path.join('expected', 'single-end.motus'))

    def test_paired_end(self):
        paired_result = motus.actions.classify(samples=self.paired_end_sequences, 
                                               threads=4)

        observed_taxa_table = paired_result.table.view(pd.DataFrame)

        assert observed_taxa_table.equals(self.expected_paired)

    def test_single_end(self):
        single_result = motus.actions.classify(samples=self.single_end_sequences, 
                                               threads=4,
                                               mode='insert.raw_counts')

        observed_taxa_table = single_result.table.view(pd.DataFrame)

        assert set(observed_taxa_table.index) == set(self.expected_single.index)


if __name__ == '__main__':
    unittest.main()