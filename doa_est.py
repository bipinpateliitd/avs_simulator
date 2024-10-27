import numpy as np

def doa_est(Sin, S_cosine, S_sine):
    """
    Estimate the Direction of Arrival (DoA) of a signal using FFT.

    Parameters:
    Sin (np.ndarray): Input signal array.
    S_cosine (np.ndarray): Cosine component of the signal.
    S_sine (np.ndarray): Sine component of the signal.

    Returns:
    float: Estimated direction of arrival (theta_est) in degrees.
    """
    
    # Perform FFT on the input signals
    Sin_fft = np.fft.fft(Sin)
    S_cosine_fft = np.fft.fft(S_cosine)
    S_sine_fft = np.fft.fft(S_sine)
    
    # Determine the number of points in the FFT result
    no_points = len(Sin_fft)
    
    # Find the index of the maximum value in the first half of the FFT result
    index = np.argmax(np.abs(Sin_fft[:no_points // 2]))
    
    # Calculate y and x using the imaginary parts of the FFT results
    y = np.imag(S_sine_fft[index]) * np.imag(Sin_fft[index])
    x = np.imag(S_cosine_fft[index]) * np.imag(Sin_fft[index])
    
    # Estimate the direction of arrival (theta_est) in degrees
    theta_est = np.degrees(np.arctan2(y, x))
    
    # Normalize angle to be within 0 to 360 degrees
    if theta_est < 0:
        theta_est = 360 + theta_est
    
    return theta_est
