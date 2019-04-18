"""
A module with examples which combine more generators together.
"""
from .generators.noise import ColoredNoise, PulseGenerator, SineOscillator
from .generators.operators import Product
import scipy.signal as signal


def coloredGatedNoise(
        colored_noise_exponent=2.0,
        colored_noise_high_pass=128,
        gate_distance=50.0,
        gate_randomness=0.0,
        gate_signal=signal.gaussian(3610, 180)):
    """
    Gate a colored noise with a pulsed gaussian.
    """
    colored_noise = ColoredNoise(
        exponent=colored_noise_exponent,
        high_pass=colored_noise_high_pass)
    pulsed_noise = PulseGenerator(
        distance=gate_distance,
        randomness=gate_randomness,
        pulse_signal=gate_signal)
    product = Product(colored_noise, pulsed_noise)
    return product


def gatedSine(
        frequency=440.0,
        gate_distance=50.0,
        gate_randomness=0.0,
        gate_signal=signal.gaussian(3610, 180)):
    """
    Gate a colored noise with a pulsed gaussian.
    """
    sine_oscillator = SineOscillator(
        frequency=frequency)
    pulsed_noise = PulseGenerator(
        distance=gate_distance,
        randomness=gate_randomness,
        pulse_signal=gate_signal)
    product = Product(sine_oscillator, pulsed_noise)
    return product
