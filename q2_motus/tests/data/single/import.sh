#!bin/bash
qiime tools import --type SampleData[SequencesWithQuality] \
--input-path manifest.tsv \
--output-path ../single-end.qza \
--input-format SingleEndFastqManifestPhred33V2