In this tutorial, we would like to demonstrate how the `q2-mOTUs` fits into the QIIME 2 framework. We will use the study `PRJEB52147` and its metadata from Qiita `ID 13241`. The article is published in [Scientific Reports](https://www.nature.com/articles/s41598-022-10276-y).

First, we import the quality-controlled metagenomic sequencing data similarly as we do it for test data using `Manifest` file and `qiime tools import`. An example might be found in [paired](https://github.com/motu-tool/q2-mOTUs/tree/main/q2_motus/tests/data/paired) folder. Artifact was not uploaded to GitHub due to a large filesize. 

## Profiling metagenomic samples

```
qiime motus profile \
--i-samples $TMPDIR/study-seqs.qza \
--p-threads 8 \
--o-table artifacts/motu-table.qza \
--o-taxonomy artifacts/motu-taxonomy.qza
``` 

Now, we make a summary of the `FeatureTable[Frequency]` artifact `motu-table.qza`. 
```
qiime feature-table summarize \
--i-table artifacts/motu-table.qza \
--o-visualization visualizations/motu-table-summary.qzv
```

[motu-table-summary.qzv](https://view.qiime2.org/visualization/?type=html&src=https%3A%2F%2Fdl.dropbox.com%2Fs%2Fvsedg96hb6uayjw%2Fmotu-table-summary.qzv%3Fdl%3D1)

## Exploratory analysis 

We will create a PCoA using Bray-Curtis distance metric for our samples to get an overview of samples. 
### Creating a distance matrix
First, let's create a DistanceMatrix artifact using `qiime diversity beta` command. 

```
qiime diversity beta --i-table artifacts/motu-table.qza \
--p-metric braycurtis \
--o-distance-matrix artifacts/bc-distances.qza
```

### Calculating PCoA

Then, lets calculate PCoA using `qiime diversity pcoa` command. 

```
qiime diversity pcoa \
--i-distance-matrix artifacts/bc-distances.qza \
--o-pcoa artifacts/bc-pcoa.qza
```

### Visualizing results
And visualize results using `Emperor`. 

```
qiime emperor plot --i-pcoa artifacts/bc-pcoa.qza \
--m-metadata-file artifacts/metadata.tsv \
--o-visualization visualizations/bc-emperor.qzv
```

[bc-emperor.qzv](https://view.qiime2.org/visualization/?type=html&src=https%3A%2F%2Fdl.dropbox.com%2Fs%2F7tsb7mrhfxq1ztf%2Fbc-emperor.qzv%3Fdl%3D1)

We might see, that different sample types cluster together. We will filter only samples for `feces`. 
    
```
qiime feature-table filter-samples \
--i-table artifacts/motu-table.qza \
--m-metadata-file artifacts/PRJEB52147_metadata.qza \
--p-where "[sample_type]='feces'" \
--o-filtered-table artifacts/motu-table-feces.qza
```

## Taxnomomy visualization

Now, we'll create visualizations of out taxonomical profiles using `taxa barplot`.

```
qiime taxa barplot \
--i-table artifacts/motu-table-feces.qza \
--i-taxonomy artifacts/motu-taxonomy.qza \
--m-metadata-file artifacts/PRJEB52147_metadata.qza \
--o-visualization visualizations/motu-taxa-barplot-feces.qzv
```

[motu-taxa-barplot-feces.qzv](https://view.qiime2.org/visualization/?type=html&src=https%3A%2F%2Fdl.dropbox.com%2Fs%2Frtz0klfpvbsxsfj%2Fmotu-taxa-barplot-feces.qzv%3Fdl%3D1)


Then, we'll make a Krona plot, which allows us an interactive exploration of the taxonomic composition of samples.  

```
qiime krona collapse-and-plot \
--i-table artifacts/motu-table-feces.qza \
--i-taxonomy artifacts/motu-taxonomy.qza \
--o-krona-plot visualizations/motu-krona-feces.qzv
```

[motu-krona-feces.qzv](https://view.qiime2.org/visualization/?type=html&src=https%3A%2F%2Fdl.dropbox.com%2Fs%2F51kurmw326jxjie%2Fmotu-krona-feces.qzv%3Fdl%3D1)


## Hypothesis testing 

We will test if maternal asthma has a significant influence on fecal microbiome composition using Bray-Curtis distance metric. 
### Creating a distance matrix

```
qiime diversity beta \
--i-table artifacts/motu-table-feces.qza \
--p-metric braycurtis \
--o-distance-matrix artifacts/bc-distances-feces.qza
```
### Conducting a test
```
qiime diversity beta-group-significance \
--i-distance-matrix artifacts/bc-distances-feces.qza \
--m-metadata-file artifacts/PRJEB52147_metadata.qza \
--m-metadata-column diagnosis \
--o-visualization visualizations/bc-distances-feces-disagnosis.qzv
```

[bc-distances-feces-diagnosis.qzv](https://view.qiime2.org/visualization/?type=html&src=https%3A%2F%2Fdl.dropbox.com%2Fs%2F455at5yxx7accvy%2Fbc-distances-feces-diagnosis.qzv%3Fdl%3D1)

## Differential abundance testing

### Adding pseudocount 

We will see which taxa are differentially abundant between `feces` and `meconium` samples using `ANCOM` method. 
First, we will collapse our table to species level. 

```
qiime taxa collapse \
--i-table artifacts/motu-table.qza \
--i-taxonomy artifacts/motu-taxonomy.qza \
--p-level 6 \
--o-collapsed-table artifacts/motu-table-genus.qza
```

ANCOM is a compositional data analysis method, that cannot work with zeros. We will add a pseudocount of 1 and create a `FeatureTable[Composition]` artifact. 

```
qiime composition add-pseudocount \
--i-table artifacts/motu-table-genus.qza \
--p-pseudocount 1 \
--o-composition-table artifacts/motu-table-genus-ancom.qza
```
### Conducting a test

Then, we will run `ANCOM` using `qiime composition ancom` command. 

```
qiime composition ancom \
--i-table artifacts/motu-table-genus-ancom.qza \
--m-metadata-file artifacts/PRJEB52147_metadata.qza \
--m-metadata-column sample_type \
--o-visualization visualizations/motu-table-ancom.qzv
```

[motu-table-ancom.qzv](https://view.qiime2.org/visualization/?type=html&src=https%3A%2F%2Fdl.dropbox.com%2Fs%2Fp1648h8x2ux7qak%2Fmotu-table-ancom.qzv%3Fdl%3D1)

# Conclusions

`q2-mOTUs` plugin allows taxonomical profiling of metagenomic sequencing data. We demonstrated, that its output can be used for robust downstream analysis in QIIME2, thus complementing already existing software.

