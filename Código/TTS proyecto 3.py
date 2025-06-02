import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json

#configuración
ANCHO_TABLERO = 12
ALTO_TABLERO = 22
TAMANO_BLOQUE = 30
COLOR_FONDO = "#000000"
COLOR_BORDE = "#FFFFFF"
COLOR_OBSTACULO = "#555555"

COLORES_PIEZAS = [
    "#00FFFF",  # I
    "#FFFF00",  # O
    "#AA00FF",  # T
    "#FFA500",  # L
    "#0000FF",  # J
    "#00FF00",  # S
    "#FF0000"   # Z
]

#tetrominós
FORMAS_PIEZAS = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Variables globales del juego
tablero = []
pieza_actual = {}
siguiente_pieza = {}
puntaje = 0
nivel = 1
velocidad_caida = 800
jugador = ""
ranking = []
juego_activo = False
id_caida = None
"""
E:
S:
R:

"""
# Funciones del juego
def inicializar_tablero():
    global tablero
    tablero = []
    for fila in range(ALTO_TABLERO): #tablero
        tablero.append([])
        for columna in range(ANCHO_TABLERO): #bordes
            if columna == 0 or columna == ANCHO_TABLERO - 1:
                tablero[fila].append("+")
            elif fila == ALTO_TABLERO - 1:
                tablero[fila].append("+")
            else:
                tablero[fila].append(0)
    #agregar obstáculo central
    centro_x = ANCHO_TABLERO // 2
    centro_y = ALTO_TABLERO // 2
    tablero[centro_y][centro_x] = "+"
    tablero[centro_y+1][centro_x] = "+"
    tablero[centro_y-1][centro_x] = "+"
    tablero[centro_y][centro_x+1] = "+"
    tablero[centro_y][centro_x-1] = "+"
"""
E:
S:
R:
    
"""
def nueva_pieza():
    indice = random.randint(0, len(FORMAS_PIEZAS)-1)
    return {
        "forma": FORMAS_PIEZAS[indice],
        "color": COLORES_PIEZAS[indice],
        "x": ANCHO_TABLERO // 2 - len(FORMAS_PIEZAS[indice][0]) // 2,
        "y": 0
    }
"""
E:
S:
R:
    
"""
def rotar_pieza(pieza):
    if len(pieza["forma"][0]) == 2:
        return pieza["forma"]
    filas = len(pieza["forma"])
    columnas = len(pieza["forma"][0])
    rotada = [[pieza["forma"][f][c] for f in range(filas-1, -1, -1)] for c in range(columnas)]
    #guardar posición original
    x_original = pieza["x"]
    y_original = pieza["y"]
    forma_original = pieza["forma"]
    #ajuste por colision
    ajustes = [0, -1, 1, -2, 2] 
    for dx in ajustes:
        pieza["forma"] = rotada
        pieza["x"] = x_original + dx
        if not hay_colision(pieza):
            return rotada
        pieza["x"] = x_original
    pieza["forma"] = forma_original
    return forma_original
"""
E:
S:
R:
    
"""
def hay_colision(pieza, desplazamiento_x=0, desplazamiento_y=0):
    for f, fila in enumerate(pieza["forma"]):
        for c, celda in enumerate(fila):
            if celda:
                nueva_x = pieza["x"] + c + desplazamiento_x
                nueva_y = pieza["y"] + f + desplazamiento_y
                if (nueva_x < 0 or nueva_x >= ANCHO_TABLERO or nueva_y >= ALTO_TABLERO or (nueva_y >= 0 and tablero[nueva_y][nueva_x] != 0)):
                    return True
    return False
"""
E:
S:
R:
    
"""
def unir_pieza(pieza):
    for f, fila in enumerate(pieza["forma"]):
        for c, celda in enumerate(fila):
            if celda:
                tablero_y = pieza["y"] + f
                tablero_x = pieza["x"] + c
                if 0 <= tablero_y < ALTO_TABLERO and 0 <= tablero_x < ANCHO_TABLERO:
                    tablero[tablero_y][tablero_x] = 1
"""
E:
S:
R:
    
"""
def eliminar_lineas():
    global puntaje, nivel, velocidad_caida
    lineas_eliminadas = 0
    for f in range(ALTO_TABLERO-1):  # No verificar la última fila (borde)
        if all(celda == 1 or celda == "+" for celda in tablero[f][1:-1]):
            lineas_eliminadas += 1
            for f2 in range(f, 0, -1):
                tablero[f2] = tablero[f2-1][:]
            tablero[0] = ["+" if c == 0 or c == ANCHO_TABLERO-1 else 0 for c in range(ANCHO_TABLERO)]
    if lineas_eliminadas > 0:
        puntaje += lineas_eliminadas * 100
        etiqueta_puntaje.config(text=f"Puntaje: {puntaje}")
        #aumentar nivel
        nuevo_nivel = puntaje // 500 + 1
        if nuevo_nivel > nivel:
            nivel = nuevo_nivel
            etiqueta_nivel.config(text=f"Nivel: {nivel}")
            velocidad_caida = max(200, 800 - (nivel-1)*100)
            if id_caida:
                ventana.after_cancel(id_caida)
                caer_pieza()
    return lineas_eliminadas
"""
E:
S:
R:
    
"""
def dibujar_tablero():
    lienzo.delete("all")
    for f in range(ALTO_TABLERO):
        for c in range(ANCHO_TABLERO):
            x1 = c * TAMANO_BLOQUE
            y1 = f * TAMANO_BLOQUE
            x2 = x1 + TAMANO_BLOQUE
            y2 = y1 + TAMANO_BLOQUE
            if tablero[f][c] == "+":  # Bordes y obstáculos
                lienzo.create_rectangle(x1, y1, x2, y2, fill=COLOR_OBSTACULO, outline=COLOR_BORDE)
            elif tablero[f][c] == 1:  # Bloques colocados
                color_index = (f + c) % len(COLORES_PIEZAS)
                lienzo.create_rectangle(x1, y1, x2, y2, fill=COLORES_PIEZAS[color_index], outline=COLOR_BORDE)
"""
E:
S:
R:
    
"""
def dibujar_pieza_actual():
    for f, fila in enumerate(pieza_actual["forma"]):
        for c, celda in enumerate(fila):
            if celda:
                x1 = (pieza_actual["x"] + c) * TAMANO_BLOQUE
                y1 = (pieza_actual["y"] + f) * TAMANO_BLOQUE
                x2 = x1 + TAMANO_BLOQUE
                y2 = y1 + TAMANO_BLOQUE
                lienzo.create_rectangle(x1, y1, x2, y2, fill=pieza_actual["color"], outline=COLOR_BORDE)
"""
E:
S:
R:
    
"""
def dibujar_siguiente_pieza():
    lienzo_siguiente.delete("all")
    for f, fila in enumerate(siguiente_pieza["forma"]):
        for c, celda in enumerate(fila):
            if celda:
                margen_x = (4 - len(siguiente_pieza["forma"][0])) * TAMANO_BLOQUE // 2
                margen_y = (4 - len(siguiente_pieza["forma"])) * TAMANO_BLOQUE // 2
                x1 = c * TAMANO_BLOQUE + margen_x
                y1 = f * TAMANO_BLOQUE + margen_y
                x2 = x1 + TAMANO_BLOQUE
                y2 = y1 + TAMANO_BLOQUE
                lienzo_siguiente.create_rectangle(x1, y1, x2, y2, fill=siguiente_pieza["color"], outline=COLOR_BORDE)
"""
E:
S:
R:
    
"""
def caer_pieza():
    global pieza_actual, siguiente_pieza, id_caida, juego_activo
    
    if not hay_colision(pieza_actual, 0, 1):
        pieza_actual["y"] += 1
    else:
        unir_pieza(pieza_actual)
        lineas = eliminar_lineas()
        
        pieza_actual = siguiente_pieza
        siguiente_pieza = nueva_pieza()
        dibujar_siguiente_pieza()
        
        if hay_colision(pieza_actual):
            juego_activo = False
            guardar_puntaje()
            mostrar_ranking()
            lienzo.create_text(ANCHO_TABLERO*TAMANO_BLOQUE//2, ALTO_TABLERO*TAMANO_BLOQUE//2, 
                             text="¡FIN DEL JUEGO!", fill="red", font=("Arial", 24))
            return
    dibujar_tablero()
    dibujar_pieza_actual()
    if juego_activo:
        id_caida = ventana.after(velocidad_caida, caer_pieza)
"""
E:
S:
R:
    
"""
def mover_pieza(evento):
    global pieza_actual
    
    if not juego_activo:
        return
    if evento.keysym == "Left" and not hay_colision(pieza_actual, -1):
        pieza_actual["x"] -= 1
    elif evento.keysym == "Right" and not hay_colision(pieza_actual, 1):
        pieza_actual["x"] += 1
    elif evento.keysym == "Down" and not hay_colision(pieza_actual, 0, 1):
        pieza_actual["y"] += 1
    elif evento.keysym == "Up":
        pieza_actual["forma"] = rotar_pieza(pieza_actual)
    
    dibujar_tablero()
    dibujar_pieza_actual()
"""
E:
S:
R:
    
"""
def iniciar_juego(nuevo_jugador=False):
    global pieza_actual, siguiente_pieza, puntaje, nivel, velocidad_caida, juego_activo, jugador, id_caida
    
    if nuevo_jugador:
        jugador = simpledialog.askstring("Nombre", "Ingrese su nombre:")
        if not jugador:
            jugador = "Anónimo"
        marco_info.children["!label"].config(text=f"Jugador: {jugador}")
    if id_caida:
        ventana.after_cancel(id_caida)
    inicializar_tablero()
    pieza_actual = nueva_pieza()
    siguiente_pieza = nueva_pieza()
    puntaje = 0
    nivel = 1
    velocidad_caida = 800
    juego_activo = True
    
    #Actualiza_interfaz
    etiqueta_puntaje.config(text=f"Puntaje: {puntaje}")
    etiqueta_nivel.config(text=f"Nivel: {nivel}")
    dibujar_siguiente_pieza()
    dibujar_tablero()
    dibujar_pieza_actual()
    id_caida = ventana.after(velocidad_caida, caer_pieza)
"""
E:
S:
R:
    
"""
def guardar_puntaje():
    global ranking

    cargar_ranking()
    ranking.append({"jugador": jugador, "puntaje": puntaje})
    #puntaje
    ranking.sort(key=lambda x: x["puntaje"], reverse=True)
    ranking = ranking[:10]

    with open("ranking.json", "w") as archivo:
        json.dump(ranking, archivo)
    mostrar_ranking()
"""
E:
S:
R:
    
"""
def cargar_ranking():
    global ranking
    
    try:
        with open("ranking.json", "r") as archivo:
            ranking = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        ranking = []
"""
E:
S:
R:
    
"""
def mostrar_ranking():
    lista_ranking.delete(0, tk.END)
    for i, item in enumerate(ranking, 1):
        lista_ranking.insert(tk.END, f"{i}. {item['jugador']}: {item['puntaje']}")
"""
E:
S:
R:
    
"""
def guardar_juego():
    if not juego_activo:
        messagebox.showerror("Error", "No hay un juego activo para guardar")
        return
    
    estado = {
        "tablero": tablero,
        "pieza_actual": pieza_actual,
        "siguiente_pieza": siguiente_pieza,
        "puntaje": puntaje,
        "nivel": nivel,
        "velocidad_caida": velocidad_caida,
        "jugador": jugador
    }
    
    try:
        with open("partida_guardada.json", "w") as archivo:
            json.dump(estado, archivo)
        messagebox.showinfo("Éxito", "Juego guardado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el juego: {str(e)}")
"""
E:
S:
R:
    
"""
def cargar_juego():
    global tablero, pieza_actual, siguiente_pieza, puntaje, nivel, velocidad_caida, jugador, juego_activo, id_caida
    
    try:
        with open("partida_guardada.json", "r") as archivo:
            estado = json.load(archivo)
        
        # Cancelar movimiento automático anterior si existe
        if id_caida:
            ventana.after_cancel(id_caida)
        
        # Restaurar estado del juego
        tablero = estado["tablero"]
        pieza_actual = estado["pieza_actual"]
        siguiente_pieza = estado["siguiente_pieza"]
        puntaje = estado["puntaje"]
        nivel = estado["nivel"]
        velocidad_caida = estado["velocidad_caida"]
        jugador = estado["jugador"]
        juego_activo = True
        
        # Actualizar la interfaz
        marco_info.children["!label"].config(text=f"Jugador: {jugador}")
        etiqueta_puntaje.config(text=f"Puntaje: {puntaje}")
        etiqueta_nivel.config(text=f"Nivel: {nivel}")
        dibujar_siguiente_pieza()
        dibujar_tablero()
        dibujar_pieza_actual()
        
        # Reanudar el movimiento automático
        id_caida = ventana.after(velocidad_caida, caer_pieza)
        
        messagebox.showinfo("Éxito", "Juego cargado correctamente")
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontró un juego guardado")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el juego: {str(e)}")

#interfaz gráfica
ventana = tk.Tk()
ventana.title("Tetris - Proyecto Programado 2")
ventana.resizable(False, False)

#lienzo
lienzo = tk.Canvas(ventana, width=ANCHO_TABLERO*TAMANO_BLOQUE, 
                   height=ALTO_TABLERO*TAMANO_BLOQUE, bg=COLOR_FONDO)
lienzo.grid(row=0, column=0, padx=10, pady=10)

# Marco_informacion
marco_info = tk.Frame(ventana)
marco_info.grid(row=0, column=1, padx=10, pady=10, sticky="n")

#informacion
tk.Label(marco_info, text="Tetris", font=("Arial", 16)).pack(pady=5)
tk.Label(marco_info, text=f"Jugador: {jugador}", font=("Arial", 12)).pack()

etiqueta_puntaje = tk.Label(marco_info, text=f"Puntaje: {puntaje}", font=("Arial", 12))
etiqueta_puntaje.pack()

etiqueta_nivel = tk.Label(marco_info, text=f"Nivel: {nivel}", font=("Arial", 12))
etiqueta_nivel.pack()

tk.Label(marco_info, text="Siguiente pieza:", font=("Arial", 12)).pack(pady=(10,0))
lienzo_siguiente = tk.Canvas(marco_info, width=4*TAMANO_BLOQUE, height=4*TAMANO_BLOQUE, bg=COLOR_FONDO)
lienzo_siguiente.pack()

# Marco_ranking
marco_ranking = tk.Frame(marco_info)
marco_ranking.pack(pady=(20,0))
tk.Label(marco_ranking, text="Top 10", font=("Arial", 12)).pack()
lista_ranking = tk.Listbox(marco_ranking, height=10, width=25)
lista_ranking.pack()

#control de jeugo
marco_botones = tk.Frame(marco_info)
marco_botones.pack(pady=20)

boton_iniciar = tk.Button(marco_botones, text="Nuevo Juego", command=lambda: iniciar_juego(True))
boton_iniciar.pack(side="left", padx=5)

boton_guardar = tk.Button(marco_botones, text="Guardar", command=guardar_juego)
boton_guardar.pack(side="left", padx=5)

boton_cargar = tk.Button(marco_botones, text="Cargar", command=cargar_juego)
boton_cargar.pack(side="left", padx=5)

#Confi controles del teclado
ventana.bind("<Left>", mover_pieza)
ventana.bind("<Right>", mover_pieza)
ventana.bind("<Down>", mover_pieza)
ventana.bind("<Up>", mover_pieza)

#ranking al iniciar
cargar_ranking()
mostrar_ranking()

ventana.mainloop()