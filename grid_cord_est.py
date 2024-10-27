import numpy as np

def grid_cord_new(N, X, thet):
    """
    Estimate the coordinates of a target using a grid search method.

    Parameters:
    N (int): Number of sensors.
    X (np.ndarray): Array of sensor positions, shape (N, 2).
    thet (np.ndarray): Array of measured angles in degrees, shape (N,).

    Returns:
    np.ndarray: Estimated target coordinates.
    """
    
    # Initial grid spacing and range
    S = 100
    CX = np.arange(-10000, 10001, S)
    XX = np.array(np.meshgrid(CX, CX)).T.reshape(-1, 2)
    T_est = None

    for jj in range(4):  # Assuming four iterations for refinement
        tol = 1  # Initial tolerance for grid refinement
        phi = np.zeros((N, len(XX)))
        
        # Calculate angles from all points on the grid to each sensor
        for i2 in range(len(XX)):
            for i3 in range(N):
                ty = XX[i2, 1] - X[i3, 1]
                tx = XX[i2, 0] - X[i3, 0]
                phi[i3, i2] = np.degrees(np.arctan2(ty, tx))
                if phi[i3, i2] < 0:
                    phi[i3, i2] += 360

        # Calculate angular residuals
        theta_resd = np.zeros(len(XX))
        for i4 in range(len(XX)):
            theta_diff = np.zeros(N)
            for i5 in range(N):
                Xp = thet[i5]
                Yp = phi[i5, i4]
                a = np.abs(np.exp(1j * np.radians(Xp)) - np.exp(1j * np.radians(Yp))) / 2
                theta_diff[i5] = 2 * np.degrees(np.arcsin(a))
            theta_resd[i4] = np.sum(theta_diff)

        # Find the minimum residual and refine the grid around this point
        n = np.argmin(theta_resd)
        T_est = XX[n]
        mx, my = T_est
        MX = np.arange(mx - tol * S, mx + tol * S + S / 10, S / 10)
        MY = np.arange(my - tol * S, my + tol * S + S / 10, S / 10)
        XX = np.array(np.meshgrid(MX, MY)).T.reshape(-1, 2)

        # Reduce the grid spacing and increase tolerance
        S /= 10
        tol += 1

    return T_est

"""
# Example usage:
N = 3
X = np.array([[100, 200], [300, 400], [500, 600]])  # Sensor positions
thet = np.array([45, 135, 225])  # Measured angles in degrees

T_est = grid_cord_new(N, X, thet)
print("Estimated position:", T_est)
"""
