# Importar bibliotecas necesarias
import customtkinter as ctk  # Biblioteca para interfaz gráfica de usuario
from tkinter import filedialog, messagebox  # Utilidades para diálogos de archivos y mensajes
import librosa  # Librería para análisis y manipulación de audio
import numpy as np  # Biblioteca para manejo de arrays y operaciones matemáticas
import matplotlib.pyplot as plt  # Biblioteca para crear gráficos
import funcionesFiltros  # Módulo personalizado para filtros y transformada de Fourier
import soundfile as sf  # Biblioteca para lectura y escritura de archivos de audio

# Configurar el tema de la interfaz gráfica de usuario
ctk.set_appearance_mode("light")  # Configuración del modo claro para la interfaz

# Crear ventana principal
app = ctk.CTk()  # Inicializar ventana principal de la aplicación
app.title("HMI para Procesamiento de Señales")  # Título de la ventana
app.geometry("600x500")  # Tamaño inicial de la ventana

# Función para cargar un archivo de audio
def cargar_audio():
    """Permite al usuario cargar un archivo de audio desde su sistema."""
    filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.aac")])
    if filepath:  # Verifica que se haya seleccionado un archivo
        global audio, sample_rate
        audio, sample_rate = librosa.load(filepath, sr=None)  # Cargar el archivo de audio
        messagebox.showinfo("Archivo cargado", f"Se ha cargado el archivo: {filepath}")  # Notificación de éxito

# Función para guardar el archivo de audio procesado
def guardar_archivo():
    """Permite guardar el archivo de audio filtrado en formato WAV."""
    if 'audio_filtrado' in globals():  # Verificar si el audio filtrado existe
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAV", "*.wav")])
        if save_path:  # Verifica que se haya especificado una ruta de guardado
            sf.write(save_path, audio_filtrado, sample_rate)  # Guardar el archivo procesado
            messagebox.showinfo("Archivo guardado", f"Archivo guardado en: {save_path}")  # Notificación de éxito
    else:
        messagebox.showerror("Error", "No hay archivo filtrado para guardar.")  # Mostrar error

# Función para actualizar la interfaz según el filtro seleccionado
def actualizar_deslizadores(*args):
    """Muestra u oculta los controles de frecuencia adicionales según el filtro."""
    if filtro_var.get() == "Pasa-banda":
        slider_cutoff_max.grid(row=1, column=1, padx=10, pady=5)
        label_frecuencia_max.grid(row=1, column=2, padx=10, pady=5)
    else:
        slider_cutoff_max.grid_forget()
        label_frecuencia_max.grid_forget()

# Función para actualizar etiquetas de frecuencias dinámicamente
def actualizar_frecuencia(valor):
    """Actualiza la etiqueta de frecuencia según el valor del deslizador."""
    label_frecuencia.configure(text=f"{int(valor)} Hz")

def actualizar_frecuencia_max(valor):
    """Actualiza la etiqueta de frecuencia máxima para filtros pasa-banda."""
    label_frecuencia_max.configure(text=f"{int(valor)} Hz")

# Función para aplicar un filtro al audio cargado
def aplicar_filtro():
    """Aplica el filtro seleccionado al archivo de audio cargado y muestra los gráficos."""
    if 'audio' not in globals():  # Validar que haya un archivo cargado
        messagebox.showerror("Error", "Primero carga un archivo de audio.")
        return

    # Configuración inicial del filtro
    tipo = filtro_var.get()  # Tipo de filtro seleccionado
    order = int(entry_orden.get())  # Orden del filtro
    nyquist = 0.5 * sample_rate  # Frecuencia de Nyquist

    #Declarar la variable global para almacenar el audio filtrado
    global audio_filtrado  # Mantiene el resultado del filtrado para ser utilizado en otras funciones

    """Evaluar el tipo de filtro seleccionado por el usuario y aplicar la transformación correspondiente"""
    if tipo == "Pasa-bajas":
        cutoff = slider_cutoff.get()  # Obtener la frecuencia de corte desde el deslizador
        normal_cutoff = cutoff / nyquist  # Normalizar la frecuencia con respecto a la frecuencia de Nyquist
        audio_filtrado = funcionesFiltros.filtro_pasa_bajas(audio, normal_cutoff, n=order)  # Aplicar filtro pasa-bajas

    elif tipo == "Pasa-altas":
        cutoff = slider_cutoff.get()  # Obtener la frecuencia de corte
        normal_cutoff = cutoff / nyquist  # Normalizar la frecuencia
        audio_filtrado = funcionesFiltros.filtro_pasa_altas(audio, normal_cutoff, n=order)  # Aplicar filtro pasa-altas

    elif tipo == "Pasa-banda":
        cutoff_min = slider_cutoff.get()  # Frecuencia mínima de corte
        cutoff_max = slider_cutoff_max.get()  # Frecuencia máxima de corte
        normal_cutoff_min = cutoff_min / nyquist  # Normalizar frecuencia mínima
        normal_cutoff_max = cutoff_max / nyquist  # Normalizar frecuencia máxima
        audio_filtrado = funcionesFiltros.filtro_pasa_banda(audio, normal_cutoff_min, normal_cutoff_max, n=order)  # Aplicar filtro pasa-banda

    else:
        messagebox.showerror("Error", "Filtro no reconocido")  # Mostrar error si el filtro no es válido
        return  # Salir de la función

    # Calcular la transformada de Fourier del audio original y filtrado
    freqsn, fft_normal = funcionesFiltros.transformada_fourier(audio, sample_rate)  # FFT del audio original
    freqsf, fft_filtrada = funcionesFiltros.transformada_fourier(audio_filtrado, sample_rate)  # FFT del audio filtrado

    # Configurar la figura para visualizar los resultados
    plt.figure(figsize=(12, 8))

    # Graficar la señal original en el dominio del tiempo
    plt.subplot(2, 2, 1)
    plt.plot(np.linspace(0, len(audio) / sample_rate, len(audio)), audio, color='blue')
    plt.title("Señal original")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")

    # Graficar la señal filtrada en el dominio del tiempo
    plt.subplot(2, 2, 2)
    plt.plot(np.linspace(0, len(audio_filtrado) / sample_rate, len(audio_filtrado)), audio_filtrado, color='red')
    plt.title(f"Señal Filtrada ({tipo})")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")

    # Graficar el espectro de frecuencias del audio original (solo frecuencias positivas)
    plt.subplot(2, 2, 3)
    maskn = freqsn > 0  # Filtrar solo frecuencias positivas
    plt.plot(freqsn[maskn], np.abs(fft_normal)[maskn], color='orange')
    plt.title("Transformada de Fourier - Original")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud")

    # Graficar el espectro de frecuencias del audio filtrado (solo frecuencias positivas)
    plt.subplot(2, 2, 4)
    maskf = freqsf > 0  # Filtrar solo frecuencias positivas
    plt.plot(freqsf[maskf], np.abs(fft_filtrada)[maskf], color='green')
    plt.title("Transformada de Fourier - Filtrado")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud")

    # Ajustar el diseño de los gráficos para una mejor visualización
    plt.tight_layout()
    plt.show()

# Contenedor principal de controles en la interfaz
frame_controles = ctk.CTkFrame(app)
frame_controles.pack(pady=20, padx=20, fill="both", expand=True)

# Botón para cargar un archivo de audio
btn_cargar = ctk.CTkButton(
    frame_controles, fg_color="#B3E5FC", text_color="black",
    text="Cargar Archivo", command=cargar_audio  # Llama a la función que abre el explorador de archivos
)
btn_cargar.pack(pady=5)

# Contenedor para la selección de filtros de audio
frame_filtro = ctk.CTkFrame(frame_controles)
frame_filtro.pack(pady=5)

# Etiqueta de selección de filtro
filtrotxt = ctk.CTkLabel(frame_filtro, text="Seleccione Filtro:")
filtrotxt.pack(side="left", padx=10)

# Menú desplegable para filtros con selección inicial "Pasa-bajas"
filtro_var = ctk.StringVar(value="Pasa-bajas")
filtro_var.trace("w", actualizar_deslizadores)  # Llama a la función que ajusta los controles dinámicamente
menu_filtro = ctk.CTkComboBox(
    frame_filtro, variable=filtro_var,
    values=["Pasa-bajas", "Pasa-altas", "Pasa-banda"]  # Opciones disponibles para aplicar diferentes filtros
)
menu_filtro.pack(side="right", padx=10)

# Contenedor para controles de frecuencia de corte
frame_frecuencia = ctk.CTkFrame(frame_controles)
frame_frecuencia.pack(pady=5, fill="x")

# Etiqueta indicando la frecuencia de corte
label_titulo = ctk.CTkLabel(frame_frecuencia, text="Frecuencia de corte (Hz):")
label_titulo.grid(row=0, column=0, padx=10)

# Deslizador para frecuencia de corte mínima
slider_cutoff = ctk.CTkSlider(
    frame_frecuencia, fg_color="#E0F7FA",
    from_=1, to=10000, command=actualizar_frecuencia  # Llama a la función que actualiza el valor mostrado
)
slider_cutoff.grid(row=0, column=1, padx=10)

# Etiqueta que muestra la frecuencia seleccionada en el deslizador
label_frecuencia = ctk.CTkLabel(frame_frecuencia, text="1 Hz")  # Inicializa con un valor mínimo
label_frecuencia.grid(row=0, column=2, padx=10)

# Deslizador y etiqueta para frecuencia de corte máxima en filtros pasa-banda
slider_cutoff_max = ctk.CTkSlider(
    frame_frecuencia, fg_color="#E0F7FA",
    from_=1, to=10000, command=actualizar_frecuencia_max  # Llama a la función para actualizar frecuencia máxima
)
label_frecuencia_max = ctk.CTkLabel(frame_frecuencia, text="1 Hz")  # Inicializa con el valor mínimo

# Campo de entrada para definir el orden del filtro con un valor predeterminado de 2
ctk.CTkLabel(frame_controles, text="Orden del Filtro:").pack()
entry_orden = ctk.CTkEntry(frame_controles)
entry_orden.insert(0, "2")  # Inserta el valor predeterminado para el orden del filtro
entry_orden.pack(pady=5)

# Contenedor de botones para aplicar el filtro y guardar el archivo procesado
frame_botones = ctk.CTkFrame(frame_controles)
frame_botones.pack(pady=5)

# Botón para aplicar el filtro al audio cargado
btn_filtro = ctk.CTkButton(
    frame_botones, fg_color="#B3E5FC", text_color="black",
    text="Aplicar Filtro", command=aplicar_filtro  # Ejecuta la función que procesa el audio con el filtro seleccionado
)
btn_filtro.pack(side="left", padx=10)

# Botón para guardar el archivo de audio procesado
btn_guardar = ctk.CTkButton(
    frame_botones, fg_color="#B3E5FC", text_color="black",
    text="Guardar Archivo", command=guardar_archivo  # Llama a la función para guardar el archivo filtrado
)
btn_guardar.pack(side="right", padx=10)

# Ejecutar la ventana principal de la aplicación
app.mainloop()