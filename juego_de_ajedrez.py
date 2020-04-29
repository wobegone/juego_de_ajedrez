#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
import tablero
import ajedrez_parser

class Juego_de_ajedrez():
    filas = 8
    columnas = 8
    color1 = "#DDB88C"    #es la casilla blanca
    color2 = "#A66D4F"    #es la casilla oscura
    sombra_color1 = "#696969"
    sombra_color2 = "#A9A9A9"
    color_casillas_tablero = {}
    dim_casilla = 48  #64
    imagenes = {}
    posibles_jugadas = []
    #para ejecutar los movimientos
    casilla_origen = None
    casilla_destino = None
    
    
    def __init__(self, raiz, posicion):
        self.raiz = raiz
        self.tablero = posicion

        canvas_width = self.columnas * self.dim_casilla
        canvas_height = self.filas * self.dim_casilla
        #para hacer la pantalla de tamaño cambiante e incluir el tablero y una "caja de texto"

        buttonc1 = self.Button("Reset")
        buttonc1.show()
        tablec.attach(buttonc1, 1,3,11,12)
        buttonc1.connect("clicked", self.onReset)
        
        panes = PanedWindow(raiz, bg='grey', width=2.5*canvas_width)
        panes.pack()
        
        self.canvas = Canvas(panes, width=canvas_width, height=canvas_height)
        self.canvas.pack(padx=8, pady=8)
        self.dibuja_tablero()
        
        self.ventana_derecha = Canvas(panes, width=canvas_width, height=canvas_height)
        self.ventana_derecha.pack(padx=8, pady=8)
        
        #lbl = Label(self.right,text="Nc6", font=("ChessSansUscf", 16))
        lbl = Label(self.ventana_derecha,\
                text="Ventana de texto para las jugadas")
        lbl.bind("<Button-1>",lambda x: lbl.config(text="Texto cambiado"))
        lbl.grid(row=0, column=0, sticky=E)
        
        panes.add(self.canvas)
        panes.add(self.ventana_derecha)
        # Esto lo usaremos para mantener el rastro de una pieza(item) 
        # cuando se arrastre (drag)
        #self.canvas.config(scrollregion=self.canvas(ALL))
        self._drag_data = {"x": 0, "y": 0, "item": None}
        #print(21, juego.moves({ 'verbose': True }))  # nos muestra todas las jugadas posibles

    """
    Ahora, dibujamos las cuadriculas del tablero usando el método canvas.create_rectangle, 
    llenándolo alternando entre los dos colores que definimos anteriormente.
    
    Para dibujar cuadros en la tabla usamos el método canvas.create_rectangle (), 
    que dibuja un rectángulo con las coordenadas x, y de las dos esquinas diagonalmente opuestas del rectángulo 
    (coordenadas de los bordes superior izquierdo e inferior derecho).
    
    Necesitaremos apuntar al tablero. 
    Por lo tanto, agregamos una etiqueta denominada - area - a cada uno de los cuadrados creados en el tablero. 
    
    """
    def dibuja_tablero(self):
        self.canvas.delete("area")
        color = self.color1
        for r in range(self.filas):
            color = self.color1 if color == self.color2 else self.color2 
            num_casilla = str(r+1)
            for c in range(self.columnas):
                letra_casilla = chr(97 + c)
                x1 = (c * self.dim_casilla)
                y1 = ((7-r) * self.dim_casilla)
                x2 = x1 + self.dim_casilla
                y2 = y1 + self.dim_casilla
                # x1 y y1 es el vertice superior izquierdo
                # x2 e y2 es el vertice inferior derecho
                id_casilla = str(x1) + '-' + str(y1) + '-' + str(x2) + '-' + str(y2)
                
                self.canvas.create_rectangle(x1, y1, x2, y2,  fill=color, tags=(id_casilla,"area"))
                color = self.color1 if color == self.color2 else self.color2
                color_sombreado = None
                if color == self.color1 :
                    color_sombreado = self.sombra_color1
                else:
                    color_sombreado = self.sombra_color2
                estruct_casilla = {'color_sin_sombra': color, 'color_con_sombra': color_sombreado, 
                                'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}
                self.color_casillas_tablero[letra_casilla + num_casilla] = estruct_casilla

                
    # dibujamos las piezas en la posicion FEN de chessboard          
    def dibuja_piezas(self): # new method defined here
        self.canvas.delete("ocupada")
        #for xycoord, piece in self.chessboard.iteritems(): # iterates through the chess board instance created above in the __init__ method
        for xycoord, valor in self.tablero.items():
            #sacamos las coordenadas de cada casilla : c8 será --> 7,2 ; a8 --> 7,0 y asi sucesivamente
            x,y = self.tablero.num_notacion(xycoord)
            if valor is not None:
                nom_fichero = "./piezas/%s%s.png" % (valor['color'], valor['type'])
                if valor['color'] == 'w' :
                    nom_pieza = "%s%s%s" % (valor['type'].upper(), x, y)
                else:
                    nom_pieza = "%s%s%s" % (valor['type'], x, y)
                if(nom_fichero not in self.imagenes):
                    self.imagenes[nom_fichero] = PhotoImage(file=nom_fichero)
                self.obj_imagen = self.canvas.create_image(0,0, image=self.imagenes[nom_fichero], tags=(nom_pieza, "ocupada"), anchor="c")            
                x0 = (y * self.dim_casilla) + int(self.dim_casilla/2)
                y0 = ((7-x) * self.dim_casilla) + int(self.dim_casilla/2)
                self.canvas.coords(nom_pieza, x0, y0)
                
                self.canvas.tag_bind(self.obj_imagen, "<Enter>", self.entra_mouse_over)
                #self.canvas.tag_bind(self.obj_imagen, "<Leave>", self.sale_mouse_over)
                #empezamos ahora el drag & drop
                #añadimos la ligazon del clic, arrastrar y soltar sobre
                #las imagenes con el tag "ocupada"
                self.canvas.tag_bind("ocupada", "<ButtonPress-1>", self.on_pieza_presionada)
                self.canvas.tag_bind("ocupada", "<ButtonRelease-1>", self.on_pieza_soltada)
                self.canvas.tag_bind("ocupada", "<B1-Motion>", self.on_pieza_moviendo)
                
    
    # empezamos el drag &drop de las piezas
    def on_pieza_presionada(self, event):
        '''Comienza el arrastre de una pieza'''
        #para averiguar la casilla de inicio
        col_tamano = fila_tamano = self.dim_casilla
        seleccionada_columna = event.x // col_tamano
        seleccionada_fila = 7 - (event.y // fila_tamano)
        pos = self.tablero.alfa_notacion((seleccionada_fila, seleccionada_columna))
        #averiguamos la pieza y color que esta en tablero[pos] --> pos es la casilla b8, c7, etc.
        #si el turno (w o b) coincide con el color de la pieza, iniciamos el movimiento
        if pos in self.tablero:
            if juego.turno() != self.tablero[pos]['color']:
                self.casilla_origen = None
            else:
                self.casilla_origen = pos
        else:
            self.casilla_origen = None
        #registramos el tema y su localizacion
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


    def on_pieza_soltada(self, event):
        '''Final del arrastre de la pieza'''
        # reseteamos la informacion del arrastre
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        #ahora obtenemos la casilla destino
        col_tamano = fila_tamano = self.dim_casilla
        seleccionada_columna = event.x // col_tamano
        seleccionada_fila = 7 - (event.y // fila_tamano)
        self.casilla_destino = self.tablero.alfa_notacion((seleccionada_fila, seleccionada_columna))
        movimiento = juego.move({ 'from': self.casilla_origen, 'to': self.casilla_destino, 'promotion': 'q' })
        if movimiento:
            promocion = movimiento['promotion']
            pieza = movimiento['piece']
            san = movimiento['san']
            color = movimiento['color']
            flags = movimiento['flags']
            """
            El campo flags puede contener uno o mas de los valores siguientes:
            - 'n' - a non-capture
            - 'b' - a pawn push of two squares
            - 'e' - an en passant capture
            - 'c' - a standard capture
            - 'p' - a promotion
            - 'k' - kingside castling
            - 'q' - queenside castling
            """
            # O-O
            #ahora vamos a arreglar el tablero interno
            # este primer del es para borrar la pieza de la casilla origen. Ocurre siempre
            del self.tablero[self.casilla_origen]   # borramos la pieza en el tablero interno
            #ahora vamos con los enroques
            if 'k' in movimiento['flags']:
                if movimiento['color'] == 'w':
                    del self.tablero['h1']
                elif movimiento['color'] == 'b':
                    del self.tablero['h8']
            if 'q' in movimiento['flags']:
                if movimiento['color'] == 'w':
                    del self.tablero['a1']
                elif movimiento['color'] == 'b':
                    del self.tablero['a8']
            #ahora vamos con la captura al paso
            if 'e' in flags:
                if movimiento['color'] == 'w': 
                   numero = int(movimiento['to'][1]) - 1
                   numstr = str(numero)
                   casilla_a_borrar = movimiento['to'][0] + numstr
                   del self.tablero[casilla_a_borrar]
                elif movimiento['color'] == 'b':
                   numero = int(movimiento['to'][1]) + 1
                   numstr = str(numero)
                   casilla_a_borrar = movimiento['to'][0] + numstr
                   del self.tablero[casilla_a_borrar]
            self.tablero.procesa_notacion(juego.fen())
            self.dibuja_tablero()
            self.dibuja_piezas()
            
            #pyglet.font.add_file('./fuentes/ChessSansUscf.ttf') --> se tiene que poner en directorio de SO
            #fuente_ajedrez = pyglet.font.load('ChessSansUscf')
            depositLabel = Message(self.ventana_derecha, text = juego.pgn(), width=300, padx=2, justify=LEFT) #, font_name='ChessSansUscf')            
            depositLabel.grid(column=0, row=0)

        else:
            self.dibuja_tablero()
            self.dibuja_piezas()
        
        

    def on_pieza_moviendo(self, event):
        '''Maneja el arrastre de la pieza'''
        if self.casilla_origen == None:
            # reseteo la información del drag
            self._drag_data["item"] = None
            self._drag_data["x"] = 0
            self._drag_data["y"] = 0
        else:
            # calcula cuanto se ha movido el raton
            delta_x = event.x - self._drag_data["x"]
            delta_y = event.y - self._drag_data["y"]
            # muevo el objeto la distancia adecuada
            self.canvas.move(self._drag_data["item"], delta_x, delta_y)
            # guardo la posicion nueva
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
    
    
    # -----------------terminamos el drag & drop de las piezas -------
    
    
    # ----------- eventos del raton on/out over------------------------
    def pieza_esta_raton(self, coord_x, coord_y):
        col_tamano = fila_tamano = self.dim_casilla
        seleccionada_columna = coord_x // col_tamano
        seleccionada_fila = 7 - (coord_y // fila_tamano)
        pos = self.tablero.alfa_notacion((seleccionada_fila, seleccionada_columna))
        
        try:
            posibles_destinos = []
            for i in juego.moves({ 'verbose': True }):
                if i['from'] == pos:
                    posibles_destinos.append(i)
            return(posibles_destinos)
        except:
            pass
            
            
    def entra_mouse_over(self, event):
        def casillas_grises(casilla):
            x1 = self.color_casillas_tablero[casilla]['x1']
            y1 = self.color_casillas_tablero[casilla]['y1']
            x2 = self.color_casillas_tablero[casilla]['x2']
            y2 = self.color_casillas_tablero[casilla]['y2']
            color = self.color_casillas_tablero[casilla]['color_con_sombra']
            #self.canvas.create_rectangle(x1, y1, x2, y2,  fill=color, tags="area")
            id_casilla = str(x1) + '-' + str(y1) + '-' + str(x2) + '-' + str(y2)
            self.canvas.itemconfig(id_casilla,  fill=color)
            #hemos quitado la pieza y ahora la ponemos
            
            x,y = self.tablero.num_notacion(self.posibles_jugadas[0]['from'])
            nom_fichero = "./piezas/%s%s.png" % (self.posibles_jugadas[0]['color'], self.posibles_jugadas[0]['piece'])
            if self.posibles_jugadas[0]['color'] == 'w' :
                nom_pieza = "%s%s%s" % (self.posibles_jugadas[0]['piece'].upper(), x, y)
            else:
                nom_pieza = "%s%s%s" % (self.posibles_jugadas[0]['piece'], x, y)
            self.canvas.delete(nom_pieza)
            if(nom_fichero not in self.imagenes):
                self.imagenes[nom_fichero] = PhotoImage(file=nom_fichero)
            self.obj_imagen = self.canvas.create_image(0,0, image=self.imagenes[nom_fichero], tags=(nom_pieza, "ocupada"), anchor="c")
            x0 = (y * self.dim_casilla) + int(self.dim_casilla/2)
            y0 = ((7-x) * self.dim_casilla) + int(self.dim_casilla/2)
            self.canvas.coords(nom_pieza, x0, y0)
            
        self.posibles_jugadas = self.pieza_esta_raton(event.x, event.y)
        if len(self.posibles_jugadas) > 0 :
            origen = self.posibles_jugadas[0]['from']
            casillas_grises(origen)
            for i in range(len(self.posibles_jugadas)):
                casillas_grises(self.posibles_jugadas[i]['to'])
            self.canvas.tag_bind(self.obj_imagen, "<Leave>", self.sale_mouse_over)
                    

    def sale_mouse_over(self, event):
        self.dibuja_tablero()
        self.dibuja_piezas()
        
    #---------------------------- fin de raton on/out over ------------------

    
                    
                    


def inicia_programa(posic_tablero):
    root = Tk()
    root.title("Juego_de_ajedrez")
    gui = Juego_de_ajedrez(root, posic_tablero)
    gui.dibuja_tablero()
    gui.dibuja_piezas()
    root.mainloop()


if __name__ == "__main__":
    #primero la posición inicial del tablero
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    # inicio el validador de jugadas con la posición inicial
    juego = ajedrez_parser.Chess(fen)
    if not juego:
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    # inicio el tablero interno grafico. El real se controla con ajedrez_parser
    partida = tablero.TableroAjedrez(fen, juego)
    inicia_programa(partida)
