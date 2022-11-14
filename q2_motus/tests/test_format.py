from q2_motus import (
    MotusMergedAbundanceFormat,
)
from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

class TestMotusMergedAbundanceFormat(TestPluginBase):
    package = 'q2_motus.tests'

    def test_motus_merged_abundance_format_valid(self):
        filenames = ['motus-merged-abundance-1.tsv']
        filepaths = [self.get_data_path(filename)
                     for filename in filenames]

        for filepath in filepaths:
            format = MotusMergedAbundanceFormat(filepath, mode='r')
            format.validate()

    def test_motus_merged_abundance_format_no_samples(self):
        filenames = ['motus-merged-abundance-2.tsv']
        filepaths = [self.get_data_path(filename)
                     for filename in filenames]

        for filepath in filepaths:
            with self.assertRaisesRegex(ValidationError, 'No sample columns'):
                format = MotusMergedAbundanceFormat(filepath, mode='r')
                format.validate()

    def test_motus_merged_abundance_format_invalid_value_type(self):
        filenames = ['motus-merged-abundance-3.tsv']
        filepaths = [self.get_data_path(filename)
                     for filename in filenames]

        for filepath in filepaths:
            with self.assertRaisesRegex(ValidationError, 'int.*'):
                format = MotusMergedAbundanceFormat(filepath, mode='r')
                format.validate()

    def test_motus_merged_abundance_format_extra_column(self):
        filenames = ['motus-merged-abundance-4.tsv']
        filepaths = [self.get_data_path(filename)
                     for filename in filenames]

        for filepath in filepaths:
            with self.assertRaisesRegex(ValidationError, 'int.*abs'):
                format = MotusMergedAbundanceFormat(filepath, mode='r')
                format.validate()

    def test_motus_merged_abundance_inconsistent_columns(self):
        filenames = ['motus-merged-abundance-5.tsv']
        filepaths = [self.get_data_path(filename)
                     for filename in filenames]

        for filepath in filepaths:
            with self.assertRaisesRegex(ValidationError, 'Number of columns'):
                format = MotusMergedAbundanceFormat(filepath, mode='r')
                format.validate()

    def test_motus_not_merged_abundance(self):
        filenames = ['expected/single-end.motus']
        filepaths = [self.get_data_path(filename)
                     for filename in filenames]

        for filepath in filepaths:
            with self.assertRaisesRegex(ValidationError, 'not a merged'):
                format = MotusMergedAbundanceFormat(filepath, mode='r')
                format.validate()
            
