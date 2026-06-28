from __future__ import annotations
import numpy as np


def pwm_fourier_magnitudes(duty: float = 0.382, harmonics: int = 40, v_bus: float = 24.0, bipolar: bool = True) -> np.ndarray:
    """Return ideal PWM voltage harmonic magnitudes |V_n| for n=1..harmonics.
    For bipolar square/PWM centered around zero, multiply by 2 relative to unipolar AC component.
    DC is intentionally excluded.
    """
    n = np.arange(1, int(harmonics)+1, dtype=float)
    mag = (v_bus / (np.pi*n)) * np.abs(np.sin(np.pi*n*float(duty)))
    if bipolar:
        mag *= 2.0
    return mag


def phase_factor(phase_index: int, harmonic_n: int) -> complex:
    return np.exp(1j * 2.0*np.pi * (phase_index % 3) / 3.0 * harmonic_n)
