module purge
module load conda

while true; do
  source activate video-utils
  if [ $? -eq 0 ]; then
    break;
  else
     sleep $[ ( $RANDOM % 10 ) + 1 ]s
  fi
done
