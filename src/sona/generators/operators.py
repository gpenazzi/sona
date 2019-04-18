"""
Module implementing generators to do math with generators.
"""
import numpy

from sona.generators.generator import SampleGenerator


class Product(SampleGenerator):
    """ Element-wise product of two generators chunks. """
    def __init__(self, first, second, amplitude=1.0):
        """
        Initialize the product generator with the two generators to use as factors.
        The product is calculated as first.chunk * second.chunk

        Args:
            first (a SampleGenerator): generator providing first chunk.
            second (a SampleGenerator): generator providing second chunk.

        Attributes:
            first (a SampleGenerator): the generator providing first chunk.
            second (a SampleGenerator): the generator providing second chunk.
        """
        super(Product, self).__init__(amplitude=amplitude)
        self.first = first
        self.second = second

    def __next__(self):
        """
        Generate the product chunks.
        """
        first_chunk = next(self.first)
        second_chunk = next(self.second)
        self._chunk = numpy.multiply(first_chunk, second_chunk)
        return self._chunk
