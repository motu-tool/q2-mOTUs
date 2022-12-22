import pandas as pd 
from q2_types.feature_data import FeatureData, Taxonomy
from q2_types.feature_table import FeatureTable, Frequency
from q2_types.per_sample_sequences import (PairedEndSequencesWithQuality,
                                           SequencesWithQuality)
from q2_types.sample_data import SampleData
from qiime2.plugin import (Bool, Choices, Citations, Int, Plugin, Range,
                           SemanticType, Str)

import q2_motus
from q2_motus._taxonomy import import_table, profile
from q2_motus._format import MotusMergedAbundanceFormat, MotusMergedAbundanceDirectoryFormat

citations = Citations.load('citations.bib', package='q2_motus')

plugin = Plugin(
    name='motus',
    version=q2_motus.__version__,
    website="https://github.com/motu-tool/q2-motus",
    package='q2_motus',
    citations=[citations["Ruscheweyh2022"]],
    description=('This QIIME 2 plugin allows taxonomical profiling of '
                 'metagenomic samples using mOTU tool.'),
    short_description='Taxonomical profiling of metagenomic samples using mOTU.'
)


MotusMergedAbundanceTable = SemanticType('MotusMergedAbundanceTable')
plugin.register_semantic_types(MotusMergedAbundanceTable)

plugin.register_formats(MotusMergedAbundanceFormat,
                        MotusMergedAbundanceDirectoryFormat)
plugin.register_semantic_type_to_format(MotusMergedAbundanceTable, 
                                        MotusMergedAbundanceDirectoryFormat)

def _motus_to_df(path):
    result = pd.read_csv(str(path), sep='\t', header=0, index_col=0, skiprows=2)
    result.index.name = 'FeatureID'
    return result

@plugin.register_transformer
def _1(data: MotusMergedAbundanceFormat) -> pd.DataFrame:
    return _motus_to_df(data)


plugin.methods.register_function(
    function=profile,
    inputs={"samples": SampleData[SequencesWithQuality | PairedEndSequencesWithQuality]},
    outputs=[
        ("table", FeatureTable[Frequency]), 
        ("taxonomy", FeatureData[Taxonomy])
        ],
    parameters={"threads": Int % Range(1, None),
                "min_alen": Int % Range(1, None),
                "marker_gene_cutoff": Int % Range(1, 10),
                "mode": Str % Choices(["base.coverage", "insert.raw_counts", "insert.scaled_counts"]),
                "reference_genomes": Bool,
                "ncbi_taxonomy": Bool,
                "jobs": Int % Range(1, None)},
    name="mOTU profiler",
    description="Executes a taxonomical classification of a sample.",
    citations=[citations["Ruscheweyh2022"]],
    input_descriptions={"samples": "Samples for profiling."},
    parameter_descriptions={"threads": "The number of threads to use. We suggest using 4-8 threads.",
                            "min_alen": "Minimum alignment length.",
                            "marker_gene_cutoff": "Minimum number of marker genes to be considered a species." 
                                                  "Ranges from 1 to 10. A higher value increases precision (and lowers recall)",
                            "mode": "The mode to use for abundance estimation." 
                                    "base.coverage measures the average base coverage of the gene."
                                    "insert.raw_counts measures the number of reads that map to the gene."
                                    "insert.scaled_counts measures the number of reads that map to the gene, scaled by the length of the gene.",
                            "reference_genomes": "Use only species with reference genomes (ref-mOTUs).",
                            "ncbi_taxonomy": "Use NCBI taxonomy instead of mOTU.",
                            "jobs": "The number of jobs to use for the computation. Each job uses n threads from the threads parameter."},
    output_descriptions={"table": "The feature table with counts of marker genes in samples.",
                         "taxonomy": "The taxonomy."}
)


plugin.methods.register_function(
    function=import_table,
    inputs={"motus_table": MotusMergedAbundanceTable},
    outputs=[
        ("table", FeatureTable[Frequency]), 
        ("taxonomy", FeatureData[Taxonomy])
        ],
    parameters={"ncbi_taxonomy": Bool},
    name="mOTU table importer",
    description="Imports precomputed mOTU table to QIIME2.",
    citations=[citations["Ruscheweyh2022"]],
    input_descriptions={"motus_table": "The path to a precomputed merged mOTU table."},
    parameter_descriptions={"ncbi_taxonomy": "Use NCBI taxonomy instead of mOTU."},
    output_descriptions={"table": "The feature table with counts of marker genes in samples.",
                         "taxonomy": "The taxonomy."}
)
    