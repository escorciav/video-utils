Utilities to process videos from python, usually in batch mode.

# Setup

The main requirements of this project are Python==3.6, ffmpeg, numpy, pandas. To ensure reproducibility, we use conda.

1. [Install miniconda](https://conda.io/docs/user-guide/install/index.html).

    > Feel free to skip this step, if you already have anaconda or miniconda installed in your machine.

2. Creating the environment.

    `conda env create -n video-utils-tools -f environment_x64.yml`

That's all! You are ready to use the tools.

# Usage

1. Activate the environment

    `conda activate video-utils-tools`

2. Read the helper in the programs inside `tools` folder. For example:

    `python tools/batch_dump_frames.py -h`