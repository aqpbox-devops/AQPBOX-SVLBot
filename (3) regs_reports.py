import pandas as pd
import argparse
from __init__ import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('report_file', type=str, help='Path to the final report file')

    args = parser.parse_args()

