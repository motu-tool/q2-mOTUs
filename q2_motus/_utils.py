
import numpy as np
import pandas as pd
import re
import subprocess
from typing import List, Tuple


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


# Taxonomy formatting according to discussion 2023-01-16
def reformat_taxonomy(df: pd.DataFrame,
                      ref_col_name: str,
                      tax_col_name: str = "Taxon",
                      sep: str = "; ") -> pd.DataFrame:
    """
    Reformat taxonomy column to report mOTU results.

    Parameters
    ----------
    df : pd.DataFrame
        QIIME2 taxonomy dataframe.
    ref_col_name : str
        Name of the column containing the reference mOTU name.
    tax_col_name : str, optional
        Name of the column containing the full taxonomy, by default "Taxon".
    sep : str, optional
        Separator used in the taxonomy column, by default "; ".
    """

    df = df.reset_index()
    # iterate over rows
    for n, row in df.iterrows():

        taxonomy = row[tax_col_name].split(sep)

        revised_taxonomy = []
        unidentified = False
        for t in taxonomy:
            # find "incertae sedis" in t

            if re.search(r"incertae sedis", t, re.IGNORECASE):
                unidentified = True

            if unidentified:
                t = t[:3]

            if t.startswith("s__"):
                ref_motu = df.loc[n, ref_col_name]
                t = f"m__{ref_motu}"

            revised_taxonomy.append(t)

        df.loc[n, tax_col_name] = "; ".join(revised_taxonomy)

    df = df.set_index("Feature ID")

    return df


def load_motus_table(tab_fp: str) -> pd.DataFrame:
    """
    Load mOTUs table.

    Parameters
    ----------
    tab_fp : str
        Path to the mOTUs table.
    """
    df = pd.read_csv(tab_fp, sep='\t', index_col=0, skiprows=2)
    return df


def extract_table_tax(df: pd.DataFrame, ncbi: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract taxonomy and table from mOTUs table for QIIME2.

    Parameters
    ----------
    df : pd.DataFrame
        mOTUs table.
    ncbi : bool, optional
        Whether the table was generated using NCBI taxonomy, by default False.
    """

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