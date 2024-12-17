import json
import pickle

import mysql.connector
import numpy as np
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()

# Cargar el modelo desde el archivo
with open("model.pkl", "rb") as file:
    theta = pickle.load(file)


# Definir la conexion a la base de datos mysql
def get_connection():
    host = "database-4.cpmuweq8mgcr.us-west-2.rds.amazonaws.com"
    user = "admin"
    password = "ramonawstest1"
    database = "finalRamon"
    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS predictions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        CRIM FLOAT,
        ZN FLOAT,
        INDUS FLOAT,
        CHAS INT,
        NOX FLOAT,
        RM FLOAT,
        AGE FLOAT,
        DIS FLOAT,
        RAD FLOAT,
        TAX FLOAT,
        PTRATIO FLOAT,
        B FLOAT,
        LSTAT FLOAT,
        prediction FLOAT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""
    )
    conn.commit()
    return conn


def get_stats():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT count(*), sum(prediction) ,max(prediction),min(prediction) FROM predictions"
    )
    logs = cursor.fetchall()
    connection.close()
    return logs


def insert_log(request, prediction):
    connection = get_connection()
    cursor = connection.cursor()

    insert_query = """INSERT INTO predictions (CRIM, ZN, INDUS, CHAS, NOX, RM, AGE, DIS, RAD, TAX, PTRATIO, B, LSTAT, prediction)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""

    values = (
        request.crim,
        request.zn,
        request.indus,
        request.chas,
        request.nox,
        request.rm,
        request.age,
        request.dis,
        request.rad,
        request.tax,
        request.ptratio,
        request.b,
        request.lstat,
        prediction,
    )

    cursor.execute(insert_query, values)
    connection.commit()
    connection.close()


# Definir un modelo de entrada para la solicitud POST
class InputData(BaseModel):
    crim: float
    zn: float
    indus: float
    chas: int
    nox: float
    rm: float
    age: float
    dis: float
    rad: int
    tax: int
    ptratio: float
    b: float
    lstat: float


@app.post("/predict")
def predict(data: InputData):
    """
    Predice el peso basado en el sexo y la altura.

    """
    # extraer los valores de la solicitud

    # Crear el vector de entrada para la predicción
    x_input = np.array(
        [
            [
                data.crim,
                data.zn,
                data.indus,
                data.chas,
                data.nox,
                data.rm,
                data.age,
                data.dis,
                data.rad,
                data.tax,
                data.ptratio,
                data.b,
                data.lstat,
            ]
        ]
    )  # [1, ...]

    # Calcular el peso predicho

    peso_predicho = theta.predict(x_input).item()

    # Insertar el log en la base de datos
    print(peso_predicho)
    insert_log(data, peso_predicho)

    response = data.dict().copy()
    response["medv_predicho"] = peso_predicho

    return json.dumps(response)


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
