#!bin/bash
qiime tools import --type SampleData[PairedEndSequencesWithQuality] \
--input-path manifest_paired.tsv \
--output-path ../paired-end.qza \
--input-format PairedEndFastqManifestPhred33V2