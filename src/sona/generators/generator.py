"""
Module containing sample generator base class
"""
import numpy

from sona.params import BUFFERSIZE, BITRATE

class SampleGenerator(object):

    def __init__(self,
                 chunk_size=BUFFERSIZE,
                 bitrate=BITRATE,
                 amplitude=1.0):
        """
        Base class for sound generators.

        Args:
            chunk_size (int): the size of the chunk returned by next(). It has to be an even
                number.
            bitrate (int): the bit rate per second.
            amplitude (float): the amplitude to which the samples are to be renormalized.
        """
        self._amplitude = amplitude
        self._bitrate = bitrate
        if chunk_size % 2 == 0:
            self._chunk_size = chunk_size
        else:
            raise ValueError("chunk_size has to be even.")
        self._chunk = numpy.zeros(self._chunk_size, dtype=numpy.float32)

    def _reset(self):
        self._chunk[:] = 0.0

    def __iter__(self):
        return self

    def __len__(self):
        return 1

    def normalize(self):
        # Restore minimum to zero, if it is not.
        self._chunk = self._chunk - min(self._chunk)
        # Normalize to [0,1]
        self._chunk = (self._amplitude *
            (self._chunk / max(numpy.abs(self._chunk)))).astype(numpy.float32)

    def __next__(self):
        raise NotImplementedError("next() is a virtual method")

    def chunkSize(self):
        return self._chunk_size
