#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from json import loads
from multiprocessing import Pool
from subprocess import Popen, check_output, DEVNULL, PIPE


def arg_builder(args, kwargs, defaults={}):
    """Build arguments from `args` and `kwargs` in a shell-lexical manner."""
    for key, val in defaults.items():
        kwargs[key] = kwargs.get(key, val)

    args = list(args)

    for arg, val in kwargs.items():
        if isinstance(val, bool):
            if val:
                args.append("-" + arg)
        else:
            args.extend(("-" + arg, val))

    return args


def run_ffmpeg(input_file, output_file, async=True, *args, **kwargs):
    """Use FFMPEG to convert a media file."""
    with Popen(("ffmpeg", *arg_builder(args, kwargs, defaults={"y": True}),
                "-progress", "-", "-i", input_file, output_file),
               shell=True, stderr=DEVNULL, stdout=PIPE) as ffmpeg:
        if async:
            progress = {}

            while True:
                line = ffmpeg.stdout.readline().decode().split("=")

                if ffmpeg.poll() is not None:
                    break

                key = line[0].strip()

                if key == "progress":
                    yield progress

                if len(line) == 2:
                    progress[key] = line[1].strip()

        else:
            return ffmpeg.wait()


def run_ffprobe(file_path, *args, **kwargs):
    """Use FFPROBE to get information about a media file."""
    return loads(check_output(("ffprobe", *arg_builder(args, kwargs, defaults={"show_format": True}),
                               "-of", "json", file_path), shell=True, stderr=DEVNULL))


def batch_ffprobe(file_paths, workers=4):
    with Pool(workers) as pool:
        return pool.map(run_ffprobe, file_paths)


def batch_ffprobe_async(file_paths, workers=4, callback=None):
    with Pool(workers) as pool:
        pool.map_async(run_ffprobe, file_paths, callback=callback)
        return pool


class BatchMediaConverter:
    def __init__(self, input_dir, output_dir, input_fmt="flac", output_fmt="mp3", workers=4):
        self.input_dir = input_dir
        self.output_dir = output_dir

        self.input_fmt = input_fmt
        self.output_fmt = output_fmt

        self.workers = workers

        self.files_callback = self._callback
        self.data_callback = self._callback
        self.speed_callback = self._callback

        self.meta_callback = None

        self.batch_meta = []
        self.active_pool = None

    @staticmethod
    def _callback(value):
        pass

    def start(self):
        pass

    def cancel(self):
        pass
