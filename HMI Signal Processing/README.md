"""
# Manual de Usuario: HMI para Procesamiento de Señales

## 📌 Descripción del Proyecto
Este programa es una **Interfaz Gráfica de Usuario (GUI)** desarrollada con **CustomTkinter**, que permite el procesamiento de señales de audio utilizando filtros digitales. 
Incluye opciones para **cargar archivos de audio**, **aplicar filtros**, **visualizar resultados** y **guardar archivos procesados**.

## 💻 Requisitos del Sistema
Antes de ejecutar el programa, asegúrate de contar con:
- **Python 3.8+** instalado en tu sistema.
- Las siguientes bibliotecas instaladas:

pip install customtkinter librosa numpy matplotlib soundfile


## 🔧 Instalación
1. **Clona** o **descarga** el código fuente en tu máquina.
2. **Instala las dependencias** con el comando anterior.
3. **Ejecuta el script** en tu entorno de desarrollo con:

python HMI_SP.py 



## 🎛 Interfaz y Funcionalidades
"""

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

"""
### 🟢 Carga de Archivos
- Pulsa el botón **"Cargar Archivo"** para seleccionar un archivo de audio (`.wav`, `.mp3`, `.aac`).
- Recibirás una confirmación de que el archivo ha sido cargado correctamente.
"""

def cargar_audio():
 """Permite al usuario cargar un archivo de audio desde su sistema."""
 filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.aac")])
 if filepath:  
     global audio, sample_rate
     audio, sample_rate = librosa.load(filepath, sr=None)  # Cargar el archivo de audio
     messagebox.showinfo("Archivo cargado", f"Se ha cargado el archivo: {filepath}")  # Notificación de éxito

"""
### 🎚 Selección de Filtros
- En el **menú desplegable**, elige entre:
- **Pasa-bajas:** Permite el paso de frecuencias bajas y elimina las altas.
- **Pasa-altas:** Permite el paso de frecuencias altas y elimina las bajas.
- **Pasa-banda:** Permite solo un rango específico de frecuencias.
- Ajusta los **deslizadores** para definir la frecuencia de corte.
"""

# Contenedor para selección de filtro
frame_filtro = ctk.CTkFrame(app)
frame_filtro.pack(pady=5)

# Etiqueta de selección de filtro
filtrotxt = ctk.CTkLabel(frame_filtro, text="Seleccione Filtro:")
filtrotxt.pack(side="left", padx=10)

# Menú desplegable para filtros con selección inicial "Pasa-bajas"
filtro_var = ctk.StringVar(value="Pasa-bajas")
filtro_var.trace("w", lambda *args: None)  # Se actualizan controles dinámicamente
menu_filtro = ctk.CTkComboBox(frame_filtro, variable=filtro_var, values=["Pasa-bajas", "Pasa-altas", "Pasa-banda"])
menu_filtro.pack(side="right", padx=10)

"""
### 🔎 Aplicación de Filtros
- Después de seleccionar el filtro y ajustar la frecuencia:
- Pulsa **"Aplicar Filtro"** para procesar la señal de audio.
- Se generarán **gráficos** mostrando la señal original, filtrada y sus transformadas de Fourier.
"""

def aplicar_filtro():
 """Aplica el filtro seleccionado al archivo de audio cargado y muestra los gráficos."""
 if 'audio' not in globals():  # Validar que haya un archivo cargado
     messagebox.showerror("Error", "Primero carga un archivo de audio.")
     return

 # Configuración inicial del filtro
 tipo = filtro_var.get()  
 order = 2
 nyquist = 0.5 * sample_rate  

 global audio_filtrado  
 if tipo == "Pasa-bajas":
     cutoff = 1000  
     normal_cutoff = cutoff / nyquist  
     audio_filtrado = funcionesFiltros.filtro_pasa_bajas(audio, normal_cutoff, n=order)
 elif tipo == "Pasa-altas":
     cutoff = 1000  
     normal_cutoff = cutoff / nyquist  
     audio_filtrado = funcionesFiltros.filtro_pasa_altas(audio, normal_cutoff, n=order)
 elif tipo == "Pasa-banda":
     cutoff_min = 500  
     cutoff_max = 2000  
     normal_cutoff_min = cutoff_min / nyquist  
     normal_cutoff_max = cutoff_max / nyquist  
     audio_filtrado = funcionesFiltros.filtro_pasa_banda(audio, normal_cutoff_min, normal_cutoff_max, n=order)
 else:
     messagebox.showerror("Error", "Filtro no reconocido")
     return

"""
### 💾 Guardar Archivo
- Una vez filtrado el audio, usa **"Guardar Archivo"** para exportarlo en formato **`.wav`**.
- Se abrirá un cuadro de diálogo para elegir la ubicación donde guardar el archivo.
"""

def guardar_archivo():
 """Permite guardar el archivo de audio filtrado en formato WAV."""
 if 'audio_filtrado' in globals():  
     save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAV", "*.wav")])
     if save_path:  
         sf.write(save_path, audio_filtrado, sample_rate)  
         messagebox.showinfo("Archivo guardado", f"Archivo guardado en: {save_path}")  
 else:
     messagebox.showerror("Error", "No hay archivo filtrado para guardar.")  

"""
## 📊 Visualización Gráfica
El programa genera cuatro gráficos:
1. **Señal original en el tiempo.**
2. **Señal filtrada según el tipo de filtro seleccionado.**
3. **Transformada de Fourier de la señal original.**
4. **Transformada de Fourier de la señal filtrada.**
"""

# Ejecutar la ventana principal de la aplicación
app.mainloop()