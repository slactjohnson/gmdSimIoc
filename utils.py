"""
Module for utility functions for the simulated GMD IOC.
"""

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



