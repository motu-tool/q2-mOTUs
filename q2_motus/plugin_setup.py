import q2_motus

from qiime2.plugin import (Int, Range, Str, Bool, Choices, Plugin, Citations) 

from q2_motus._taxonomy import classify
from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import SequencesWithQuality, PairedEndSequencesWithQuality
from q2_types.feature_table import FeatureTable, Frequency

citations = Citations.load('citations.bib', package='q2_motus')

plugin = Plugin(
    name='motus',
    version=q2_motus.__version__,
    website="https://github.com/motu-tool/q2-motus",
    package='q2_motus',
    citations=[citations["Milanese2019-gw"]],
    description=('This QIIME 2 plugin allows taxonomical profiling of '
                 'metagenomic samples using mOTU tool.'),
    short_description='Taxonomical profiling of metagenomic samples using mOTU.'
)


plugin.methods.register_function(
    function=classify,
    inputs={"samples": SampleData[SequencesWithQuality | PairedEndSequencesWithQuality]},
    outputs=[("table", FeatureTable[Frequency]), 
             ("taxonomy", FeatureData[Taxonomy])],
    parameters={"threads": Int % Range(1, None),
                "min_alen": Int % Range(1, None),
                "marker_gene_cutoff": Int % Range(1, 10),
                "mode": Str % Choices(["base.coverage", "insert.raw_counts", "insert.scaled_counts"]),
                "reference_genomes": Bool,
                "ncbi_taxonomy": Bool,
                "full_taxonomy": Bool,
                "taxonomy_level": Str % Choices(["mOTU", "genus", "family", "order", "class", "phylum", "kingdom"])},
    name="mOTU paired end profiler",
    description="Executes a taxonomical classification of paired-end sample.",
    input_descriptions={"samples": "The paired-end samples to be classified."},
    parameter_descriptions={"threads": "The number of threads to use.",
                            "min_alen": "Minimum alignment length.",
                            "marker_gene_cutoff": "Minimum number of marker genes to be considered a species." 
                                                  "Ranges from 1 to 10. A higher value increases precision (and lowers recall)",
                            "mode": "The mode to use for abundance estimation." 
                                    "base.coverage measures the average base coverage of the gene."
                                    "insert.raw_counts measures the number of reads that map to the gene."
                                    "insert.scaled_counts measures the number of reads that map to the gene, scaled by the length of the gene.",
                            "reference_genomes": "Use only species with reference genomes (ref-mOTUs).",
                            "ncbi_taxonomy": "Use NCBI taxonomy instead of mOTU.",
                            "full_taxonomy": "Use full taxonomy.",
                            "taxonomy_level": "The taxonomy level to use for profiling."})