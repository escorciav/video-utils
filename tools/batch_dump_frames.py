#!/usr/bin/env python
"""

Python program to dump frames of many videos

"""
import argparse
import logging
import os

from joblib import Parallel, delayed
import pandas as pd

from okvideo.ffmpeg import dump_frames


def main(input_file, output_folder, baseformat, filters, n_jobs,
         fullpath_flag, video_path):
    df = pd.read_csv(input_file, header=None)
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    Parallel(n_jobs=n_jobs)(
        delayed(dump_wrapper)(i, output_folder, baseformat, filters,
                              fullpath_flag, video_path)
        for i in df.loc[:, 0])
    return None


def dump_wrapper(filename, output_folder, baseformat, filters, fullpath_flag,
                 video_path):
    filename_noext = os.path.splitext(filename)[0]
    if fullpath_flag:
        filename_noext = os.path.basename(filename_noext)
    if video_path:
        filename = os.path.join(video_path, filename)
    output_dir = os.path.join(output_folder, filename_noext)
    if not os.path.isfile(filename):
        logging.debug('Unexistent file {}'.format(filename))
        return False
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    output = os.path.join(output_dir, baseformat)
    return dump_frames(filename, output, filters)


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description=('Extract frames of a bunch of videos. The file-system '
                     'organization is preserved if relative-path are used.'))
    p.add_argument('-if', '--input-file', required=True,
                   help='CSV file with list of videos to process.')
    p.add_argument('-of', '--output-folder', help='Folder to allocate frames')
    p.add_argument('-bf', '--baseformat', default='%06d.jpg',
                   help='Format used for naming frames e.g. %%06d.jpg')
    p.add_argument('--filters', default='',
                   help='Filters for ffmpeg')
    # Workers
    p.add_argument('-n', '--n-jobs', default=1, type=int,
                   help='Max number of process')
    # Video path
    p.add_argument('-ff', '--fullpath-flag', action='store_true',
                   help='Input-file uses fullpath instead of rel-path')
    p.add_argument('-vpath', '--video-path', default=None,
                   help='Path where the videos are located.')
    # Logging
    p.add_argument('-log', '--loglevel', default='INFO',
                   help='verbosity level')
    args = p.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(
        format=('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d]: '
                '%(message)s'),
        level=numeric_level)
    delattr(args, 'loglevel')

    main(**vars(args))
