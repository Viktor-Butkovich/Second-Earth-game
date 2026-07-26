from __future__ import annotations
from typing import List
import pandas as pd


def read_csv(file_path: str) -> List[str]:
    """
    Description:
        Reads in .csv file and returns contents
    Input:
        string file_path: file path of .csv file
    Output:
        string list: List of string lines of the .csv file
    """
    return pd.read_csv(file_path, header=None)[0].astype(str).tolist()
