import cv2
import numpy as np

from app.core.ia import modelo

def procesar_imagen(imagen):

    alto_original, ancho_original = imagen.shape[:2]  # <-- guardamos tamaño real

    img = cv2.resize(imagen, (512, 512))

    entrada = np.expand_dims(img / 255.0, axis=0)

    pred = modelo.predict(entrada, verbose=0)[0].squeeze()

    sensibilidad = 0.80

    mask = (pred > sensibilidad).astype(np.uint8)

    kernel = np.ones((5,5), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    final_mask = np.zeros_like(mask)

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for cnt in contours:
        if cv2.contourArea(cnt) > 400:
            cv2.drawContours(
                final_mask,
                [cnt],
                -1,
                1,
                thickness=cv2.FILLED
            )

    porcentaje = (np.sum(final_mask)/(512*512))*100

    if porcentaje > 0.4:
        diagnostico = "EL PACIENTE TIENE CARIES"
    else:
        diagnostico = "EL PACIENTE NO TIENE CARIES"

    overlay = img.copy()

    overlay[final_mask == 1] = (0,0,255)

    resultado = cv2.addWeighted(img,0.7,overlay,0.3,0)

    # Regresamos la imagen resultado al tamaño original con el que llegó
    resultado = cv2.resize(resultado, (ancho_original, alto_original))

    return resultado, diagnostico, porcentaje