import numpy as np

def avs_data(SL_dB, Source, r, theta, noise):
    """
    Calculate received signals and Signal-to-Noise Ratio (SNR) for a given source signal and noise.

    Parameters:
    SL_dB (float): Source level in dB.
    Source (np.ndarray): Source signal array.
    r (float): Distance from the source in meters.
    theta (float): Angle in degrees.
    noise (np.ndarray): Noise signal array.

    Returns:
    tuple: Containing the received signal (Rx), received cosine component (Rx_cos), 
           received sine component (Rx_sin), Signal-to-Noise Ratio (SNR), 
           and Reference Noise Level (RNL).
    """
    
    # Convert distance to meters if necessary, here assumed already in meters
    d = r
    
    # Calculate power of the source signal
    p_sig = np.mean(Source**2)
    
    # Normalize angle to be within 0 to 360 degrees
    if theta < 0:
        theta += 360
    
    # Calculate Transmission Loss (TL)
    TL = 20 * np.log10(d)
    
    # Calculate received power levels in dB
    PR1 = SL_dB - TL - 171.5
    PR = SL_dB + 4.8 - TL - 171.5
    
    # Convert dB to linear scale for signal amplitudes
    A = 10 ** (PR / 10)
    A1 = 10 ** (PR1 / 10)
    
    # Calculate scaling factors
    sf = np.sqrt(A / p_sig)
    sf1 = np.sqrt(A1 / p_sig)
    
    # Scale signals
    S0 = Source * sf1
    S = Source * sf
    S_sin = S * np.sin(np.deg2rad(theta))
    S_cos = S * np.cos(np.deg2rad(theta))
    
    # Add noise to the scaled signals
    Rx_sin = S_sin + noise
    Rx_cos = S_cos + noise
    Rx = S0 + noise
    
    # Calculate noise power
    p_noise1 = np.mean(noise**2)
    NL = 10 * np.log10(p_noise1)
    
    # Calculate Signal-to-Noise Ratio (SNR)
    SNR = abs(NL) - abs(PR)
    
    # Calculate Reference Noise Level (RNL)
    RNL = SL_dB - TL
    
    return Rx, Rx_cos, Rx_sin, SNR, RNL
