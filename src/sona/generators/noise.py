"""
Colored Noise generators module.
"""
import numpy

from sona.params import BUFFERSIZE
from sona.generators.generator import SampleGenerator

class NoiseGenerator(SampleGenerator):

    def __init__(self,
                 spectrum_filter=lambda x, f: x,
                 high_pass_zeroed_samples=128,
                 chunk_size=BUFFERSIZE,
                 amplitude=1.0):
        """
        A generic noise generator. The class will create a random spectrum and process it with
        the function provided in ``spectrum_filter``.

        Args:
            spectrum_filter (function): the function y(x, f) used to process the noise. X represent
                a random spectrum and S is the frequency. For example, a 1/f noise is obtained by
                passing spectrum_filter=lambda x, f: x/f
            high_pass_zeroed_samples (integer): set the first high_pass_zeroed_samples spectrum
                components to zero. This implements a rudimental high pass filter and avoids
                divergence of the samples.
            chunk_size (even int): the size of the chunks returned by the iterator.
            amplitude (float): signal amplitude.
        """
        super(NoiseGenerator, self).__init__(chunk_size=chunk_size, amplitude=amplitude)
        self._spectrum_filter = spectrum_filter
        self._high_pass_zeroed_samples = high_pass_zeroed_samples

    def next(self):
        """
        Generate the signal chunks.
        """
        spectrum = numpy.random.randn(self._chunk_size / 2) + \
                   1j * numpy.random.randn(self._chunk_size / 2)
        # A punk high-pass Filter
        spectrum[:self._high_pass_zeroed_samples] = 0
        frequency = numpy.arange(len(spectrum), dtype=numpy.float32)
        # Avoid 0 value, can mess up some operations.
        frequency[0] += 0.01

        self._chunk = numpy.fft.irfft(self._spectrum_filter(spectrum, frequency))
        self._chunk = self.normalize(self._chunk).astype(numpy.float32)
        return self._chunk

def coloredNoise(exponent, high_pass_zeroed_samples):
    """
    Build a colored noise generator with a spectrum 1/f**e

    Args:
        exponent (float): the exponent of the frequency.
        high_pass_zeroed_samples (int): the number of samples to be zeroed in the high pass filter.

    Returns:
        An instance of ``NoiseGenerator``.
    """
    spectrum_filter = lambda x, f: x / f**exponent
    return NoiseGenerator(spectrum_filter=spectrum_filter,
                          high_pass_zeroed_samples=high_pass_zeroed_samples)
