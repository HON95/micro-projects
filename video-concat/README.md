# Video Concatenator

Concatenate multiple video files into one and optionally modify the framerate. It handles the video frame by frame, so no interpolation or other weird stuff happens.

Supports only MP4 for now, but that's easily changeable.

## Setup

1. `apt install ffmpeg`
1. `pip3 install -r requirements.txt`

## Usage

- `./video-concat.py <input> [input ...] [-h] [-q] -o <output> [-w] [-f FPS] [-x N] [-s N] [-p N]`
- `-h`/`--help`: Show help.
- `-q`/`--quiet`: Hide informational output.
- `-o`/`--overwrite`: Overwrite output file if it exists.
- `-f N`/`--framerate=N`: Change the frame rate. This may speed up or slow down the original video files.
- `-x N`/`--speedup=N`: Speed up the video by factor N by keeping only every N frames and discarding the rest. This preserved the frame rate.
- `-s N`/`--status=N`: Print status message every N seconds.
- `-p N`/`--preview=N`: Preview output frame every N seconds.
