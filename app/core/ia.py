from tensorflow.keras.models import load_model

modelo = load_model(
    "app/models/modelo_final.keras",
    compile=False
)