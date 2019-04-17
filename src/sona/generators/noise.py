"""
Colored Noise generators module.
"""
import numpy
from scipy.signal import gaussian
from sona.generators.generator import SampleGenerator

import time


class NoiseGenerator(SampleGenerator):
    """A noise generator."""

    def __init__(self,
                 spectrum_filter=lambda x, f: x,
                 high_pass=128,
                 amplitude=1.0):
        """
        A generic noise generator. The class will create a random spectrum and process it with
        the function provided in ``spectrum_filter``.

        Args:
            spectrum_filter (function): the function y(x, f) used to process the noise. X represent
                a random spectrum and S is the frequency. For example, a 1/f noise is obtained by
                passing spectrum_filter=lambda x, f: x/f
            high_pass (integer): set the first high_pass_zeroed_samples spectrum
                components to zero. This implements a rudimental high pass filter and avoids
                divergence of the samples.
            amplitude (float): signal amplitude.
        """
        super(NoiseGenerator, self).__init__(amplitude=amplitude)
        self._spectrum_filter = spectrum_filter
        self.high_pass = high_pass

    def __next__(self):
        """
        Generate the signal chunks.
        """
        spectrum = numpy.random.randn((self._chunk_size + 2) // 2) + \
            1j * numpy.random.randn((self._chunk_size + 2) // 2)
        # A punk high-pass Filter
        spectrum[:self.high_pass] = 0
        frequency = numpy.arange(len(spectrum), dtype=numpy.float32)
        # Avoid 0 value, can mess up some operations.
        frequency[0] += 0.01

        self._chunk = numpy.fft.irfft(self._spectrum_filter(spectrum, frequency))
        self.normalize()
        return self._chunk


class ColoredNoise(NoiseGenerator):
    """A colored noise with a spectrum 1/f**e."""
    def __init__(self,
                 exponent,
                 high_pass,):
        """
        Build a colored noise generator with a spectrum 1/f**e

        Args:
            exponent (float): the exponent of the frequency.
            high_pass (int): the number of samples to be zeroed in the high pass
                filter.

        Returns:
            An instance of ``NoiseGenerator``.
        """
        self._exponent = exponent
        super(ColoredNoise, self).__init__(
            spectrum_filter=lambda x, f: x / f**self._exponent,
            high_pass=high_pass,)

    @property
    def exponent(self):
        return self._exponent

    @exponent.setter
    def exponent(self, value):
        self._exponent = value
        self._spectrum_filter = lambda x, f: x / f**self._exponent


class PulseGenerator(SampleGenerator):
    """ A pulsed audio noise generator """
    def __init__(self,
                 distance=100.0,
                 randomness=5.0,
                 pulse_signal=gaussian(361, 18),
                 amplitude=1.0):
        """
        A pulsed noise generator. It creates a train of delta function spaced accordingly to the
        input parameters.

        Args:
            distance (float): the average distance in ms between different pulses.
            randomness (float): the width of the uniform distribution to modify randomly
                the distance between pulses. A uniform distribution is used, with
                b - a = sqrt(12) * standard_deviation
            pulse_signal (array): the shape of the pulse.
            amplitude (float): signal amplitude.
        """
        super(PulseGenerator, self).__init__(amplitude=amplitude)
        self._distance = distance
        self._average_integer_distance = int((self._distance * 1e-3) * self._bitrate)

        self._randomness = randomness
        self._random_range = int(
            (self._randomness * numpy.sqrt(12) * 1e-3) * self._bitrate)

        # An absolute frame time
        self._random_generator_state = numpy.random.RandomState()
        self.pulse_signal = pulse_signal
        self._pulse_signal_buffer = self.pulse_signal[:]


    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value
        self._average_integer_distance = int(
            (self._distance * 1e-3) * self._bitrate)

    @property
    def randomness(self):
        return self._randomness

    @randomness.setter
    def randomness(self, value):
        self._randomness = value
        self._random_range = int(
            (self._randomness * numpy.sqrt(12) * 1e-3) * self._bitrate)

    def _determineNextSampleDistance(self):
        """ Determine the integer distance to next sample. """
        if self._random_range > 0.0:
            random_component = self._random_generator_state.randint(
                0, self._random_range)
            self._random_generator_state.seed()
        else:
            random_component = 0
        return self._average_integer_distance + random_component

    def _getSignalBufferSamples(self, n):
        """
        Retrieve n samples from the signal buffer.
        If it depletes, regenerate it.
        """
        if n < self._pulse_signal_buffer.size:
            start = time.time()
            samples, self._pulse_signal_buffer = numpy.split(
                self._pulse_signal_buffer, [n])
            return samples
        else:
            start = time.time()
            # Take the leftover.
            leftover = self._pulse_signal_buffer[:]
            self._pulse_signal_buffer = numpy.zeros(0)

            # Regenerate the buffer.
            while self._pulse_signal_buffer.size < n:
                self._pulse_signal_buffer = numpy.concatenate(
                        [self._pulse_signal_buffer,
                         self.pulse_signal,
                         numpy.zeros(self._determineNextSampleDistance())])

            samples = numpy.concatenate(
                [leftover, self._pulse_signal_buffer[:n-leftover.size]])
            self._pulse_signal_buffer = self._pulse_signal_buffer[n-leftover.size:]
            return samples

    def __next__(self):
        """
        Generate the signal chunks.
        """
        self._reset()
        self._chunk = self._getSignalBufferSamples(self._chunk_size)
        if numpy.count_nonzero(self._chunk) > 0:
            self.normalize()
        return self._chunk
