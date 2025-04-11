import customtkinter as ctk
from tkinter import filedialog, messagebox
import librosa
import numpy as np
import matplotlib.pyplot as plt
import funcionesFiltros
import soundfile as sf

# Configurar el tema de la interfaz
ctk.set_appearance_mode("light")

# Crear la ventana principal de la aplicación
app = ctk.CTk()
app.title("HMI para Procesamiento de Señales")
app.geometry("600x500")

# Función para cargar archivo de audio desde el sistema
def cargar_audio():
    """Carga un archivo de audio y almacena la señal y su frecuencia de muestreo."""
    filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.aac")])
    if filepath:
        global audio, sample_rate
        audio, sample_rate = librosa.load(filepath, sr=None)
        messagebox.showinfo("Archivo cargado", f"Se ha cargado el archivo: {filepath}")

# Función para guardar el archivo procesado
def guardar_archivo():
    """Guarda el audio filtrado en un archivo seleccionado por el usuario."""
    if 'audio_filtrado' in globals():
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAV", "*.wav")])
        if save_path:
            sf.write(save_path, audio_filtrado, sample_rate)
            messagebox.showinfo("Archivo guardado", f"Archivo guardado en: {save_path}")
    else:
        messagebox.showerror("Error", "No hay archivo filtrado para guardar.")

# Función para actualizar los controles de frecuencia según el filtro seleccionado
def actualizar_deslizadores(*args):
    """Muestra u oculta el segundo deslizador si se selecciona 'Pasa-banda'."""
    if filtro_var.get() == "Pasa-banda":
        slider_cutoff_max.grid(row=1, column=1, padx=10, pady=5)
        label_frecuencia_max.grid(row=1, column=2, padx=10, pady=5)
    else:
        slider_cutoff_max.grid_forget()
        label_frecuencia_max.grid_forget()

# Función para actualizar la etiqueta de frecuencia mínima
def actualizar_frecuencia(valor):
    """Actualiza la etiqueta con el valor seleccionado en el deslizador de frecuencia."""
    label_frecuencia.configure(text=f"{int(valor)} Hz")

# Función para actualizar la etiqueta de frecuencia máxima en caso de filtro pasa-banda
def actualizar_frecuencia_max(valor):
    """Actualiza la etiqueta con el valor de la segunda frecuencia en filtro pasa-banda."""
    label_frecuencia_max.configure(text=f"{int(valor)} Hz")

# Función para aplicar el filtro seleccionado
def aplicar_filtro():
    """Aplica el filtro seleccionado a la señal de audio cargada."""
    if 'audio' not in globals():
        messagebox.showerror("Error", "Primero carga un archivo de audio.")
        return

    tipo = filtro_var.get()
    order = int(entry_orden.get())
    nyquist = 0.5 * sample_rate  # Frecuencia de Nyquist

    global audio_filtrado
    if tipo == "Pasa-bajas":
        cutoff = slider_cutoff.get()
        normal_cutoff = cutoff / nyquist
        audio_filtrado = funcionesFiltros.filtro_pasa_bajas(audio, normal_cutoff, n=order)
    elif tipo == "Pasa-altas":
        cutoff = slider_cutoff.get()
        normal_cutoff = cutoff / nyquist
        audio_filtrado = funcionesFiltros.filtro_pasa_altas(audio, normal_cutoff, n=order)
    elif tipo == "Pasa-banda":
        cutoff_min = slider_cutoff.get()
        cutoff_max = slider_cutoff_max.get()
        normal_cutoff_min = cutoff_min / nyquist
        normal_cutoff_max = cutoff_max / nyquist
        audio_filtrado = funcionesFiltros.filtro_pasa_banda(audio, normal_cutoff_min, normal_cutoff_max, n=order)
    else:
        messagebox.showerror("Error", "Filtro no reconocido")
        return

    # Aplicar transformada de Fourier y graficar resultados
    freqsn, fft_normal = funcionesFiltros.transformada_fourier(audio, sample_rate)
    freqsf, fft_filtrada = funcionesFiltros.transformada_fourier(audio_filtrado, sample_rate)

    plt.figure(figsize=(12, 8))

    # Señal original
    plt.subplot(2, 2, 1)
    plt.plot(np.linspace(0, len(audio) / sample_rate, len(audio)), audio, color='blue')
    plt.title("Señal original")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")

    # Señal filtrada
    plt.subplot(2, 2, 2)
    plt.plot(np.linspace(0, len(audio_filtrado) / sample_rate, len(audio_filtrado)), audio_filtrado, color='red')
    plt.title(f"Señal Filtrada ({tipo})")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")

    # Transformada de Fourier de la señal original
    plt.subplot(2, 2, 3)
    maskn = freqsn > 0
    plt.plot(freqsn[maskn], np.abs(fft_normal)[maskn], color='orange')
    plt.title("Transformada de Fourier audio normal")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud")
    plt.grid()

    # Transformada de Fourier de la señal filtrada
    plt.subplot(2, 2, 4)
    maskf = freqsf > 0
    plt.plot(freqsf[maskf], np.abs(fft_filtrada)[maskf], color='green')
    plt.title("Transformada de Fourier audio filtrado")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud")
    plt.grid()

    plt.tight_layout()
    plt.show()

# Interfaz gráfica y controles
frame_controles = ctk.CTkFrame(app)
frame_controles.pack(pady=20, padx=20, fill="both", expand=True)

btn_cargar = ctk.CTkButton(frame_controles, text="Cargar Archivo", command=cargar_audio)
btn_cargar.pack(pady=5)

# Menú de selección de filtros
filtro_var = ctk.StringVar(value="Pasa-bajas")
filtro_var.trace("w", actualizar_deslizadores)
menu_filtro = ctk.CTkComboBox(frame_controles, variable=filtro_var, values=["Pasa-bajas", "Pasa-altas", "Pasa-banda"])
menu_filtro.pack(pady=5)

# Controles de frecuencia
frame_frecuencia = ctk.CTkFrame(frame_controles)
frame_frecuencia.pack(pady=5, fill="x")

slider_cutoff = ctk.CTkSlider(frame_frecuencia, from_=1, to=10000, command=actualizar_frecuencia)
slider_cutoff.grid(row=0, column=1, padx=10)
label_frecuencia = ctk.CTkLabel(frame_frecuencia, text="1 Hz")
label_frecuencia.grid(row=0, column=2, padx=10)

slider_cutoff_max = ctk.CTkSlider(frame_frecuencia, from_=1, to=10000, command=actualizar_frecuencia_max)
label_frecuencia_max = ctk.CTkLabel(frame_frecuencia, text="1 Hz")

entry_orden = ctk.CTkEntry(frame_controles)
entry_orden.insert(0, "2")
entry_orden.pack(pady=5)

btn_filtro = ctk.CTkButton(frame_controles, text="Aplicar Filtro", command=aplicar_filtro)
btn_filtro.pack(side="left", padx=10)

btn_guardar = ctk.CTkButton(frame_controles, text="Guardar Archivo", command=guardar_archivo)
btn_guardar.pack(side="right", padx=10)

app.mainloop()