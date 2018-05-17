import glob, time, datetime

while True:
    n = len(glob.glob('/home/escorciav/mnt/marla-ssdscratch/datasets/mantis/dove/relevant/*.mp4'))
    now = datetime.datetime.now()
    print '{} [{}/8274]'.format(now.isoformat(), n)
    time.sleep(900)
