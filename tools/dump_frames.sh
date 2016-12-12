#!/bin/bash
#
#SBATCH -n 2
#SBATCH --mem=6G
#SBATCH --time=02:00:00
#SBATCH --job-name=dump-frames
#SBATCH --workdir=/home/escorcv/projects/video-utils
#SBATCH --output=/home/escorcv/projects/video-utils/log/%J-%a.out
#SBATCH --array=1-3
video_list="activitynet_v1-2.csv"
output_list="activitynet_v1-2-outputs.csv"
downsample="-vf scale=171x128 "
output_format="%06d.png"

# SLURM_ARRAY_TASK_ID receives second argument
# It makes sbatch-script compatible without slurm ;)
if [ -z ${SLURM_ARRAY_TASK_ID+x} ]; then
  SLURM_ARRAY_TASK_ID=$1
fi

hostname
echo "----- Executing before job -----"
module load apps/conda;
source activate video-utils
echo "------ Executing main job ------"
# Grab i-th line from video_list
video_filename="$(sed -n ${SLURM_ARRAY_TASK_ID}p $video_list)"
output_dir="$(sed -n ${SLURM_ARRAY_TASK_ID}p $output_list)"
# Dump frames
mkdir -p $output_dir
ffmpeg -v error -i $video_filename -qscale:v 2 ${downsample}-f image2 $output_dir/$output_format
