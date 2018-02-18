#!/usr/bin/env python
"""

Python program to dump CSV with duration and frame rate of many videos

"""
import argparse
import os

import pandas as pd
from joblib import Parallel, delayed

from okvideo.ffmpeg import (get_duration, get_frame_rate, get_num_frames,
                            get_resolution)


def video_stats(filename, video_path):
    stats = []
    stats.append(os.path.basename(os.path.splitext(filename)[0]))
    filename = os.path.join(video_path, filename)
    stats.append(get_duration(filename))
    stats.append(get_frame_rate(filename))
    stats.append(get_num_frames(filename))
    stats.extend(list(get_resolution(filename)))
    return stats


def main(input_file, output_file, n_jobs, video_path):
    df = pd.read_csv(input_file, header=None)
    stats = Parallel(n_jobs=n_jobs, verbose=5)(
        delayed(video_stats)(i, video_path)
        for i in df.loc[:, 0])
    df_stat = pd.DataFrame(stats,
                           columns=['video-name', 'duration', 'frame-rate',
                                    'num-frames', 'width', 'height'])
    df_stat.to_csv(output_file, index=False)


if __name__ == '__main__':
    description = 'Get information (duration, frame-rate) of several videos.'
    epilog = ('This program uses FFPROBE to grab video information. We '
              'highly recommended to ensure that frame-rate, num-frames, '
              'duration correspond among them.')
    p = argparse.ArgumentParser(description=description, epilog=epilog)
    p.add_argument('-if', '--input-file', required=True,
                   help=('CSV-file with list of videos to process. Remove any '
                         'header or comments. Use "\t" as separator if any.'))
    p.add_argument('-of', '--output-file', required=True,
                   help=('CSV-file with video-name, duration (s), frame-rate, '
                         'number-frames, width, height'))
    p.add_argument('-n', '--n-jobs', default=4, type=int,
                   help='Number of process to spawn with joblib')
    p.add_argument('-vpath', '--video-path', default=None,
                   help='Path where the videos are located.')
    args = p.parse_args()
    main(**vars(args))
