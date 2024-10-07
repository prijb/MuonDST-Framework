# Definir valores iniciales y el incremento
A = 0
incremento = 10
B_maximo = 3825

# Crear una lista para almacenar las líneas
lineas = []

# Generar las líneas según las condiciones
while A + incremento <= B_maximo:
    B = A + incremento
    linea = f"nmin={A} nmax={B}"
    lineas.append(linea)
    A += incremento

# Escribir las líneas en un fichero
with open("output.txt", "w") as f:
    for linea in lineas:
        f.write(linea + "\n")

print("Fichero generado correctamente.")
