from subprocess import check_output
import glob
import os
import subprocess


def dump_frames(filename, output_folder, output_format='%06d.png'):
    """Dump frames of a video-file into a folder

    Parameters
    ----------
    filename : str
        Fullpath of video-file
    output_folder : str
        Fullpath of folder to place frames
    basename_format: str, optional
        String format used to save video frames.

    Outputs
    -------
    success : bool

    Raises
    ------
    IOError
        Unexistent video file

    """
    if not os.path.isfile(filename):
        raise IOError('Unexistent video {}'.format(filename))

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    output_format = os.path.join(output_folder, output_format)
    cmd = ('ffmpeg -v error -i {} -qscale:v 2 -f image2 {}'.format(
        filename, output_format)).split()

    try:
        out = check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print('Imposible to dump video', filename)
        print('Traceback:\n', out)
        return False
    return True


def get_duration(filename):
    """Return duration on seconds of a video

    Parameters
    ----------
    filename : str
        Fullpath of video-file

    Outputs
    -------
    frame_rate : float

    Raises
    ------
    IOError
        Unexistent video file

    """
    if not os.path.isfile(filename):
        raise IOError('Unexistent video {}'.format(filename))

    cmd = ('ffprobe -v 0 -of flat=s=_ -select_streams v:0 -show_entries '
           'stream=duration -of default=nokey=1:noprint_wrappers=1 ' +
           filename).split()
    duration_exp = check_output(cmd, universal_newlines=True)
    duration_exp = duration_exp.rstrip()
    try:
        duration = float(duration_exp)
    except:
        duration = 0.
    return duration


def get_frame_rate(filename):
    """Return frame-rate of video

    Parameters
    ----------
    filename : str
        Fullpath of video-file

    Outputs
    -------
    frame_rate : float

    Raises
    ------
    IOError
        Unexistent video file

    """
    if not os.path.isfile(filename):
        raise IOError('Unexistent video {}'.format(filename))

    cmd = ('ffprobe -v 0 -of flat=s=_ -select_streams v:0 -show_entries '
           'stream=avg_frame_rate -of default=nokey=1:noprint_wrappers=1 ' +
           filename).split()
    frame_rate_exp = check_output(cmd, universal_newlines=True)
    frame_rate_exp = frame_rate_exp.rstrip()

    try:
        frame_rate = float(frame_rate_exp)
    except:
        if frame_rate_exp == 'N/A':
            frame_rate = 0.
        else:
            numerator, denominator = frame_rate_exp.split('/')
            frame_rate = float(numerator) / float(denominator)

    return frame_rate


def get_num_frames(filename, ext='*.jpg'):
    """Count number of frames of a video

    Parameters
    ----------
    filename : str
        fullpath of video file
    ext : str, optional
        image extension

    Outputs
    -------
    counter : int
        number of frames

    Raises
    ------
    IOError
        Unexistent video file

    """
    if os.path.isdir(filename):
        return len(glob.glob(os.path.join(filename, ext)))
    elif not os.path.isfile(filename):
        raise IOError('Unexistent video {}'.format(filename))

    cmd = ('ffprobe -v error -count_frames -select_streams v:0 -show_entries '
           'stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 ' +
           filename)
    nframes_expr = check_output(cmd, universal_newlines=True, shell=True)
    nframes = int(nframes_expr.rstrip())
    return nframes
