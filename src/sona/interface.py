"""
pyAudio-sona interface and command line user interface.
"""
import argparse
import contextlib
import numpy
import os
import pyaudio
import sys
import threading
import time

from .generators.noise import ColoredNoise
from .generators.noise import PulseGenerator
from .params import BUFFERSIZE, BITRATE

@contextlib.contextmanager
def ignore_stderr():
    """
    A context manager to ignore stderr. We use it to avoid PyAudio
    pulluting the console output.
    Credits to:
    https://stackoverflow.com/questions/36956083/how-can-the-terminal-output-of-executables-run-by-python-functions-be-silenced-i/36966379#36966379
    """
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

class Player():
    """
    A threaded player class.
    """
    def __init__(self):
        """
        The player constructor.
        """
        self._stop = False

    def __call__(self, generator):
        """
        The player call function.

        Args:
            generator (SampleGenerator): the generator to be played.
        """
        lock = threading.Lock()
        self.thread = threading.Thread(target=self._play, args=(generator, lock))
        with ignore_stderr():
            self.thread.start()

    def _play(self, generator, lock):
        """
        The meaty play function.

        Args:
           generator (SampleGenerator): the generator to be played.
           lock (threading.Lock): a thread lock.
        """
        with lock:
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pyaudio.paFloat32,
                                   channels=1,
                                   rate=BITRATE,
                                   output=True)

            for data in generator:
                if not self._stop:
                    stream.write(data.tostring())
                else:
                    break
            # Close the stream and terminate pyAudio.
            stream.stop_stream()
            stream.close()
            pa.terminate()
            print('Audio terminated correctly')
            # Allow re-play.
            self._stop = False

    def stop(self):
        """
        Stop the playback.
        """
        self._stop = True


def play(generator):
    """
    Play indefinitely the given generator.

    Args:
        generator (derived class of ``SampleGenerator``): the generator to be
            played.
    """
    def callback(in_data, frame_count, time_info, status):
        data = next(generator)
        return (data, pyaudio.paContinue)

    # open stream using callback (3)
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paFloat32,
                     channels=1,
                     rate=BITRATE,
                     frames_per_buffer=BUFFERSIZE,
                     output=True,
                     stream_callback=callback)

    try:
        stream.start_stream()

        # wait for stream to finish (5)
        while stream.is_active():
            time.sleep(1.0)
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        print('Audio terminated correctly')


def parse_command_line():
    """
    Get the input parser.

    Return:
        parser (ArgumentParser): the input parser.
    """
    parser = argparse.ArgumentParser()
    helpstring = """
        The generator to be used. Up to now sona supports colored_noise and
        pulse_noise
        """
    parser.add_argument("generator",
                        type=str,
                        help=helpstring)
    helpstring = """
        The exponent to be used in the colored noise. Higher values correspond to a lower tone.
        Default value 2.0
        """
    parser.add_argument("--exponent",
                        type=float,
                        default=2.0,
                        help=helpstring)
    helpstring = """
        The number of samples to be zeroed in a simple high pass filter. A number betwen 128 and
        1024 is suggested. Default value 128.
        """
    parser.add_argument("--highpass",
                        type=int,
                        default=128,
                        help=helpstring)
    helpstring = """
        The distance between pulses for a pulsed noise in ms.
        """
    parser.add_argument("--distance",
                        type=float,
                        default=50.0,
                        help=helpstring)
    helpstring = """
        The randomness in the distance between pulses for a pulsed noise (standard deviation in ms).
        """
    parser.add_argument("--randomness",
                        type=float,
                        default=20.0,
                        help=helpstring)
    args = parser.parse_args()
    return parser

def start(parser):
    """
    Start playing the generator using the option specified in the parses.

    Args:
        parser (ArgumentParser): the input parser from argparse.
    """
    args = parser.parse_args()
    if args.generator == 'colored_noise':
        generator = ColoredNoise(args.exponent, args.highpass)
    elif args.generator == 'pulse_noise':
        generator = PulseGenerator(
            distance=args.distance,
            randomness=args.randomness)
    else:
        raise ValueError("unknown generator")

    play(generator)
