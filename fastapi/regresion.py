import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

def gradientDescent(x, y, alfa, numIter):    
    m, n = np.shape(x)    
    xTrans = x.transpose()    
    theta = np.zeros(n)    
    for i in range(0, numIter):        
        hipotesis = np.dot(x, theta)        
        dif = hipotesis - y       
        costo = np.sum(dif ** 2) / (2 * m) 
        gradiente = np.dot(xTrans, dif) / m
        ant_theta = theta 
        theta = theta - alfa * gradiente        
        if np.all(np.abs(ant_theta-theta)<0.0000001): break        
        if i%10000==0:            
            print("Iter: %d | Costo: %f" % (i,costo))    
    
    print("Iter: %d | Costo: %f" % (i,costo))    
    
    return theta

puntos = pd.read_csv("../pesos_y_alturas.csv")
x1=puntos['Sexo'].values=='Masculino'
x2=puntos['Altura'].values
y=puntos['Peso'].values
m=np.size(x1)
x=np.c_[np.ones(m), x1, x2]
m, n = np.shape(x)
numIter= 1000000
alfa = .4
theta = gradientDescent(x, y, alfa, numIter)
print(theta)

import pickle

# Guardar el modelo en un archivo
with open("modelo_gradient_descent.pkl", "wb") as file:
    pickle.dump(theta, file)

print("Modelo guardado exitosamente en modelo_gradient_descent.pkl")
