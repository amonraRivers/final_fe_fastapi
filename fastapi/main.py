from fastapi import FastAPI

# Crear una instancia de FastAPI
app = FastAPI()

# Ruta de ejemplo
@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}

# Ruta con parámetro en la URL
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# Ruta para crear un nuevo ítem
@app.post("/items/")
def create_item(item: dict):
    return {"item_name": item["name"], "description": item["description"]}
