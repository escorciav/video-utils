from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import glob
import os


def get_id(filename):
    basename = os.path.basename(os.path.splitext(filename)[0])
    fparts = basename.split('-')
    return fparts[-1]


def input_parser():
    description = "Print ID of logging files that do not contain a token"
    p = ArgumentParser(description=description,
                       formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument('-d', '--logdir', required=True,
                   help='Path of folder with logging files')
    p.add_argument('-e', '--ext', default='.out',
                   help='Extension of logging files')
    p.add_argument('-t', '--token', default='Successful execution',
                   help='Token of success')
    return p


def main(logdir, ext, token):
    """Print files that does not have token
    """
    if not os.path.isdir(logdir):
        raise 'Unexistent directory {}'.format(logdir)

    buggous_id, counter = [], 0
    logfiles = glob.iglob(os.path.join(logdir, '*' + ext))
    for i in logfiles:
        counter += 1
        with open(i, 'r') as fid:
            log = fid.read()
            if token not in log:
                buggous_id.append(get_id(i))

    print 'Number of files parsed:', counter
    print 'Number of buggous files:', len(buggous_id)
    print ','.join(buggous_id)


if __name__ == "__main__":
    p = input_parser()
    main(**vars(p.parse_args()))
