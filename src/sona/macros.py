"""
A module with examples which combine more generators together.
"""
from sona import *
import scipy.signal as signal


def coloredGatedNoise(
        colored_noise_exponent=2.0,
        colored_noise_high_pass=128,
        pulse_noise_distance=50.0,
        pulse_noise_randomness=20.0,
        pulse_noise_signal=signal.gaussian(361, 18)):
    """
    Gate a colored noise with a pulsed gaussian.
    """
    colored_noise = ColoredNoise(
        exponent=colored_noise_exponent,
        high_pass=colored_noise_high_pass)
    pulsed_noise = PulseGenerator(
        distance=pulse_noise_distance,
        randomness=pulse_noise_randomness,
        pulse_signal=pulse_noise_signal)
    product = Product(colored_noise, pulsed_noise)
    return product

ColoredGatedNoise = coloredGatedNoise()