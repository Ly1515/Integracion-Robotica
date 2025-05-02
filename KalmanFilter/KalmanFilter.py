import cv2
import numpy as np

# ----- Funciones -----

# Inicializa y configura el filtro de Kalman para seguimiento.
def initialize_kalman():
    # Crea un filtro de Kalman con 4 estados (x, y, dx, dy) y 2 mediciones (x, y).
    kalman = cv2.KalmanFilter(4, 2)

    # Configura la matriz de medición para extraer las posiciones (x, y) del estado.
    kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                         [0, 1, 0, 0]], np.float32)

    # Configura la matriz de transición para actualizar la posición y velocidad.
    kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                        [0, 1, 0, 1],
                                        [0, 0, 1, 0],
                                        [0, 0, 0, 1]], np.float32)

    # Define la covarianza del ruido del proceso apara mayor suavidad.
    kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03

    # Define la covarianza del ruido de medición.
    kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1.0
    return kalman

# Mejora el brillo del cuadro usando la corrección gamma.
def preprocess_frame(frame):
    # Define el valor de gamma para ajustar la intensidad del brillo.
    gamma = 0.5

    # Crea una tabla de búsqueda (look-up table) para transformar la intensidad del brillo.
    look_up_table = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    frame = cv2.LUT(frame, look_up_table)
    return frame

# Detecta un objeto específico basado en un rango de color HSV.
def detect_object(frame):
    # Convierte el cuadro a espacio de color HSV.
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define el rango de colores para detectar el objeto.
    lower_hsv = np.array([5, 50, 50])
    upper_hsv = np.array([25, 200, 200])
    mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)

    # Reduce el ruido mediante un filtro de brillo y operaciones morfológicas.
    v_channel = hsv_frame[:, :, 2]
    _, brightness_mask = cv2.threshold(v_channel, 220, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.bitwise_and(mask, brightness_mask)
    mask = cv2.medianBlur(mask, 5)
    mask = cv2.dilate(mask, None, iterations=2)
    mask = cv2.erode(mask, None, iterations=1)

    # Encuentra contornos en la máscara procesada.
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Asegura que el objeto detectado cumple ciertos criterios de tamaño y proporción.
        if cv2.contourArea(largest_contour) > 800 and w / h < 2.0:
            return (x, y, w, h), mask
    return None, mask

# Detecta la silueta de un objeto usando detección de bordes.
def detect_silhouette(frame):
    # Convierte el cuadro a escala de grises.
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplica el detector de bordes Canny.
    edges = cv2.Canny(gray_frame, 70, 150)

    # Encuentra contornos en la imagen de bordes.
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Solo considera siluetas suficientemente grandes.
        if cv2.contourArea(largest_contour) > 800:
            return (x, y, w, h), edges
    return None, edges

# Inicializa un diccionario para asignar IDs únicos a cada perro.
dog_ids = {}
next_id = 1

# Calcula una distancia euclidiana para asociar perros detectados con IDs existentes.
def get_dog_id(center_x, center_y):
    global next_id
    # Busca un ID cercano en el diccionario basado en una distancia mínima.
    for dog_id, (prev_x, prev_y) in dog_ids.items():
        distance = np.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)
        if distance < 50:  # Umbral para considerar que es el mismo perro.
            dog_ids[dog_id] = (center_x, center_y)  # Actualiza la posición.
            return dog_id
    # Si no hay coincidencia, asigna un nuevo ID.
    dog_ids[next_id] = (center_x, center_y)
    next_id += 1
    return next_id - 1

# ----- Código principal -----

# Define la ruta del video.
video_path = "VideoFinalPerritos.mp4"
cap = cv2.VideoCapture(video_path)  # Carga el video.

# Inicializa el filtro de Kalman y la matriz de medición.
kalman = initialize_kalman()
measurement = np.zeros((2, 1), np.float32)

# Procesa cada cuadro del video.
while True:
    ret, frame = cap.read()  # Lee el siguiente cuadro.
    if not ret:
        break  # Termina si no hay más cuadros.

    frame = preprocess_frame(frame)  # Preprocesa el cuadro.

    # Intenta detectar el objeto basado en el color.
    detected_rect, mask = detect_object(frame)
    if detected_rect:
        # Si el objeto es detectado, realiza la corrección de Kalman.
        x, y, w, h = detected_rect
        center_x, center_y = x + w // 2, y + h // 2

        measurement[0] = center_x
        measurement[1] = center_y
        kalman.correct(measurement)  # Actualiza el estado.

        # Asigna un ID único al perro detectado.
        dog_id = get_dog_id(center_x, center_y)

        # Dibuja un rectángulo alrededor del objeto detectado.
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {dog_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        # Si no se detecta el objeto, intenta detectar la silueta.
        detected_silhouette, edges = detect_silhouette(frame)
        if detected_silhouette:
            # Realiza la corrección de Kalman basado en la silueta.
            x, y, w, h = detected_silhouette
            center_x, center_y = x + w // 2, y + h // 2

            measurement[0] = center_x
            measurement[1] = center_y
            kalman.correct(measurement)

            # Asigna un ID único a la silueta detectada.
            dog_id = get_dog_id(center_x, center_y)

            # Dibuja un rectángulo alrededor de la silueta detectada.
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, f"ID: {dog_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        else:
            # Si no se detecta nada, utiliza la predicción de Kalman.
            prediction = kalman.predict()
            predicted_x, predicted_y = int(prediction[0]), int(prediction[1])

            # Dibuja un rectángulo de predicción.
            pred_w, pred_h = 60, 60
            cv2.rectangle(frame, (predicted_x - pred_w // 2, predicted_y - pred_h // 2),
                          (predicted_x + pred_w // 2, predicted_y + pred_h // 2), (0, 255, 255), 2)

    # Muestra los cuadros procesados en diferentes ventanas.
    cv2.imshow('Seguimiento por Movimiento', frame)
    if detected_rect:
        cv2.imshow('Mascara HSV', mask)
    elif detected_silhouette:
        cv2.imshow('Bordes Silueta', edges)

    # Presiona 'q' para salir del bucle.
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()