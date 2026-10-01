import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.core.ia import modelo


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/predict",
    tags=["Predicción"]
)


# ============================================================
# PROCESAR IMAGEN
# ============================================================

def procesar_imagen(imagen):
    """
    Procesa una radiografía dental utilizando el modelo U-Net con umbrales
    personalizados por clase.

    Entrada del modelo:
        (1, 256, 256, 1)

    Clases:
        0 = Healthy / fondo
        1 = Caries (Umbral: >= 0.90)
        2 = Infección (Umbral: >= 0.50)
        3 = Muela del juicio / diente impactado (Umbral: >= 0.50)

    Retorna:
        resultado, diagnostico, porcentaje
    """

    # ========================================================
    # 1. Guardar tamaño original
    # ========================================================
    alto_original, ancho_original = imagen.shape[:2]

    # ========================================================
    # 2. Convertir a escala de grises
    # ========================================================
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # ========================================================
    # 3. Redimensionar a 256x256
    # ========================================================
    entrada = cv2.resize(
        gris,
        (256, 256),
        interpolation=cv2.INTER_AREA
    )

    # ========================================================
    # 4. Normalizar
    # ========================================================
    entrada = entrada.astype(np.float32) / 255.0

    # ========================================================
    # 5. Agregar canal (256x256 -> 256x256x1)
    # ========================================================
    entrada = np.expand_dims(entrada, axis=-1)

    # ========================================================
    # 6. Agregar batch (256x256x1 -> 1x256x256x1)
    # ========================================================
    entrada = np.expand_dims(entrada, axis=0)

    print("Forma de entrada al modelo:", entrada.shape)

    # ========================================================
    # 7. Predicción
    # ========================================================
    prediccion = modelo.predict(entrada, verbose=0)[0]

    print("Forma de salida del modelo:", prediccion.shape)

    # ========================================================
    # 8. Obtener clase de cada píxel con umbrales personalizados
    # ========================================================
    # Umbrales mínimos de confianza requeridos por clase:
    UMBRAL_CARIES = 0.90     # Exige >= 90% de certeza para caries
    UMBRAL_INFECCION = 0.50  # 50% para infección
    UMBRAL_MUELA = 0.50      # 50% para muela del juicio

    if prediccion.ndim == 3:
        # Inicializar la máscara en 0 (Healthy / Fondo)
        mascara = np.zeros(prediccion.shape[:2], dtype=np.uint8)

        # Probabilidades por canal
        prob_caries = prediccion[:, :, 1]
        prob_infeccion = prediccion[:, :, 2]
        prob_muela = prediccion[:, :, 3]

        # Asignación por condición de umbral
        mascara[prob_muela >= UMBRAL_MUELA] = 3
        mascara[prob_infeccion >= UMBRAL_INFECCION] = 2
        mascara[prob_caries >= UMBRAL_CARIES] = 1

    else:
        # En caso de salida binaria (2D)
        mascara = (prediccion >= UMBRAL_CARIES).astype(np.uint8)

    # ========================================================
    # 9. Regresar máscara al tamaño original
    # ========================================================
    mascara = cv2.resize(
        mascara,
        (ancho_original, alto_original),
        interpolation=cv2.INTER_NEAREST
    )

    # ========================================================
    # 10. Copiar imagen original
    # ========================================================
    resultado = imagen.copy()

    # ========================================================
    # 11. Calcular píxeles de cada clase
    # ========================================================
    total_pixeles = mascara.shape[0] * mascara.shape[1]

    pixeles_caries = np.sum(mascara == 1)
    pixeles_infeccion = np.sum(mascara == 2)
    pixeles_muela = np.sum(mascara == 3)

    # ========================================================
    # 12. Calcular porcentajes sobre el área total
    # ========================================================
    porcentaje_caries = (pixeles_caries / total_pixeles) * 100
    porcentaje_infeccion = (pixeles_infeccion / total_pixeles) * 100
    porcentaje_muela = (pixeles_muela / total_pixeles) * 100

    # ========================================================
    # 13. Determinar diagnóstico principal
    # ========================================================
    porcentajes = {
        "Caries": porcentaje_caries,
        "Infección": porcentaje_infeccion,
        "Muela del juicio": porcentaje_muela
    }

    diagnostico = max(porcentajes, key=porcentajes.get)
    porcentaje = porcentajes[diagnostico]

    # ========================================================
    # Si no hay ninguna detección que supere los umbrales
    # ========================================================
    if porcentaje == 0:
        diagnostico = "Healthy"
        porcentaje = (np.sum(mascara == 0) / total_pixeles) * 100

    # ========================================================
    # 14. Crear overlay
    # ========================================================
    overlay = resultado.copy()

    # Clase 1 = CARIES (BGR: Rojo)
    overlay[mascara == 1] = (0, 0, 255)

    # Clase 2 = INFECCIÓN (BGR: Verde)
    overlay[mascara == 2] = (0, 255, 0)

    # Clase 3 = MUELA DEL JUICIO (BGR: Azul)
    overlay[mascara == 3] = (255, 0, 0)

    # ========================================================
    # 15. Combinar imagen original + overlay
    # ========================================================
    resultado = cv2.addWeighted(
        resultado,
        0.7,
        overlay,
        0.3,
        0
    )

    # ========================================================
    # 16. Retornar resultado
    # ========================================================
    return resultado, diagnostico, porcentaje


# ============================================================
# ENDPOINT /predict
# ============================================================

@router.post("/")
async def predict(file: UploadFile = File(...)):
    # ========================================================
    # 1. Verificar tipo de archivo
    # ========================================================
    tipos_permitidos = ["image/jpeg", "image/jpg", "image/png"]

    if file.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen JPG, JPEG o PNG."
        )

    # ========================================================
    # 2. Leer archivo
    # ========================================================
    contenido = await file.read()

    if not contenido:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío."
        )

    # ========================================================
    # 3. Convertir bytes a imagen OpenCV
    # ========================================================
    datos = np.frombuffer(contenido, np.uint8)
    imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)

    if imagen is None:
        raise HTTPException(
            status_code=400,
            detail="No se pudo leer la imagen."
        )

    # ========================================================
    # 4. Procesar imagen
    # ========================================================
    try:
        resultado, diagnostico, porcentaje = procesar_imagen(imagen)
    except Exception as e:
        print("Error procesando imagen:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la imagen: {str(e)}"
        )

    # ========================================================
    # 5. Convertir resultado a JPG
    # ========================================================
    exitoso, buffer = cv2.imencode(".jpg", resultado)

    if not exitoso:
        raise HTTPException(
            status_code=500,
            detail="No se pudo generar la imagen procesada."
        )

    # ========================================================
    # 6. Preparar respuesta StreamingResponse
    # ========================================================
    imagen_bytes = buffer.tobytes()

    response = StreamingResponse(
        BytesIO(imagen_bytes),
        media_type="image/jpeg"
    )

    # ========================================================
    # 7. Enviar diagnóstico mediante headers
    # ========================================================
    response.headers["X-Diagnostico"] = diagnostico
    response.headers["X-Porcentaje"] = str(round(porcentaje, 2))

    return response