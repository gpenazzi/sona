"""
A module with examples which combine more generators together.
"""
from sona import *
import scipy.signal as signal


def coloredGatedNoise(
        colored_noise_exponent=3.0,
        colored_noise_high_pass=18,
        pulse_noise_distance=200.0,
        pulse_noise_randomness=10.0,
        pulse_noise_signal=signal.gaussian(3610, 180)):
    """
    Gate a colored noise with a pulsed gaussian.
    """
    colored_noise = ColoredNoise(
        exponent=colored_noise_exponent,
        high_pass_zeroed_samples=colored_noise_high_pass)
    pulsed_noise = PulseGenerator(
        distance=pulse_noise_distance,
        randomness=pulse_noise_randomness,
        pulse_signal=pulse_noise_signal)
    product = Product(colored_noise, pulsed_noise)
    return product
