import glob
import json
import os
import shutil
import subprocess
import uuid
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from joblib import delayed
from joblib import Parallel
import pandas as pd


def construct_video_filename(row, dirname, trim_format):
    "Given a dataset row, create the output filename for a given video"
    basename = trim_format.format(row['youtube_id'])
    output_filename = os.path.join(dirname, basename)
    return output_filename


def download_video(video_identifier, dirname, num_attempts=5,
                   url_base='https://www.youtube.com/watch?v='):
    "Download video with youtube-dl"
    # Construct command line for getting the direct video link.
    filename = os.path.join(dirname, '%s.%%(ext)s' % uuid.uuid4())
    command = ['youtube-dl',
               '--quiet', '--no-warnings',
               '-f', 'mp4',
               '-o', '"%s"' % filename,
               '"%s"' % (url_base + video_identifier)]
    command = ' '.join(command)
    attempts = 0
    while True:
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT,
                                    shell=True)
        except subprocess.CalledProcessError as err:
            attempts += 1
            if attempts == num_attempts:
                return False, err.output
        else:
            break
    filename = glob.glob('%s*' % filename.split('.')[0])[0]
    return True, filename


def trim_video(filename, output_filename, start_time, end_time):
    "Trim video"
    status, msg = True, 'Downloaded'

    if end_time == 0:
        # Not trim
        shutil.move(filename, output_filename)
        return status, msg
    elif end_time < 0:
        # reencode video with size 320:420
        filters = ['-vf', 'scale=320:240']
    else:
        # trim video
        filters = ['-ss', str(start_time),
                   '-t', str(end_time - start_time)]

    # Construct command to trim the videos (ffmpeg required).
    command = (['ffmpeg',
                '-i', '"%s"' % filename] +
               filters +
               ['-c:v', 'libx264', '-c:a', 'copy',
                '-loglevel', 'panic',
                '"%s"' % output_filename])
    command = ' '.join(command)
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as err:
        print(' '.join(command))  # delete-me
        status, msg = False, err.output

    if not status and os.path.exists(output_filename):
        os.remove(output_filename)
    # os.remove(filename)
    return status, msg


def get_video(video_identifier, filename, start_time, end_time,
              tmp_dir='/tmp/kinetics'):
    """Download and clip a video from youtube if exists and is not blocked.

    Args:
        video_identifier (string): Unique YouTube video identifier
            (11 characters)
        filename (string): file path where the video will be stored.
        start_time (float): begining time in seconds from where the video
            will be trimmed.
        end_time (float) : ending time in seconds of the trimmed video.
    """
    # Defensive argument checking.
    assert isinstance(video_identifier, str), 'video_identifier must be string'
    assert isinstance(filename, str), 'filename must be string'
    assert len(video_identifier) == 11, 'video_identifier must have length 11'

    status, msg_or_file = download_video(video_identifier, tmp_dir)
    if not status:
        return status, msg_or_file
    else:
        tmp_filename = msg_or_file

    status, msg = trim_video(tmp_filename, filename, start_time, end_time)
    return status, msg


def download_clip_wrapper(row, dirname, trim_format, tmp_dir):
    """Wrapper for parallel processing purposes."""
    filename = construct_video_filename(row, dirname, trim_format)
    clip_id = os.path.basename(filename).split('.mp4')[0]
    if os.path.exists(filename):
        status = tuple([clip_id, True, 'Exists'])
        return status

    downloaded, log = get_video(
        row['youtube_id'], filename, row['time_start'], row['time_end'],
        tmp_dir=tmp_dir)
    status = tuple([clip_id, downloaded, log])
    return status


def parse_csv(input_csv, ignore_is_cc=False):
    """Returns a parsed DataFrame.

    Args:
        input_csv (string) : path to CSV file containing the following columns
            'youtube-id,start-time,end-time,label'

    Returns:
        df (DataFrame)
    """
    df = pd.read_csv(input_csv)
    return df


def main(input_csv, output_dir, trim_format='{}.mp4', n_jobs=24, backend=None,
         verbose=0, tmp_dir='/tmp/kinetics'):
    trim_format = '{}.mp4'
    # Reading and parsing Kinetics.
    dataset = parse_csv(input_csv)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Download all clips.
    status_lst = Parallel(
        n_jobs=n_jobs, backend=backend, verbose=verbose)(
        delayed(download_clip_wrapper)(
            row, output_dir, trim_format, tmp_dir)
        for i, row in dataset.iterrows())

    # Clean tmp dir.
    shutil.rmtree(tmp_dir)

    # Save download report.
    with open('download_report.json', 'w') as fobj:
        fobj.write(json.dumps(status_lst, indent=2))


if __name__ == '__main__':
    description = 'Helper script for downloading and trimming Youtube videos.'
    p = ArgumentParser(description=description,
                       formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument('input_csv', type=str,
                   help=('CSV file containing the following format: '
                         'video_id,start_time,end_time,label'))
    p.add_argument('output_dir', type=str,
                   help='Output directory where videos will be saved.')
    p.add_argument('-f', '--trim-format', type=str, default='{}.mp4',
                   help=('DISABLED: pyformat string for the basename of '
                         'trimmed videos: '
                         '{}_{start_time:02d}_{end_time:02d}.mp4'))
    p.add_argument('-n', '--n-jobs', type=int, default=64)
    p.add_argument('-b', '--backend', type=str, default='threading')
    p.add_argument('-v', '--verbose', type=int, default=0)
    p.add_argument('-t', '--tmp-dir', type=str, default='/tmp/kinetics')
    main(**vars(p.parse_args()))
