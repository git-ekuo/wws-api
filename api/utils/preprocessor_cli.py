"""
A command prompt CLI to help ingest new data
"""
import argparse

from api.ingest.preprocess import Preprocessor

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-process files for year-month combination')
    parser.add_argument('year', type=int, help='an integer representing the year, e.g., 2017')
    parser.add_argument('path', help='a string indicating the system path leading to where the data is. '
                                     'e.g., /s3bucket/')

    args = parser.parse_args()
    year = args.year
    data_path = args.path
    Preprocessor.preprocess(year, data_path)
