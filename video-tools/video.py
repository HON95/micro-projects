#!/usr/bin/env python3

import argparse
import imageio
import os
from pathlib import Path
import re
import sys
import time


VERSION = "1.0.0-dev"
OUTPUT_QUALITY = 10


_quiet = False
_input_files = None
_output_file = None
_overwrite = False
_framerate = None
_status = None
_preview = None


def main():
    """
    Main.
    """
    if not parse_arguments():
        sys.exit(1)
    iprint("Version:", VERSION)
    iprint()
    if not check_files():
        sys.exit(1)
    process()


def parse_arguments():
    """
    Parse arguments.
    """
    global _quiet, _input_files, _output_file, _overwrite, _framerate, _status, _preview

    parser = argparse.ArgumentParser(description="Concatenate a bunch of video files. Optionally modify some properties.")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="Hide informational output.")
    parser.add_argument(metavar="input", nargs="+", dest="inputs", help="One or more video files to use as input.")
    parser.add_argument("-o", "--output", metavar="output", required=True, dest="output", help="Video output file.")
    parser.add_argument("-w", "--overwrite", action="store_true", dest="overwrite", help="Overwrite output file if it exists.")
    parser.add_argument("-f", "--framerate", metavar="FPS", type=float, dest="framerate", help="New frame rate. If omitted, the frame rate of the first input is used.")
    parser.add_argument("-s", "--status", metavar="N", type=int, dest="status", help="If positive, show status output every N seconds.")
    parser.add_argument("-p", "--preview", metavar="N", type=int, dest="preview", help="If positive, preview every N frames.")

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as err:
        print(err)
        return False

    _quiet = args.quiet
    _input_files = args.inputs
    _output_file = args.output
    _overwrite = args.overwrite
    _framerate = args.framerate
    _status = args.status
    _preview = args.preview

    assert _input_files is not None
    assert len(_input_files) > 0
    assert _output_file is not None
    if _framerate:
        assert _framerate > 0
    if _preview:
        assert _preview > 0

    return True


def check_files():
    """
    Make sure the provided input files exist and that the dir of the output file is writable.
    """
    # Check input files
    iprint("Input files:")
    for input_file_path in _input_files:
        input_file = Path(input_file_path)
        iprint("-", input_file)
        if not input_file.is_file():
            eprint("Input file does not exist: {}".format(input_file))
            return False
        if not os.access(input_file, os.R_OK):
            eprint("Input file is not readable: {}".format(input_file))
            return False
    iprint()

    # Check output file dir
    output_file = Path(_output_file)
    iprint("Output file:", output_file)
    if output_file.exists():
        if not _overwrite:
            eprint("Output file already exists: {}".format(output_file))
            return False
        elif not output_file.is_file():
            eprint("Output file exists but is not a file: {}".format(output_file))
            return False
    if not os.access(output_file.parent, os.W_OK):
        eprint("Output file is not in writable directory: {}".format(output_file.parent))
        return False
    iprint()

    return True


def process():
    size = None
    framerate = _framerate
    pixelformat = None
    codec = None

    reader = imageio.get_reader(_input_files[0], mode="I")
    metadata = reader.get_meta_data()
    size = metadata["size"]
    if not framerate:
        framerate = metadata["fps"]
    pixelformat = re.search(r"^[0-9A-Za-z]+", metadata["pix_fmt"])[0]
    codec = metadata["codec"]
    reader.close()

    iprint("Size: {}x{}".format(*size))
    iprint("Framerate: {} FPS".format(framerate))
    iprint("Pixel format: {}".format(pixelformat))
    iprint("Codec: {}".format(codec))
    iprint("Selected quality: {} (10 is max)".format(OUTPUT_QUALITY))
    iprint()

    if _preview:
        import matplotlib.pyplot as pyplot
        preview_fig = pyplot.figure()
        pyplot.axis("off")

    total_image_count = 0
    start_time = time.perf_counter()
    last_status_time = start_time

    writer = imageio.get_writer(_output_file, mode="I", fps=framerate, quality=OUTPUT_QUALITY, codec=codec, pixelformat=pixelformat)

    for input_file in _input_files:
        iprint("Reading:", input_file)
        reader = imageio.get_reader(input_file, mode="I")
        for frame in reader:
            writer.append_data(frame)
            # Status
            current_time = time.perf_counter()
            if _status and (current_time - last_status_time) > _status:
                iprint("Status: duration={:.0f}s images_processed={} video_duration_processed={:.0f}s".format((current_time - start_time), total_image_count, (total_image_count / framerate)))
                last_status_time = current_time
            # Preview
            if _preview and total_image_count % _preview == 0:
                pyplot.imshow(frame)
                preview_fig.suptitle('Frame #{}\nTime {:.1f}s'.format(total_image_count, (total_image_count / framerate)))
                pyplot.pause(0.001)
            total_image_count += 1
        reader.close()
    iprint()

    writer.close()

    end_time = time.perf_counter()
    total_time = (end_time - start_time)

    iprint("Done.")
    iprint("Total duration: {:.1f}s".format(total_time))
    iprint("Total image count:", total_image_count)
    iprint("Frame processing rate: {:.1f} FPS".format(total_image_count / total_time))


def iprint(*args, **kwargs):
    """
    Print informational message. Respects the quiet flag.
    """
    if not _quiet:
        print(*args, **kwargs)


def eprint(*args, **kwargs):
    """
    Print message to STDERR.
    """
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    main()
