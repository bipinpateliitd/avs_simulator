import base64
import io
import json
import os

import eel
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np
from ambient_noise import generate_ambient_noise
from avs_data import avs_data
from doa_est import doa_est
from grid_cord_est import grid_cord_new
from matplotlib.cm import ScalarMappable
from pos_true_theta import pos
from scipy.fft import fft, ifft
from theta2_avs import theta2_avs
from tx_sig import transmit_sig

IS_DEV = True

# ########## BASIC FILE HANDLING FUNCTIONS


def getRootDBPath(relative_path=None):
    if IS_DEV:
        base_path = os.path.abspath("./db")
    else:
        base_path = os.path.join(os.path.dirname(__file__), "db")

    if relative_path:
        return os.path.join(base_path, relative_path)
    else:
        return base_path


@eel.expose
def saveToJSONFile(jsonFileName, data):
    file_path = getRootDBPath(jsonFileName)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving JSON file: {e}")


# get data from specified file
@eel.expose
def getFromJSONFile(jsonFileName):
    try:
        with open(getRootDBPath(jsonFileName), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("File not found")
        return None
    except json.JSONDecodeError:
        print("File is Empty")
        return None


# Remove Duplicate data, excluding recordtime from input history
@eel.expose
def removeDuplicateHistory(data, key_to_ignore="recordTime"):
    seen = set()
    result = []

    for item in data:
        # Create a frozenset of the dictionary items excluding the key to ignore
        item_to_check = frozenset((k, v)
                                  for k, v in item.items() if k != key_to_ignore)

        if item_to_check not in seen:
            seen.add(item_to_check)
            result.append(item)

    return result


# Update Input history by prepending specified data
@eel.expose
def updateInputHistory(newData):
    fileName = "inputs-history.json"
    # If data is said to be set empty
    if (newData == []):
        saveToJSONFile(fileName, [])
        return

    # Get existing data
    existingHistory = getFromJSONFile(fileName)

    # If file doesn't exist or it is empty
    if (existingHistory == None):
        saveToJSONFile(fileName, [newData])
        return

    # At last, prepend current data, remove duplicates if any, and save
    updatedHistory = [newData] + existingHistory
    updatedHistory = removeDuplicateHistory(updatedHistory)
    saveToJSONFile(fileName, updatedHistory)

# ########## PERFORM AND SAVE CALCULATIONS


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
    # ###### ###### THROWS ERROR ###### ######
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
        "targetStrength": convert_to_native_type(TS),
        "samplingRate": convert_to_native_type(fs),
        "seastate": convert_to_native_type(seastate),
        "signalDuration": convert_to_native_type(duration),
        "noiseSourceFrequency": convert_to_native_type(f),
        "avs1X": convert_to_native_type(SX1),
        "avs1Y": convert_to_native_type(SY1),
        "avs2X": convert_to_native_type(SX2),
        "avs2Y": convert_to_native_type(SY2),
        "avs3X": convert_to_native_type(SX3),
        "avs3X": convert_to_native_type(SY3),
        "targetX": convert_to_native_type(TPX1),
        "targetY": convert_to_native_type(TPY1),
        "Tx": convert_to_native_type(Tx),
        "t": convert_to_native_type(t),
        "noise1": convert_to_native_type(noise1),
        "noise2": convert_to_native_type(noise2),
        "noise3": convert_to_native_type(noise3),
        "rangeArr": convert_to_native_type(D),
        "actualDoaArr": convert_to_native_type(true_theta),
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
        "estimatedDoa1": convert_to_native_type(doa_est_1),
        "estimatedDoa2": convert_to_native_type(doa_est_2),
        "estimatedDoa3": convert_to_native_type(doa_est_3),
        "theta_estimate": convert_to_native_type(theta_estimate),
        "doaError1": convert_to_native_type(doa_error1),
        "doaError2": convert_to_native_type(doa_error2),
        "estimatedTargetX": convert_to_native_type(T_est_x),
        "estimatedTargetY": convert_to_native_type(T_est_y),
        "rangeError": convert_to_native_type(range_error)
    }

    # Saving the results dictionary to a JSON file
    saveToJSONFile("calculations.json", results)


@eel.expose
def performCalculations():
    inputData = getFromJSONFile("inputs.json")
    saveCalculationsToJSONFile(
        inputData["targetStrength"],
        inputData["samplingRate"],
        inputData["seastate"],
        inputData["signalDuration"],
        inputData["noiseSourceFrequency"],
        inputData["avs1X"],
        inputData["avs1Y"],
        inputData["avs2X"],
        inputData["avs2Y"],
        inputData["targetX"],
        inputData["targetY"]
    )


# ########## AUDIO FILE HANDLING FUNCTIONS


@eel.expose
def saveSpectrogramImage(yAxisDataName):

    inputData = getFromJSONFile("calculations.json")

    try:
        signal = inputData[yAxisDataName]
    except KeyError:
        print("The key", yAxisDataName, "doesn't exist")
        return None
    signal = np.array(signal)
    samplingRate = inputData["samplingRate"]

    # Compute the Short-Time Fourier Transform (STFT)
    D = librosa.stft(signal, n_fft=2048, hop_length=512, win_length=2048)
    DP = np.abs(D) ** 2

    # Convert the amplitude to dB-scaled spectrogram
    S_db = librosa.power_to_db(DP)

    # Create a buffer to save image
    buffer = io.BytesIO()

    # Plotting without colorbar
    plt.figure(figsize=(10, 6))
    librosa.display.specshow(S_db, sr=samplingRate,
                             hop_length=512, x_axis='time', y_axis='linear')
    plt.axis('off')  # No axes for a cleaner image
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buffer.seek(0)

    # Encode the byte array as base64 string
    encoded_image = base64.b64encode(buffer.read()).decode('utf-8')

    # Cleanup and return the base64 string
    buffer.close()
    return encoded_image


# ########## STARTTING APPLICATION
eel.init("web")
eel.start('index.html', port=1234, host='localhost')
