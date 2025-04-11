# Importar las bibliotecas necesarias
from scipy.signal import butter, filtfilt  # Para aplicar filtros digitales de Butterworth
import numpy as np  # Biblioteca para operaciones matemáticas y manejo de arrays

# Función para aplicar un filtro pasa-bajas
def filtro_pasa_bajas(audio, normal_cutoff, n):
    """Aplica un filtro pasa-bajas de Butterworth a una señal de audio.
    
    Parámetros:
    audio (numpy array): Señal de audio a filtrar
    normal_cutoff (float): Frecuencia de corte normalizada (relativa a la frecuencia de Nyquist)
    n (int): Orden del filtro
    
    Retorna:
    numpy array: Señal de audio filtrada
    """
    b, a = butter(N=n, Wn=normal_cutoff, btype='low', analog=False)  # Crear el filtro pasa-bajas
    return filtfilt(b, a, audio)  # Aplicar el filtro y retornar la señal procesada

# Función para aplicar un filtro pasa-altas
def filtro_pasa_altas(audio, normal_cutoff, n):
    """Aplica un filtro pasa-altas de Butterworth a una señal de audio.
    
    Parámetros:
    audio (numpy array): Señal de audio a filtrar
    normal_cutoff (float): Frecuencia de corte normalizada
    n (int): Orden del filtro
    
    Retorna:
    numpy array: Señal de audio filtrada
    """
    b, a = butter(N=n, Wn=normal_cutoff, btype='high', analog=False)  # Crear el filtro pasa-altas
    return filtfilt(b, a, audio)  # Aplicar el filtro y retornar la señal procesada

# Función para aplicar un filtro pasa-banda
def filtro_pasa_banda(audio, normal_cutoff_min, normal_cutoff_max, n):
    """Aplica un filtro pasa-banda de Butterworth a una señal de audio.
    
    Parámetros:
    audio (numpy array): Señal de audio a filtrar
    normal_cutoff_min (float): Frecuencia de corte inferior normalizada
    normal_cutoff_max (float): Frecuencia de corte superior normalizada
    n (int): Orden del filtro
    
    Retorna:
    numpy array: Señal de audio filtrada
    """
    b, a = butter(N=n, Wn=[normal_cutoff_min, normal_cutoff_max], btype='band', analog=False)  # Crear el filtro pasa-banda
    return filtfilt(b, a, audio)  # Aplicar el filtro y retornar la señal procesada

# Función para calcular la Transformada de Fourier de una señal
def transformada_fourier(audio, sample_rate):
    """Calcula la Transformada de Fourier de una señal de audio.
    
    Parámetros:
    audio (numpy array): Señal de audio a transformar
    sample_rate (int): Frecuencia de muestreo en Hz
    
    Retorna:
    tuple: (frecuencias, valores FFT)
    """
    N = len(audio)  # Obtener la cantidad de muestras de la señal
    fft = np.fft.fft(audio)  # Calcular la Transformada de Fourier
    freqs = np.fft.fftfreq(N, 1/sample_rate)  # Calcular las frecuencias correspondientes
    return freqs, fft  # Retornar el espectro de frecuencias y la transformada