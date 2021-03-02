"""
Module for utility functions for the simulated GMD IOC.
"""

import numpy as np

def calc_attn_signal(signal, attn1, attn2):
    """
    Calculate output signal from raw based on attenuator settings.
    
    signal : list
        List of waveform values. 

    attn1 : int
        Attnuator 1 setting as an interger multiple of -3dB. Ranges from
        0 dB (attn1=0) to -45 dB (attn1=15).

    attn2 : int
        Attnuator 2 setting as an interger multiple of -3dB. Ranges from
        0 dB (attn2=0) to -45 dB (attn2=15).
    """
    assert 0 <= attn1 < 16
    assert 0 <= attn2 < 16

    total_db = -3*(attn1+attn2)

    out = [float(val)*10**(total_db/20) for val in signal]

    return out


def ThreshDetect(high_val, low_val, signal):
    if max(signal) > high_val:
        return -1
    elif max(signal) < low_val:
        return 1
    else:
        return 0

def PlateauDetect(n_plateau, signal):
    n_detected = 0
    for i in range(n_plateau, len(signal)):
        if signal[i-1] == signal[i]:
            n_detected += 1
        else:
            n_detected = 0
        if n_detected >= n_plateau:
            return 1
    return 0

def UpDownByOne(peak_status, current_att):
    if peak_status == -1: # Too high
        if current_att == 15:
            return 15
        else:
            return current_att + 1
    elif peak_status == 1: # Too low
        if current_att == 0:
            return 0
        else:
            return current_att - 1
    else: # Juuuusssst right (or something bad happened)
        return current_att

def EvenAttenuation(att_val):
    preatt = int(att_val%2 + att_val/2)
    posatt = int(att_val/2)
    return preatt, posatt

def FavorPost(preatt, posatt, peak_status, pd):
    if peak_status == -1: # Too high
        if pd: # There is a plateau
            if preatt < 15:
                return preatt+1, posatt
            elif posatt < 15:
                return preatt, posatt+1
        else:
            if posatt < 15:
                return preatt, posatt+1
            elif preatt < 15:
                return preatt+1, posatt
    elif peak_status == 1: # Too low
        if pd: # There is a plateau. Will this happen? Try to lower post by 2, 
               # increase pre by 1
            if preatt < 15:
                if posatt > 1:
                    return preatt+1, posatt-2
                elif preatt > 0:
                    return preatt-1, posatt
            elif preatt > 0:
                return preatt-1, posatt
            elif posatt > 0:
                return preatt, posatt-1
        else:
            if preatt > 0:
                return preatt-1, posatt
            elif posatt > 0:
                return preatt, posatt-1
    return preatt, posatt

#def PeakSharpen(signal, k2, k4):
def PeakSharpen(signal, k2):
    """
    Algorithm to sharpen a peak based on its even derivatives.

    Parameters
    ----------

    signal : list of numeric
        The signal to be differentiated

    k2 : 2nd derivative scaling parameter.

    k4 : 4th derivative scaling parameter.
    """
    d1sig = np.diff(signal)
    d2sig = np.diff(d1sig)
    # Each derivative returns an array of n-1 length. We want the output array
    # to maintain its original length, so pad the back side of the derivative
    # with copies of the last value (probably ~zero anyway since the original
    # signal is fairly flat in that region.
    last = d2sig[-1]
    d2sig = np.concatenate((d2sig, np.array([last, last])))
    retsig = [signal[i]-k2*d2sig[i] for i in range(len(signal))]

    return retsig

    
