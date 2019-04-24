"""
pyAudio-sona interface and command line user interface.
"""
import argparse
import contextlib
import os
import pyaudio
import sys
import threading
import time
import scipy.signal as signal

from .generators.noise import ColoredNoise
from .generators.noise import PulseGenerator
from .generators.noise import SineOscillator
from .params import BUFFERSIZE, BITRATE
from .macros import coloredGatedNoise
from .macros import gatedSine

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
    A non-blocking player class.

    Usage:
        >>> player = Player(generator)
        # This starts the generator
        >>> player.start()
        # This stops the generator
        >>> player.stop()
    """
    def __init__(self, generator):
        """
        The player constructor.
        """
        self._stop = False
        self._generator = generator

    def start(self):
        """
        Play the generator.

        Args:
            generator (SampleGenerator): the generator to be played.
        """
        def callback(in_data, frame_count, time_info, status):
            data = next(self._generator)
            return (data, pyaudio.paContinue)

        # open stream using callback (3)
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=BITRATE,
            frames_per_buffer=BUFFERSIZE,
            output=True,
            stream_callback=callback)
        self._stream.start_stream()

    def stop(self):
        """
        Stop the playback.
        """
        # Close the stream and terminate pyAudio.
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pa:
            self._pa.terminate()
        print('Audio terminated correctly')


def play(generator):
    """
    Play indefinitely the given generator.

    Args:
        generator (derived class of ``SampleGenerator``): the generator to be
            played.
    """
    player = Player(generator)
    try:
        player.start()
        # Event loop to keep playing.
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        player.stop()


def parse_command_line():
    """
    Get the input parser.

    Return:
        parser (ArgumentParser): the input parser.
    """
    parser = argparse.ArgumentParser()
    helpstring = """
        The generator to be used. Up to now sona supports:
          - colored_noise
          - pulse_noise
          - gated_pulse
          - gated_sine
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

    helpstring = """
        The gating width in ms.
        """
    parser.add_argument("--gate-width",
                        type=float,
                        default=10.0,
                        help=helpstring)

    helpstring = """
        The oscillator frequency.
        """
    parser.add_argument("--frequency",
                        type=float,
                        default=440.0,
                        help=helpstring)

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
    elif args.generator == 'gated_noise':
        int_width = int(BITRATE / 1000 * args.gate_width)
        generator = coloredGatedNoise(
            colored_noise_exponent=args.exponent,
            colored_noise_high_pass=args.highpass,
            gate_distance=args.distance,
            gate_randomness=args.randomness,
            gate_signal=signal.gaussian(int_width * 16, int_width))
    elif args.generator == 'sine':
        generator = SineOscillator(
            frequency=args.frequency)
    elif args.generator == 'gated_sine':
        int_width = int(BITRATE * args.gate_width / 1000)
        generator = gatedSine(
            frequency=args.frequency,
            gate_distance=args.distance,
            gate_randomness=args.randomness,
            gate_signal=signal.gaussian(int_width * 20, int_width))
    else:
        raise ValueError("unknown generator")

    play(generator)
