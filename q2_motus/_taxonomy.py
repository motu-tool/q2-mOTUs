import os
import subprocess
import tempfile
from functools import partial
from multiprocessing import Pool
from typing import List, Literal, NamedTuple, Tuple, Union

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
    subprocess.call(cmd)


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
    min_alen: int = 75,
    marker_gene_cutoff: int = 3,
    mode: Literal["base.coverage", "insert.raw_counts", "insert.scaled_counts"] = "insert.scaled_counts",
    reference_genomes: bool = False,
    ncbi_taxonomy: bool = False) -> List[str]:

    """Run motu-profiler on a single sample."""

    sample_name = row[0]
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


def load_motus_table(tab_fp: str) -> pd.DataFrame:
    df = pd.read_csv(tab_fp, sep='\t', index_col=0, skiprows=2)
    return df


def extract_table_tax(df: pd.DataFrame, ncbi: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = df.replace({0 : np.nan})
    df.index.name = "Feature ID"
    if ncbi:
        df = df.rename(columns={"NCBI_tax_id" : "Taxon"})
    else:
        df = df.rename(columns={"consensus_taxonomy": "Taxon"})

    id_col = "Feature ID"
    taxonomy_col = "Taxon"

    # getting taxonomy
    tax = df.reset_index()[[id_col, taxonomy_col]].copy().set_index(id_col)
    tax[taxonomy_col] = tax[taxonomy_col].str.replace("|", "; ", regex=True)

    if ncbi:
        df = df.drop(columns = [taxonomy_col, "consensus_taxonomy"])
    else:
        df = df.drop(columns=[taxonomy_col])

    tab = df.dropna(axis=0, thresh=1)
    tab = tab.fillna(0).T
    tax = tax[tax.index.isin(tab.columns)]

    return tab, tax


def profile(
    samples: Union[SingleLanePerSamplePairedEndFastqDirFmt,
                   SingleLanePerSampleSingleEndFastqDirFmt],
    threads: int,
    min_alen: int = 75,
    marker_gene_cutoff: int = 3,
    mode: Literal["base.coverage", "insert.raw_counts", "insert.scaled_counts"] = "insert.scaled_counts",
    reference_genomes: bool = False,
    ncbi_taxonomy: bool = False,
    jobs: int = 1
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
        reads_tuples = id_to_fps.itertuples(name=None)
        func = partial(profile_sample, output_directory=profile_dir, threads=threads,
                       min_alen=min_alen, marker_gene_cutoff=marker_gene_cutoff, mode=mode,
                       reference_genomes=reference_genomes, ncbi_taxonomy=ncbi_taxonomy)

        with Pool(jobs) as pool:
            pool.map(func, reads_tuples)

        # merge profiles
        taxatable = os.path.join(temp_dir, "motus.merged")
        cmd = ["motus", "merge", "-d", profile_dir, "-o", taxatable]
        _run_command(cmd)

        # output merged profiles as feature table
        tab, tax = extract_table_tax(load_motus_table(taxatable), ncbi_taxonomy)
        return tab, tax


def import_table(
    motus_table: pd.DataFrame,
    ncbi_taxonomy: bool = False) -> (pd.DataFrame, pd.DataFrame):

    tab, tax = extract_table_tax(motus_table, ncbi=ncbi_taxonomy)
    return tab, tax