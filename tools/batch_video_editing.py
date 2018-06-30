#!/usr/bin/env python
"""

Launch ffmpeg from python to edit multiple videos at the same time

"""
import argparse
import logging
import os
import subprocess

from joblib import Parallel, delayed
import pandas as pd


def ffmpeg(filename, output_folder, filters, root):
    filename_noext = os.path.splitext(filename)[0]
    fstree = os.path.dirname(filename)
    output_dir = os.path.join(output_folder, fstree)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    output = os.path.join(output_dir, filename)

    filename = os.path.join(root, filename)
    if not os.path.isfile(filename):
        return filename_noext, False, 'unexistent file'

    cmd = ('ffmpeg -i {} {} {}'.format(filename, filters, output)).split()
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as err:
        msg = err.stdout.split('\n')[-2]
        return filename_noext, False, msg
    return filename_noext, True, 'success'


def main(args):
    args.filters = '-vf scale=320x240'
    logging.info('Editing videos')
    df = pd.read_csv(args.input_file, header=None)
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    status = Parallel(n_jobs=args.n_jobs, verbose=args.verbose)(
        delayed(ffmpeg)(i, args.output_dir, args.filters, args.root)
        for i in df.loc[:, 0])

    logging.info('Dumping report')
    with open(args.output_file, 'w') as fid:
        for i in status:
            fid.write('{},{},{}\n'.format(*i))
    logging.info('Succesful execution')


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description=('Edit a bunch of videos. TODO: the file-system '
                     'organization is preserved if relative-path are used.'))
    p.add_argument('-if', '--input-file', required=True,
                   help='CSV file with list of videos to process.')
    p.add_argument('-od', '--output-dir', help='Folder to allocate frames')
    p.add_argument('-of', '--output-file', help='CSV with report')
    p.add_argument('--filters', default='',
                   help='Filters for ffmpeg')
    # Workers
    p.add_argument('-n', '--n-jobs', default=4, type=int,
                   help='Max number of process')
    # Root folder
    p.add_argument('-r', '--root', default='',
                   help='Path where the videos are located.')
    p.add_argument('-v', '--verbose', default=5, type=int,
                   help='verbosity joblib')
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

    main(args)
