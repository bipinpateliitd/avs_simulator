import numpy as np

def pos(SP, TP):
    """
    Calculate distances and angles from AVS (Acoustic Vector Sensor) positions to a target position.

    Parameters:
    SP (np.ndarray): Array of AVS positions, shape (3, 2).
    TP (np.ndarray): Target position, shape (2,).

    Returns:
    tuple: Containing:
        - np.ndarray: Distances from each AVS to the target, shape (3,).
        - np.ndarray: Angles from each AVS to the target in degrees, shape (3,).
    """
    
    # Calculate distances from each AVS to the target position
    D1 = np.sqrt((SP[0, 0] - TP[0])**2 + (SP[0, 1] - TP[1])**2)
    D2 = np.sqrt((SP[1, 0] - TP[0])**2 + (SP[1, 1] - TP[1])**2)
    D3 = np.sqrt((SP[2, 0] - TP[0])**2 + (SP[2, 1] - TP[1])**2)
    D = np.array([D1, D2, D3])
    
    # Calculate angles from each AVS to the target position
    XX = TP[0] - SP[:, 0]
    YY = TP[1] - SP[:, 1]
    true_theta = np.degrees(np.arctan2(YY, XX))
    
    # Normalize angles to be between 0 and 360 degrees
    true_theta = np.where(true_theta < 0, true_theta + 360, true_theta)
    
    return D, true_theta

"""
# Example usage:
SP = np.array([[0, 0], [1, 0], [0, 1]])  # AVS positions
TP = np.array([1, 1])  # Target position

distances, angles = pos(SP, TP)
print("Distances:", distances)
print("Angles:", angles)
"""
