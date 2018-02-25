#!/usr/bin/env python
"""

Launch ffmpeg from python to edit multiple videos at the same time

"""
import argparse
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
        return filename_noext, False, 'Unexistent file'

    cmd = ('ffmpeg -i {} {} {}'.format(filename, filters, output)).split()
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as err:
        msg = err.stdout.split('\n')[-2]
        return filename_noext, False, msg
    return filename_noext, True, 'Done'


def main(input_file, output_dir, output_file, filters, n_jobs, root):
    df = pd.read_csv(input_file, header=None)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    status = Parallel(n_jobs=n_jobs, verbose=3)(
        delayed(ffmpeg)(i, output_dir, filters, root)
        for i in df.loc[:, 0])

    with open(output_file, 'w') as fid:
        for i in status:
            fid.write('{},{},{}\n'.format(*i))


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
    args = p.parse_args()

    main(**vars(args))
