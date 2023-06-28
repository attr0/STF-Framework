import numpy as np

def filling(X_input: np.ndarray):
    # calc the average
    mean = np.nanmean(X_input)
    # fill the na
    np.nan_to_num(X_input, copy=False, nan=mean)

def preprocess(X_input: np.ndarray):
    return X_input