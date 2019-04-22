"""
Module containing sample generator base class
"""
import numpy

from sona.params import BUFFERSIZE, BITRATE

class SampleGenerator(object):

    def __init__(self,
                 amplitude=1.0):
        """
        Base class for sound generators.

        Args:
            amplitude (float): the amplitude to which the samples are to be renormalized.
        """
        self._amplitude = amplitude
        self._bitrate = BITRATE
        if BUFFERSIZE % 2 == 0:
            self._chunk_size = BUFFERSIZE
        else:
            raise ValueError("BUFFERSIZE has to be even.")
        self._chunk = numpy.zeros(self._chunk_size, dtype=numpy.float32)

    def _reset(self):
        self._chunk[:] = 0.0

    def __iter__(self):
        return self

    def __len__(self):
        return 1

    def normalize(self, chunk):
        # Restore minimum to zero, if it is not.
        chunk = chunk - min(chunk)
        # Normalize to [0,1]
        return (self._amplitude *
            (chunk / max(numpy.abs(chunk))))

    def __next__(self):
        raise NotImplementedError("next() is a virtual method")

    def chunkSize(self):
        return self._chunk_size
