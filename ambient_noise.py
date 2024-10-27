import numpy as np
from scipy.fft import fft, ifft
from scipy.interpolate import interp1d

def generate_ambient_noise(seastate, fs, N):
    """
    Generate ambient noise for a given sea state, sampling frequency, and sample size.

    Parameters:
    seastate (int): The sea state (0, 1, 3, or 6).
    fs (int): The sampling frequency in Hz.
    N (int): The number of samples.

    Returns:
    np.ndarray: The generated ambient noise signal.
    """
    
    # Determine l based on fs (sampling frequency)
    if 5000 < fs <= 10000:
        k = 15
    elif 10000 < fs <= 20000:
        k = 16
    elif 20000 < fs <= 50000:
        k = 17
    elif 50000 < fs <= 100000:
        k = 18

    # Define frequency and noise level arrays
    f = np.array([0.001, 0.1, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000])
    amb0 = np.array([0, 0, 0, 0, 0, 0, 83, 82, 80, 44, 43.5, 43, 39, 31, 27, 20.5, 15, 10])
    amb1 = np.array([0, 0, 0, 0, 0, 0, 83, 82, 80, 53, 52.5, 52, 48, 41, 37, 30.5, 23, 20])
    amb3 = np.array([0, 0, 0, 0, 0, 0, 83, 82, 80, 67, 66, 62, 57, 50, 46, 40, 32, 29])
    amb6 = np.array([0, 0, 0, 0, 0, 0, 83, 82, 80, 73, 72, 69, 63, 56, 51, 47, 40, 35])
    amb = np.vstack([amb0, amb1, amb3, amb6])

    # Select appropriate ambient noise levels based on sea state and fs
    freq = f[:k] # ########## ON THIS LINE
    uric_data_power_db = amb[seastate, :k]

    # Convert dB to power
    uric_data_power = 10 ** (uric_data_power_db / 10)
    total_power = np.sum(uric_data_power)
    NL_db = 10 * np.log10(total_power)
    scaled_power = 10 ** ((NL_db - 171.5) / 10)

    # Interpolate noise data
    xx = np.linspace(0.001, fs / 2, N // 2 + 1)
    interp_func = interp1d(freq, uric_data_power_db, kind='cubic')
    interpolated_power_db = interp_func(xx) - 171.5

    # Generate white noise and apply frequency-dependent gain
    rng = np.random.default_rng()
    x = rng.standard_normal(N)
    X = fft(x)
    noise_amp = np.sqrt(10 ** (interpolated_power_db / 10))

    # Apply the calculated amplitude to the noise
    unique_pts = N // 2 + 1  # includes the Nyquist frequency if N is even
    X[:unique_pts] *= noise_amp[:unique_pts]
    if N % 2 == 0:
        # Handle even N separately to correctly mirror and conjugate
        X[unique_pts:] = X[unique_pts - 2:0:-1].conjugate()
    else:
        # For odd N, handle without the Nyquist frequency
        X[unique_pts:] = X[unique_pts - 1:0:-1].conjugate()

    # Inverse FFT to get the time domain signal
    y = ifft(X).real
    y -= np.mean(y)  # Remove DC offset
    y_std_dev = np.std(y)
    scaling_factor = np.sqrt(scaled_power / y_std_dev ** 2)
    y *= scaling_factor  # Scale to match the desired power

    return y
