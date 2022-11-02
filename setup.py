
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023, ETH Zurich
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from setuptools import setup, find_packages
import versioneer

setup(
    name="q2_motus",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    author="Alessio Milanese",
    author_email="alessio.milanese@biol.ethz.ch",
    description="QIIME2 implementation of the mOTU tool.",
    license='BSD-3-Clause',
    url="https://qiime2.org",
    entry_points={
        'qiime2.plugins':
        ['q2-motus=q2_motus.plugin_setup:plugin']
    },
    package_data={
        'q2_motus.tests': ['data/*'],
        'q2_motus': ['data/*', 'assets/index.html', 'citations.bib']},
    zip_safe=False,
)