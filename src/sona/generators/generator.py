"""
Module containing sample generator base class
"""
import numpy

from sona.params import BUFFERSIZE, BITRATE

class SampleGenerator(object):

    def __init__(self,
                 chunk_size=BUFFERSIZE,
                 amplitude=1.0):
        """
        Base class for sound generators.

        Args:
            chunk_size (int): the size of the chunk returned by next(). It has to be an even
                number.
            amplitude (float): the amplitude to which the samples are to be renormalized.
        """
        self._amplitude = amplitude
        if chunk_size % 2 == 0:
            self._chunk_size = chunk_size
        else:
            raise ValueError("chunk_size has to be even.")
        self._chunk = numpy.zeros(self._chunk_size, dtype=numpy.float32)

    def _reset(self):
        self._chunk = numpy.zeros(BUFFERSIZE, dtype=numpy.float32)

    def __iter__(self):
        return self

    def __len__(self):
        return 1

    @staticmethod
    def normalize(chunk):
        return chunk / max(chunk)

    def next(self):
        raise NotImplementedError("next() is a virtual method")
