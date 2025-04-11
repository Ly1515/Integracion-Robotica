from scipy.signal import butter, filtfilt
import numpy as np

def filtro_pasa_bajas(audio, normal_cutoff, n):
    b, a = butter(N=n, Wn=normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, audio)

def filtro_pasa_altas(audio, normal_cutoff, n):
    b, a = butter(N=n, Wn=normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, audio)

def filtro_pasa_banda(audio, normal_cutoff_min, normal_cutoff_max, n):
    b, a = butter(N=n, Wn=[normal_cutoff_min, normal_cutoff_max], btype='band', analog=False)
    return filtfilt(b, a, audio)

def transformada_fourier(audio, sample_rate):
    N = len(audio)
    fft = np.fft.fft(audio)
    freqs = np.fft.fftfreq(N, 1/sample_rate)
    return freqs, fft
