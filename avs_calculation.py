import numpy as np
from ambient_noise import generate_ambient_noise
from avs_data import avs_data
from doa_est import doa_est
from grid_cord_est import grid_cord_new
from pos_true_theta import pos
from tx_sig import transmit_sig

def calculate_avs_metrics(TS, fs, seastate, duration, f, SX1, SY1, SX2, SY2, TPX1, TPY1):
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

    # Calculate the estimated position
    N = 3  # Example initialization
    T_est = grid_cord_new(N, SP, theta_estimate)

    # Update values
    TPX1, TPY1 = TP
    T_est_x, T_est_y = T_est
    range_error = np.sqrt((TPX1 - T_est_x)**2 + (TPY1 - T_est_y)**2)

    # Directly return results without conversion
    results = {
        "targetStrength": TS,
        "samplingRate": fs,
        "seastate": seastate,
        "signalDuration": duration,
        "noiseSourceFrequency": f,
        "avs1X": SX1,
        "avs1Y": SY1,
        "avs2X": SX2,
        "avs2Y": SY2,
        "avs3X": SX3,
        "avs3Y": SY3,
        "targetX": TPX1,
        "targetY": TPY1,
        "Tx": Tx,
        "t": t,
        "noise1": noise1,
        "noise2": noise2,
        "noise3": noise3,
        "rangeArr": D,
        "actualDoaArr": true_theta,
        "p1": p1,
        "vx1": vx1,
        "vy1": vy1,
        "SNR1": SNR1,
        "RNL1": RNL1,
        "p2": p2,
        "vx2": vx2,
        "vy2": vy2,
        "SNR2": SNR2,
        "RNL2": RNL2,
        "p3": p3,
        "vx3": vx3,
        "vy3": vy3,
        "estimatedDoa1": doa_est_1,
        "estimatedDoa2": doa_est_2,
        "estimatedDoa3": doa_est_3,
        "theta_estimate": theta_estimate,
        "doaError1": doa_error1,
        "doaError2": doa_error2,
        "estimatedTargetX": T_est_x,
        "estimatedTargetY": T_est_y,
        "rangeError": range_error
    }

    return results
