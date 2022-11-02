import q2_motus

from qiime2.plugin import (Int, Str, Float, Plugin, Citations, Metadata,
                           Visualization)

from q2_motus._hello import print_hello

plugin = Plugin(
    name='motus',
    version=q2_motus.__version__,
    website="https://github.com/motu-tool/q2-motus",
    package='q2_motus',
    citations=Citations.load('citations.bib', package='q2_motus'),
    description=('This QIIME 2 plugin allows taxonomical profiling of '
                 'metagenomic samples using mOTU tool.'),
    short_description='Taxonomical profiling of metagenomic samples using mOTU.'
)


plugin.visualizers.register_function(
    function=print_hello,
    inputs={},
    parameters={},
    input_descriptions={},
    parameter_descriptions={},
    name='Print hello.',
    description='Print hello on the screen.'
)