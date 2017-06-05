"""
pyAudio-sona interface and command line user interface.
"""
import pyaudio
import argparse

from sona.generators.noise import coloredNoise
from sona.params import BUFFERSIZE, BITRATE

def play(generator):
    """
    Play indefenitely the given generator.

    Args:
        generator (derived class of ``SampleGenerator``): the generator to be played.
    """
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paFloat32,
                     channels=1,
                     rate=BITRATE,
                     output=True)

    try:
        for data in generator:
            stream.write(data.tostring())
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        print('Audio terminated correctly')

def parseCommandLine():
    """
    Get the input parser.

    Return:
        parser (ArgumentParser): the input parser.
    """
    parser = argparse.ArgumentParser()
    helpstring = """
        The generator to be used. Up to now sona supports:
            * colored_noise
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
        generator = coloredNoise(args.exponent, args.highpass)
    else:
        raise ValueError("unknown generator")

    play(generator)
