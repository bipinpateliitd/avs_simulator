# TODO: DELETE LATER
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft
from ambient_noise import generate_ambient_noise
from avs_data import avs_data
from doa_est import doa_est
from theta2_avs import theta2_avs
from tx_sig import transmit_sig
from pos_true_theta import pos
from grid_cord_est import grid_cord_new
from main import saveToJSONFile


def saveCalculationsToJSONFile(TS, fs, seastate, duration, f, SX1, SY1, SX2, SY2, TPX1, TPY1):
    """
    Main function to perform AVS calculations and save the results to a JSON file.

    Parameters:
    TS (float): Target Strength dB re 1uPa
    fs (int): Sampling frequency in Hz
    seastate (int): Sea state
    duration (float): Duration of Signal in seconds
    f (float): Frequency of Noise Source in Hz
    SX1, SY1 (float): Sensor 1 positions
    SX2, SY2 (float): Sensor 2 positions
    TPX1, TPY1 (float): Target positions

    Returns:
    None
    """

    # Sensor positions
    SX3, SY3 = SX2, SY2
    SP = np.array([[SX1, SY1], [SX2, SY2], [SX3, SY3]])  # AVS Positions
    TP = np.array([TPX1, TPY1])  # Target Position

    # Generate transmitted signal
    Tx, t = transmit_sig(duration, fs, f, TS)

    # Generate ambient noise
    noise1 = generate_ambient_noise(seastate, fs, len(t))
    noise2 = generate_ambient_noise(seastate, fs, len(t))
    noise3 = generate_ambient_noise(seastate, fs, len(t))

    # Calculate distances and angles
    D, true_theta = pos(SP, TP)
    r1, r2, r3 = D
    theta1, theta2, theta3 = true_theta

    # Generate AVS data
    p1, vx1, vy1, SNR1, RNL1 = avs_data(TS, Tx, r1, theta1, noise1)
    p2, vx2, vy2, SNR2, RNL2 = avs_data(TS, Tx, r2, theta2, noise2)
    p3, vx3, vy3, _, _ = avs_data(TS, Tx, r3, theta3, noise3)

    # Estimate DOA
    doa_est_1 = doa_est(p1, vx1, vy1)
    doa_est_2 = doa_est(p2, vx2, vy2)
    doa_est_3 = doa_est(p3, vx3, vy3)
    theta_estimate = np.array([doa_est_1, doa_est_2, doa_est_3])

    doa_error1 = abs(theta1 - doa_est_1)
    doa_error2 = abs(theta2 - doa_est_2)

    # Example initialization of the application parameters
    N = 3

    # Calculate the estimated position
    T_est = grid_cord_new(N, SP, theta_estimate)

    # Update values
    TPX1, TPY1 = TP
    T_est_x, T_est_y = T_est
    range_error = np.sqrt((TPX1 - T_est_x)**2 + (TPY1 - T_est_y)**2)

    # Function to convert numpy types to native python types


# Function to convert numpy types to native python types


    def convert_to_native_type(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        return obj

    # Convert the results dictionary
    results = {
        "TS": convert_to_native_type(TS),
        "fs": convert_to_native_type(fs),
        "seastate": convert_to_native_type(seastate),
        "duration": convert_to_native_type(duration),
        "f": convert_to_native_type(f),
        "SX1": convert_to_native_type(SX1),
        "SY1": convert_to_native_type(SY1),
        "SX2": convert_to_native_type(SX2),
        "SY2": convert_to_native_type(SY2),
        "SX3": convert_to_native_type(SX3),
        "SY3": convert_to_native_type(SY3),
        "TPX1": convert_to_native_type(TPX1),
        "TPY1": convert_to_native_type(TPY1),
        "Tx": convert_to_native_type(Tx),
        "t": convert_to_native_type(t),
        "noise1": convert_to_native_type(noise1),
        "noise2": convert_to_native_type(noise2),
        "noise3": convert_to_native_type(noise3),
        "D": convert_to_native_type(D),
        "true_theta": convert_to_native_type(true_theta),
        "p1": convert_to_native_type(p1),
        "vx1": convert_to_native_type(vx1),
        "vy1": convert_to_native_type(vy1),
        "SNR1": convert_to_native_type(SNR1),
        "RNL1": convert_to_native_type(RNL1),
        "p2": convert_to_native_type(p2),
        "vx2": convert_to_native_type(vx2),
        "vy2": convert_to_native_type(vy2),
        "SNR2": convert_to_native_type(SNR2),
        "RNL2": convert_to_native_type(RNL2),
        "p3": convert_to_native_type(p3),
        "vx3": convert_to_native_type(vx3),
        "vy3": convert_to_native_type(vy3),
        "doa_est_1": convert_to_native_type(doa_est_1),
        "estimatedDoa2": convert_to_native_type(doa_est_2),
        "estimatedDoa3": convert_to_native_type(doa_est_3),
        "theta_estimate": convert_to_native_type(theta_estimate),
        "doaError1": convert_to_native_type(doa_error1),
        "doaError2": convert_to_native_type(doa_error2),
        "estimatedTargetX": convert_to_native_type(T_est_x),
        "estimatedTargetX": convert_to_native_type(T_est_y),
        "rangeError": convert_to_native_type(range_error)
    }

    # Saving the results dictionary to a JSON file
    saveToJSONFile("calculations.json", results)
