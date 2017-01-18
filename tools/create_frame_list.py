from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os


def input_parser():
    description = ('Create a list from a source list. Each line of the source '
                   'list is a filename. For each line, it change the dirname '
                   'with other folder and remove any extension of the file')
    p = ArgumentParser(description=description,
                       formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument('-i', '--source_list', required=True,
                   help='Path to initial source list')
    p.add_argument('-o', '--output_list', required=True,
                   help='Filename of output list')
    p.add_argument('-d', '--dirname', required=True,
                   help='New dirname')
    return p


def main(source_list, output_list, dirname):
    """Create list replacing dirname of each line in input_list by output_dir
       and removing any extension.
    """
    locations = []
    with open(source_list, 'r') as f:
        for i in f:
            i = i.rstrip()

            # Grab basename and remove any extension
            basename = os.path.basename(i)
            video_name = os.path.splitext(basename)[0]

            # Maintain filesystem hierarchy (just 1 level XD)
            basedir = os.path.basename(os.path.dirname(i))

            locations.append(os.path.join(dirname, basedir, video_name))

    with open(output_list, 'w') as f:
        for line in locations:
            f.write(line + '\n')


if __name__ == "__main__":
    p = input_parser()
    main(**vars(p.parse_args()))
