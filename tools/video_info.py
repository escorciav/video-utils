#!/usr/bin/env python
"""

Python program to dump CSV with duration and frame rate of many videos

"""
import argparse
import os

import pandas as pd
from joblib import Parallel, delayed

from okvideo.ffmpeg import get_duration, get_frame_rate, get_num_frames


def video_stats(filename):
    stats = []
    stats.append(os.path.basename(os.path.splitext(filename)[0]))
    stats.append(get_duration(filename))
    stats.append(get_frame_rate(filename))
    stats.append(get_num_frames(filename))
    return stats


def input_parse():
    description = 'Get information (duration, frame-rate) of several videos.'
    epilog = ('This program uses FFPROBE to grab video information. It is '
              'highly recommended to ensure that frame-rate, num-frames, '
              'duration correspond among them.')
    p = argparse.ArgumentParser(description=description, epilog=epilog)
    p.add_argument('-if', '--input-file', required=True,
                   help=('TSV-file with list of videos to process. Remove any '
                         'header or comments. Use "\t" as separator if any.'))
    p.add_argument('-of', '--output-file', required=True,
                   help=('TSV-file with video-name, duration (s), frame rate, '
                         'number of frames of videos'))
    p.add_argument('-n', '--n-jobs', default=1, type=int,
                   help='Number of process to spawn with joblib')
    args = p.parse_args()
    return args


def main(input_file, output_file, n_jobs):
    df = pd.read_csv(input_file, sep='\t', header=None)
    stats = Parallel(n_jobs=n_jobs)(delayed(video_stats)(i)
                                    for i in df.loc[:, 0])
    df_stat = pd.DataFrame(stats,
                           columns=['video-name', 'duration', 'frame-rate',
                                    'num-frames'])
    df_stat.to_csv(output_file, sep='\t', index=False)


if __name__ == '__main__':
    args = input_parse()
    main(**vars(args))
