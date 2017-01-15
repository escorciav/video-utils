#!/bin/bash
#
#SBATCH -n 2
#SBATCH --mem=6G
#SBATCH --time=02:00:00
#SBATCH --job-name=dump-frames
#SBATCH --workdir=/home/escorcv/projects/video-utils
#SBATCH --output=/data/log/%J-%a.out
#SBATCH --array=1-3

# --- Input arguments ---
# CSV-file with video path
video_list="/data/activitynet/v1_2-videos.csv"
# CSV-file with location for frames (equal number of lines of video_list -> 1 to 1 matching :smile:)
output_list="/data/activitynet/v1_2-frames.csv"
# Downsample output
downsample="-vf scale=171x128 "
# Output format
output_format="%06d.png"
# ------

# Let's do it!

# SLURM_ARRAY_TASK_ID receives second argument
# It makes sbatch-script compatible without slurm ;)
if [ -z ${SLURM_ARRAY_TASK_ID+x} ]; then
  SLURM_ARRAY_TASK_ID=$1
fi

hostname
echo "----- Executing before job -----"
source activate.sh  # Setup your execution environment. Feel free to comment it.
echo "------ Executing main job ------"
# Grab i-th line from video_list and output_dir
video_filename="$(sed -n ${SLURM_ARRAY_TASK_ID}p $video_list)"
output_dir="$(sed -n ${SLURM_ARRAY_TASK_ID}p $output_list)"

# Create folder for frames if it does not exist.
mkdir -p $output_dir

# Dump frames
ffmpeg -v error -i $video_filename -qscale:v 2 ${downsample}-f image2 $output_dir/$output_format

# Makes debugging == find token
if [ $? -eq 0 ]; then
  echo 'Successful execution'
else
  echo 'Unsuccessful execution'
fi
