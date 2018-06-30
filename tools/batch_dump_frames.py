"Python program to dump frames of many videos"
import argparse
import logging
import os
from pathlib import Path

from joblib import Parallel, delayed
import pandas as pd

from okvideo.ffmpeg import dump_frames


def dump_wrapper(filename, dirname, frame_format, filters, root):
    filename_noext = os.path.splitext(filename)[0]
    if root.is_dir():
        filename = root / filename
    else:
        filename = Path(filename)
    frame_dir = dirname / filename_noext
    if not filename.is_file():
        logging.debug('Unexistent file {}'.format(filename))
        return filename_noext, False
    if not frame_dir.is_dir():
        os.makedirs(str(frame_dir))

    output = frame_dir / frame_format
    flag = dump_frames(filename, output, filters)
    return filename_noext, flag


def main(args):
    logging.info('Dumping frames')
    df = pd.read_csv(args.input_file, header=None)
    if not args.dirname.is_dir():
        os.makedirs(str(args.dirname))
    status = Parallel(n_jobs=args.n_jobs, verbose=args.verbose)(
        delayed(dump_wrapper)(
            i, args.dirname, args.frame_format, args.filters, args.root)
        for i in df.loc[:, 0])
    logging.info('Dumping report')

    with open(args.summary, 'w') as fid:
        for i in status:
            fid.write('{},{}\n'.format(*i))
    logging.info('Succesful execution')


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description=('Extract frames of a bunch of videos. The file-system '
                     'organization is preserved if relative-path are used.'))
    p.add_argument('-i', '--input-file', required=True,
                   help='CSV file with list of videos to process.')
    p.add_argument('-o', '--dirname', type=Path,
                   help='Folder to allocate frames')
    p.add_argument('-s', '--summary', help='CSV with report')
    p.add_argument('-f', '--frame-format', default='%06d.jpg',
                   help='Format used for naming frames e.g. %%06d.jpg')
    p.add_argument('--filters', default='',
                   help='Filters for ffmpeg')
    p.add_argument('-r', '--root', type=Path, default=Path('rng-vg-nfmf'),
                   help='Path where the videos are located.')
    # Workers
    p.add_argument('-n', '--n-jobs', default=4, type=int,
                   help='Max number of process')
    # Logging
    p.add_argument('--verbose', type=int, default=0,
                   help='verbosity level')
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
