from __future__ import annotations
import csv


def read_csv(file_path):
    """
    Description:
        Reads in .csv file and returns contents
    Input:
        string file_path: file path of .csv file
    Output:
        string list list: list of lists containing 1 string each, with each string being a line of the .csv file
    """
    line_list = []
    file = open(file_path, "r")
    csv_reader = csv.reader(file)

    for current_line in csv_reader:
        line_list.append(current_line)
    file.close()
    return line_list
