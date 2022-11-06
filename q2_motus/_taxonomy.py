import os
import subprocess
import tempfile
from functools import partial
from typing import List, NamedTuple, Union, Literal, Tuple

import numpy as np
import pandas as pd
from q2_types.per_sample_sequences import (
    SingleLanePerSamplePairedEndFastqDirFmt,
    SingleLanePerSampleSingleEndFastqDirFmt)


def _run_command(cmd: List[str], verbose: bool = False) -> None:
    """Run a command in a subprocess.

    Parameters
    ----------
    cmd : str
        The command to run.
    verbose : bool, optional
        Whether to print the command before running it, by default False.

    Raises
    ------
    subprocess.CalledProcessError
        If the command returns a non-zero exit status.
    """
    if verbose:
        print(cmd)
    subprocess.run(cmd, check=True)


def preprocess_manifest(data: Union[SingleLanePerSampleSingleEndFastqDirFmt,
                                    SingleLanePerSamplePairedEndFastqDirFmt]) -> pd.DataFrame:

    """Extracts sample names and filepaths from manifest file."""

    manifest = pd.read_csv(os.path.join(str(data), data.manifest.pathspec),     
                           header=0, comment='#')

    manifest.filename = manifest.filename.apply(lambda x: os.path.join(str(data), x))
    id_to_fps = manifest.pivot(index='sample-id', columns='direction', values='filename')

    return id_to_fps


def profile_sample(
    row: NamedTuple,
    output_directory: str, 
    threads: int, 
    min_alen: int,
    marker_gene_cutoff: int, 
    mode: Literal["base.coverage", "insert.raw_counts", "insert.scaled_counts"],
    reference_genomes: bool,
    ncbi_taxonomy: bool) -> List[str]: 

    """Run motu-profiler on a single sample."""

    sample_name = row.Index
    reads = row[1:]

    cmd = ["motus", "profile"]

    # single-end reads
    if len(reads) == 1:
        cmd.extend(["-s", reads[0]])
    # paired-end reads
    elif len(reads) == 2:
        cmd.extend(["-f", reads[0], "-r", reads[1]])

    cmd.extend(["-n", sample_name, 
                "-o", os.path.join(output_directory, sample_name + ".motus"), 
                "-t", str(threads),
                "-l", str(min_alen),
                "-g", str(marker_gene_cutoff),
                "-y", str(mode),
                "-c", "-q"])

    if reference_genomes:
        cmd.extend(["-e"])
    
    if ncbi_taxonomy:
        cmd.extend(["-p"])

    p = _run_command(cmd)

    return cmd


def load_table_extract_tax(tab_fp: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    '''Converts merged mOTU table to feature table and taxonomy'''
    df = pd.read_csv(tab_fp, sep='\t', index_col=0, skiprows=2)
    df = df.replace({0 : np.nan})
    df.index = df.index.rename("Feature ID")
    df = df.rename(columns={"consensus_taxonomy": "Taxon"})
    id_col = "Feature ID"
    taxonomy_col = "Taxon"
    # dropping unassigned species
    df = df.dropna(axis = 0, thresh = df.shape[1] - 1)
    # getting taxonomy
    tax = df.reset_index()[[id_col, taxonomy_col]].copy().set_index(id_col)
    tax[taxonomy_col] = tax[taxonomy_col].str.replace("|", "; ", regex=True)
    df = df.drop(columns=[taxonomy_col])
    tab = df.fillna(0).T
    return tab, tax


def classify(
    samples: Union[SingleLanePerSamplePairedEndFastqDirFmt, 
                   SingleLanePerSampleSingleEndFastqDirFmt],
    threads: int, 
    min_alen: int = 75, 
    marker_gene_cutoff: int = 3,
    mode: Literal["base.coverage", "insert.raw_counts", "insert.scaled_counts"] = "insert.scaled_counts",
    reference_genomes: bool = False,
    ncbi_taxonomy: bool = False
    ) -> (pd.DataFrame, pd.DataFrame):
    """Run motu-profiler on paired-end samples data.

    Parameters
    ----------
    sequencing_data : PairEndSequencesWithQuality
        The paired-end sequencing data to be profiled.
    threads : int
        Number of threads to use.
    """

    id_to_fps = preprocess_manifest(samples)
    # Create temporary directory

    with tempfile.TemporaryDirectory() as temp_dir:
        profile_dir = os.path.join(temp_dir, "profiles")
        os.makedirs(profile_dir, exist_ok=True)
        # iterate over samples
        for row in id_to_fps.itertuples():
            profile_sample(row, profile_dir, threads, min_alen, marker_gene_cutoff, mode,
                           reference_genomes, ncbi_taxonomy)
        
        # merge profiles
        taxatable = os.path.join(temp_dir, "motus.merged")
        cmd = ["motus", "merge", "-d", profile_dir, "-o", taxatable]
        _run_command(cmd)

        # output merged profiles as feature table
        tab, tax = load_table_extract_tax(taxatable)
        return tab, tax