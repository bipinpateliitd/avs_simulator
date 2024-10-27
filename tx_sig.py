import numpy as np

def transmit_sig(duration, fs, f, SL_dB):
    """
    Generate a transmitted signal with specified duration, sampling frequency, frequency, and source level.

    Parameters:
    duration (float): Duration of the signal in seconds.
    fs (int): Sampling frequency in Hz.
    f (float): Frequency of the sinusoidal signal in Hz.
    SL_dB (float): Source level in dB.

    Returns:
    tuple: Containing:
        - np.ndarray: The generated transmitted signal.
        - np.ndarray: The time array corresponding to the signal.
    """
    
    # Generate time array
    t = np.linspace(0, duration, int(duration * fs))
    
    # Generate sinusoidal transmitted signal
    Tx = np.sin(2 * np.pi * f * t)
    
    # Calculate the power of the signal
    p_sig = np.mean(Tx ** 2)
    
    # Calculate the desired power level
    PR = SL_dB - 171.5
    A = 10 ** (PR / 10)
    
    # Calculate the scaling factor
    sf = np.sqrt(A / p_sig)
    
    # Scale the transmitted signal to the desired power level
    Tx = Tx * sf
    
    return Tx, t

"""
# Example usage:
duration = 1.0  # Duration in seconds
fs = 44100  # Sampling frequency in Hz
f = 1000  # Frequency of the signal in Hz
SL_dB = 120  # Source level in dB

Tx, t = transmit_sig(duration, fs, f, SL_dB)
print("Transmitted signal:", Tx)
print("Time array:", t)
"""
