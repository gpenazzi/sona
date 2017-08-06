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
        """
        if first.chunkSize() != second.chunkSize():
            raise ValueError("Generator in product must have the same chunk size.")
        super(Product, self).__init__(chunk_size=first.chunkSize(), amplitude=amplitude)
        self._first = first
        self._second = second

    def next(self):
        """
        Generate the product chunks.
        """
        first_chunk = self._first.next()
        second_chunk = self._second.next()
        self._chunk = numpy.multiply(first_chunk, second_chunk)
        self.normalize()
        return self._chunk
