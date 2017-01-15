#!/usr/bin/env python
"""

Python program to dump CSV with duration and frame rate of many videos

"""
import argparse

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from okvideo.ffmpeg import get_duration, get_frame_rate


def video_stats(filename):
    stats = []
    stats.append(get_duration(filename))
    stats.append(get_frame_rate(filename))
    return stats


def input_parse():
    description = 'Get information (duration, frame-rate) of several videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('-if', '--input-file', required=True,
                   help=('CSV file with list of videos to process. Remove any '
                         'header or comments. Use "\t" as separator if any.'))
    p.add_argument('-of', '--output-file', required=True,
                   help='CSV-file with duration (s) and frame rate of videos')
    p.add_argument('-n', '--n-jobs', default=1, type=int,
                   help='Number of CPUs')
    args = p.parse_args()
    return args


def main(input_file, output_file, n_jobs):
    df = pd.read_csv(input_file, sep='\t', header=None)
    stats = Parallel(n_jobs=n_jobs)(delayed(video_stats)(i)
                                    for i in df.loc[:, 0])
    df_stat = pd.DataFrame(np.array(stats),
                           columns=['video-name', 'duration', 'frame-rate'])
    new_df = pd.concat((df, df_stat), axis=1)
    new_df.to_csv(output_file, sep='\t', index=False)


if __name__ == '__main__':
    args = input_parse()
    main(**vars(args))
