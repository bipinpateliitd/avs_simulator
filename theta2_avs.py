import numpy as np

def theta2_avs(Rx, Rx_sin, Rx_cos):
    """
    Estimate the angles of arrival (theta_est) for a given set of hydrophone and accelerometer data.

    Parameters:
    Rx (np.ndarray): Hydrophone data, shape (M, N).
    Rx_sin (np.ndarray): Accelerometer data for the y-axis, shape (M, N).
    Rx_cos (np.ndarray): Accelerometer data for the x-axis, shape (M, N).

    Returns:
    np.ndarray: Estimated angles of arrival in degrees, shape (M,).
    """
    
    M = 3  # Number of sensors or sets of data
    theta_est = np.zeros(M)
    
    for i in range(M):
        # Perform FFT on the input signals
        Sin_fft = np.fft.fft(Rx[i, :])
        S_cosine_fft = np.fft.fft(Rx_cos[i, :])
        S_sine_fft = np.fft.fft(Rx_sin[i, :])
        
        # Determine the number of points in the FFT result
        no_points = len(Sin_fft)
        
        # Find the index of the maximum value in the first half of the FFT result
        index = np.argmax(np.abs(Sin_fft[:no_points // 2]))
        
        # Calculate y and x using the imaginary parts of the FFT results
        y = np.imag(S_sine_fft[index]) * np.imag(Sin_fft[index])
        x = np.imag(S_cosine_fft[index]) * np.imag(Sin_fft[index])
        
        # Estimate the angle of arrival (theta_est) in degrees
        theta_est[i] = np.degrees(np.arctan2(y, x))
        
        # Normalize angle to be within 0 to 360 degrees
        if theta_est[i] < 0:
            theta_est[i] += 360
    
    return theta_est

"""
# Example usage:
Rx = np.random.randn(3, 1024)  # Simulated received signals
Rx_sin = np.random.randn(3, 1024)  # Simulated sine component of received signals
Rx_cos = np.random.randn(3, 1024)  # Simulated cosine component of received signals

theta_est = theta2_avs(Rx, Rx_sin, Rx_cos)
print("Estimated angles:", theta_est)
"""
