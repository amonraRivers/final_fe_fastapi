import json
import pickle

import mysql.connector
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Cargar el modelo desde el archivo
with open("modelo_gradient_descent.pkl", "rb") as file:
    theta = pickle.load(file)


# Definir la conexion a la base de datos mysql
def get_connection():
    host = "database-4.cpmuweq8mgcr.us-west-2.rds.amazonaws.com"
    user = "admin"
    password = "ramonawstest1"
    database = "finalRamon"
    return mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )


def get_stats():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT count(*), sum(prediction) ,max(prediction),min(prediction) FROM logs"
    )
    logs = cursor.fetchall()
    connection.close()
    return logs


def insert_log(request, prediction):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO logs (request, prediction) VALUES (%s, %s)", (request, prediction)
    )
    connection.commit()
    connection.close()


# Definir un modelo de entrada para la solicitud POST
class InputData(BaseModel):
    sexo: str  # "Masculino" o "Femenino"
    altura: float


@app.post("/predict")
def predict(data: InputData):
    """
    Predice el peso basado en el sexo y la altura.

    - `sexo`: "Masculino" o "Femenino"
    - `altura`: Altura de la persona en unidades adecuadas.
    """
    # Convertir sexo a una variable binaria
    x_sexo = 1 if data.sexo.lower() == "masculino" else 0

    # Crear el vector de entrada para la predicción
    x_input = np.array([1, x_sexo, data.altura])  # [1, sexo_binario, altura]

    # Calcular el peso predicho
    peso_predicho = np.dot(x_input, theta)

    # Insertar el log en la base de datos
    data_json = json.dumps(data.dict())
    insert_log(data_json, peso_predicho)

    return {"sexo": data.sexo, "altura": data.altura, "peso_predicho": peso_predicho}


@app.get("/stats")
def stats():
    logs = get_stats()
    response = {
        "total_requests": logs[0][0],
        "mean_prediction": logs[0][1] / logs[0][0],
        "max_prediction": logs[0][2],
        "min_prediction": logs[0][3],
    }
    return json.dumps(response)
