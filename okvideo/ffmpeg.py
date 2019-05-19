import ast
import glob
import logging
import os
import subprocess
from subprocess import check_output


def dump_frames(filename, output_format='%06d.jpg', filters='-qscale:v 1'):
    """Dump frames of a video-file

   Args:
        filename (str): fullpath of video-file
        basename_format (str, optional): string format used to save video
            frames.
        filters (str, optional): additional filters for ffmpeg e.g.
            "-vf scale=320x240".

    Returns:
        success : bool

    """
    cmd = 'ffmpeg -v error -i {} {} {}'.format(
        filename, filters, output_format)

    try:
        check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True,
                     shell=True)
    except subprocess.CalledProcessError as err:
        logging.debug('Imposible to dump video', filename)
        logging.debug('Traceback:\n', err.output)
        return False
    return True


def get_duration(filename):
    """Return duration on seconds of a video

    Args:
        filename (str): fullpath of video-file

    Returns:
        frame_rate (float or None): duration if seconds. If None, metadata is
            corrupted.

    """
    cmd = ('ffprobe -v 0 -of flat=s=_ -select_streams v:0 -show_entries '
           'stream=duration -of default=nokey=1:noprint_wrappers=1 ' +
           filename).split()
    pid = subprocess.run(cmd, universal_newlines=True,
                         stdout=subprocess.PIPE)
    if pid.returncode != 0:
        return None

    duration_exp = pid.stdout.rstrip()
    try:
        duration = float(duration_exp)
    except:
        duration = 0.
    return duration


def get_frame_rate(filename):
    """Return frame-rate of video

    Args:
        filename (str): Fullpath of video-file

    Returns:
        frame_rate (float or None): duration if seconds. If None, metadata is
            corrupted.

    """
    cmd = ('ffprobe -v 0 -of flat=s=_ -select_streams v:0 -show_entries '
           'stream=avg_frame_rate -of default=nokey=1:noprint_wrappers=1 ' +
           filename).split()
    pid = subprocess.run(cmd, stdout=subprocess.PIPE,
                         universal_newlines=True)
    if pid.returncode != 0:
        return None

    frame_rate_exp = pid.stdout.rstrip()
    try:
        frame_rate = float(frame_rate_exp)
    except:
        if frame_rate_exp == 'N/A':
            frame_rate = 0.
        else:
            numerator, denominator = map(float, frame_rate_exp.split('/'))
            if denominator == 0:
                frame_rate = 0
            else:
                frame_rate = numerator / denominator
    return frame_rate


def get_metadata(filename):
    """Return dict with all the metadata from the video

    Args:
        filename (str): Fullpath of video

    Returns:
        TODO

    """
    cmd = ('ffprobe -v error -v quiet -print_format json -show_format '
           '-show_streams ' + filename).split()
    output_expr = check_output(cmd, universal_newlines=True)
    metadata = ast.literal_eval(output_expr)
    return metadata


def get_num_frames(filename, ext='*.jpg'):
    """Count number of frames of a video

    Args:
        filename (str): fullpath of video file
        ext (str, optional): image extension

    Returns:
        counter (int or None): number of frames. If None, metadata is
            corrupted.

    Raises
        ValueError: unexpected filename

    """
    if os.path.isdir(filename):
        return len(glob.glob(os.path.join(filename, ext)))
    elif os.path.isfile(filename):
        cmd = ('ffprobe -v 0 -count_frames -select_streams v:0 '
               '-show_entries stream=nb_read_frames -of '
               'default=nokey=1:noprint_wrappers=1 ' + filename).split()
        pid = subprocess.run(cmd, stdout=subprocess.PIPE,
                             universal_newlines=True)
        if pid.returncode != 0:
            return None
        nframes_expr = pid.stdout
        nframes = int(nframes_expr.rstrip())
        return nframes
    else:
        raise ValueError('Unexpect filename: {}'.format(filename))


def get_resolution(filename):
    """Return resolution of video in terms of width and height

    Args:
        filename (str): Fullpath of video

    Returns:
        resolution (tuple or None): (width, height). If None, metadata is
            corrupted.

    """
    cmd = ('ffprobe -v 0 -of flat=s=_ -select_streams v:0 -show_entries '
           'stream=height,width ' + filename).split()
    pid = subprocess.run(cmd, stdout=subprocess.PIPE,
                         universal_newlines=True)
    if pid.returncode != 0:
        return None

    resolution_exp = pid.stdout
    width = int(resolution_exp.split('width=')[1].split('\n')[0])
    height = int(resolution_exp.split('height=')[1].split('\n')[0])
    return (width, height)
