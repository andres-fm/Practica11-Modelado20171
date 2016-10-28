import sys
from PyQt4 import QtGui, uic, QtCore
from enum import Enum
from xmlrpc.server import SimpleXMLRPCServer
from random import randint


class MyWindow(QtGui.QMainWindow) :

	def __init__(self):
		super(MyWindow, self).__init__()
		self.vibora = Vibora()

		self.viboras = {"0" : self.vibora}
		self.ui = uic.loadUi('servidor.ui', self)		
		self.ui.table_board.keyPressEvent = self.keyPressEvent_board
		self.escucha_tamaño_tabla()
		self.timer_actualiza_juego = QtCore.QTimer(self)
		self.actualiza_espera()          
		self.timer_actualiza_juego.timeout.connect(self.actualizar_juego)
		self.timer_actualiza_juego.start()
		self.ui.spin_espera.valueChanged.connect(self.actualiza_espera)
		self.en_juego = False
		self.first_click = True
		self.timer_servidor = QtCore.QTimer(self)
		self.nuevo_id = self.new_id()
		self.ui.button_inicar_juego.clicked.connect(self.handle_boton_iniciar)	
		self.celdas_ocupadas = dict()
		for p in self.vibora.cuerpo:
			self.celdas_ocupadas[p] = "0"
		self.ui.button_iniciar_servidor.clicked.connect(self.iniciar_servidor)		

		self.show()
	
	def new_id(self):
		i = 1
		while True :
			yield str(i)
			i += 1

	def ping(self):
		return "¡Pong!"

	"""def nueva_vibora(self):
		posicion_correcta = False
		while not posicion_correcta:
			nueva_vibora = Vibora()
			x = 0#randint(0,int(self.ui.table_board.rowCount()-4))
			y = 0#randint(0,int(self.ui.table_board.columnCount()))
			nuevo_cuerpo = [(x,y),(x+1,y),(x+2,y),(x+3,y)]
			valido = True
			for c in nuevo_cuerpo:
				if c in self.celdas_ocupadas:
					valido = False
					break
			if valido:
				posicion_correcta = True
				nueva_vibora.identificador = self.nuevo_id.__next__()
				for a in cuerpo:
					self.celdas_ocupadas[a] = nueva_vibora.identificador
				nueva_vibora.cuerpo = nuevo_cuerpo				
				#(r, g, b) = self.color_aleatorio()
				#nueva_vibora.color = (r, g, b)
				return nueva_vibora"""

	def yo_juego(self):
		posicion_correcta = False
		while not posicion_correcta:
			nueva_vibora = Vibora()
			x = randint(0,int(self.ui.table_board.rowCount()-4))
			y = randint(0,int(self.ui.table_board.columnCount())-1)
			nuevo_cuerpo = [(x,y),(x+1,y),(x+2,y),(x+3,y)]
			valido = True
			for c in nuevo_cuerpo:
				if c in self.celdas_ocupadas:
					valido = False
					break
			if valido:
				posicion_correcta = True
				nueva_vibora.identificador = self.nuevo_id.__next__()
				for a in nuevo_cuerpo:
					if a != (x,y):
						self.celdas_ocupadas[a] = nueva_vibora.identificador
				nueva_vibora.cuerpo = nuevo_cuerpo				
				(r, g, b) = self.color_aleatorio()
				nueva_vibora.color = (r, g, b)
		self.viboras[nueva_vibora.identificador] = nueva_vibora
		diccionario = {"id": nueva_vibora.identificador, "color": {"r": r, "g": g, "b": b}}
		return diccionario

	def cambia_direccion(self, identificador, direccion):
		if identificador not in self.viboras:
			return
		self.viboras[identificador].modifica_direccion(direccion)
		return True

	def estado_del_juego(self):
		estado = {
			'espera' : self.timer_actualiza_juego.interval(),
			'tamY' : self.ui.table_board.columnCount(),
			'tamX' : self.ui.table_board.rowCount(),
			'viboras' : [{
				'id' : v.identificador,
				'camino' : v.cuerpo,
				'color' : {'r' : v.color[0], 'g' : v.color[1], 'b' : v.color[2]}
			} for v in self.viboras.values()]
		}
		return estado

	def iniciar_servidor(self):		
		puerto = int(self.ui.spin_puerto_servidor.text())
		url = self.ui.line_url.text()
		try:
			self.servidor = SimpleXMLRPCServer((url, puerto))
		except :
			print("url o puerto no disponibles. Intente de nuevo")
			return
		self.servidor.register_function(self.ping, "ping")
		self.servidor.register_function(self.yo_juego, "yo_juego")
		self.servidor.register_function(self.cambia_direccion, "cambia_direccion")
		self.servidor.register_function(self.estado_del_juego, "estado_del_juego")
		self.timer_servidor.timeout.connect(self.servidor.handle_request)
		self.timer_servidor.setInterval(0)
		self.servidor.timeout = float(self.ui.SpinBox_timeout.text())
		self.timer_servidor.start()
		puerto = self.servidor.server_address[1] 
		self.ui.spin_puerto_servidor.setValue(puerto) 
		self.ui.spin_puerto_servidor.setReadOnly(True) 
		self.ui.line_url.setReadOnly(True) 
		self.ui.SpinBox_timeout.setReadOnly(True) 
		self.button_iniciar_servidor.setEnabled(False)

	def color_aleatorio(self) :
		r = lambda: randint(0,255)
		return (r(), r(), r())

	def handle_boton_iniciar(self) :
		if not self.first_click  :
			return
		#self.vibora = Vibora()
		self.colorear_vibora("0",100,149,237)
		self.en_juego = True
		self.button_terminar_juego = QtGui.QPushButton('Terminar juego', self)
		self.button_terminar_juego.clicked.connect(self.terminar_juego)
		self.ui.gridLayout.addWidget(self.button_terminar_juego)
		self.ui.button_inicar_juego.setText("Pausar juego")
		self.ui.button_inicar_juego.clicked.connect(self.pausar_juego)
		self.first_click = False

	def colorear_vibora(self, idn, r, g, b) :
		for (x,y) in self.viboras[str(idn)].cuerpo : 
			self.colorear(x,y,r, g, b)

	def colorear(self, x, y, r, g, b) :
		if self.ui.table_board.item(x,y) == None :
			cell = QtGui.QTableWidgetItem()
			self.ui.table_board.setItem(x, y, cell)
		color = QtGui.QColor(r,g,b)
		try :
			self.ui.table_board.item(x,y).setBackground(QtGui.QBrush(color))
		except :
			#si hubo un error es porque el item en dicha posicion no existia (seguramente por mover cantidad de celdas)
			#No hacemos nada
			pass


	def descolorear(self, x, y) :
		self.colorear(x, y, 255, 255, 255)

	def pausar_juego(self) :
		self.timer_actualiza_juego.stop()
		self.en_juego = False
		self.ui.button_inicar_juego.setText("Reanudar juego")
		self.ui.button_inicar_juego.clicked.connect(self.reanudar_juego)

	def terminar_juego(self) :
		self.timer_actualiza_juego.stop()
		self.ui.button_inicar_juego.clicked.connect(self.deshabilita)		
		self.en_juego = False
		for idn in self.viboras:
			self.borrar_vibora(idn) 

	def borrar_vibora(self, idn) :
		self.colorear_vibora(idn, 255, 255, 255)


	def reanudar_juego(self) :
		self.timer_actualiza_juego.start()  
		self.en_juego = True
		self.ui.button_inicar_juego.setText("Pausar juego")
		self.ui.button_inicar_juego.clicked.connect(self.pausar_juego)

	def deshabilita(self):
		return

	def actualizar_juego(self) :
		if self.en_juego:
			try:
				for idn in self.viboras:
					self.mueve_serpiente(idn)
			except:
				pass
	def mueve_serpiente(self, idn) :
		if idn not in self.viboras:
			return
		(cola_x, cola_y) = self.viboras[str(idn)].cola
		self.descolorear(cola_x, cola_y)
		if (cola_x, cola_y) in self.celdas_ocupadas:
			del self.celdas_ocupadas[(cola_x, cola_y)]
		self.viboras[str(idn)].avanza()
		(cabeza_x, cabeza_y) = self.viboras[str(idn)].cabeza
		#si la nueva posicion de la cabeza estaba ocupada, la vibora que estaba ahi ahora esta muerta
		if (cabeza_x, cabeza_y) in self.celdas_ocupadas:
			id_muerto = self.celdas_ocupadas[(cabeza_x, cabeza_y)]
			self.viboras[id_muerto].viva = False
			self.borrar_vibora(id_muerto)
			del self.viboras[id_muerto]
			if id_muerto == idn :
				return
		self.celdas_ocupadas[(cabeza_x, cabeza_y)] = str(idn)
		(r, g, b) = self.viboras[str(idn)].color
		self.colorear_vibora(idn,r,g,b)

	def actualiza_espera(self) :
		espera = int(self.ui.spin_espera.text())
		self.timer_actualiza_juego.setInterval(espera)

	def escucha_tamaño_tabla(self) :
		self.inicializa_tabla()
		self.ui.spin_columnas.valueChanged.connect(self.modifica_columnas)
		self.ui.spin_filas.valueChanged.connect(self.modifica_filas)

	def inicializa_tabla(self) :
		self.ui.table_board.setRowCount(int(self.ui.spin_filas.text()))
		self.ui.table_board.setColumnCount(int(self.ui.spin_columnas.text()))
		self.ui.table_board.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.ui.table_board.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

	def modifica_columnas(self) :
		columnas_pedidas = int(self.ui.spin_columnas.text())
		for idn in self.viboras:
			self.viboras[str(idn)].actualizar_tamaño_ancho(columnas_pedidas)
		columnas_actuales = self.ui.table_board.columnCount()
		n = abs(columnas_actuales - columnas_pedidas)
		if columnas_actuales < columnas_pedidas :
			accion, siguiente = self.ui.table_board.insertColumn, 1 
		else :
			accion, siguiente = self.ui.table_board.removeColumn, -1
			columnas_actuales -= 1
		for i in range(n) :
			accion(columnas_actuales)
			columnas_actuales += siguiente		
		self.ui.table_board.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

	def modifica_filas(self) :
		filas_pedidas = int(self.ui.spin_filas.text())
		for idn in self.viboras:
			self.viboras[str(idn)].actualizar_tamaño_alto(filas_pedidas)
		filas_actuales = self.ui.table_board.rowCount()
		n = abs(filas_actuales - filas_pedidas)
		if filas_actuales < filas_pedidas :
			accion, siguiente = self.ui.table_board.insertRow, 1 
		else :
			accion, siguiente = self.ui.table_board.removeRow, -1
			filas_actuales -= 1
		for i in range(n) :
			accion(filas_actuales)
			filas_actuales += siguiente		
		self.ui.table_board.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

	def keyPressEvent_board(self, eventQKeyEvent) :
		key = eventQKeyEvent.key()
		if key == QtCore.Qt.Key_Left:
			self.vibora.modifica_direccion(3)
		elif key == QtCore.Qt.Key_Up:
			self.vibora.modifica_direccion(0)
		elif key == QtCore.Qt.Key_Right:
			self.vibora.modifica_direccion(1)
		elif key == QtCore.Qt.Key_Down:
			self.vibora.modifica_direccion(2)

class Vibora() :

	def __init__(self) :
		self.identificador = "0"
		self.color = (100,149,237)
		self.viva = True
		self.cuerpo = [(0,0),(1,0),(2,0),(3,0),(4,0)]#lista de tuplas, donde cada tupla son (x,y) coordenadas en la tabla. Lista en posicion 0 es cola
		self.direccion = Direccion(2)
		self.cola = self.cuerpo[0]
		self.cabeza = self.cuerpo[-1]
		self.ancho_tablero = 20
		self.alto_tablero = 20

	def avanza(self) :
		self.actualizar_extremos()
		for i in range(len(self.cuerpo)-1) :
			self.cuerpo[i] = self.cuerpo[i+1][:]

		if self.direccion == Direccion.arriba :
			self.cuerpo[-1] = (self.cabeza[0]-1,self.cabeza[1]) if self.cuerpo[-1][0] != 0 else (self.alto_tablero-1,self.cabeza[1])

		elif self.direccion == Direccion.abajo :
			self.cuerpo[-1] = (self.cabeza[0]+1,self.cabeza[1]) if self.cuerpo[-1][0] != self.alto_tablero-1 else (0,self.cabeza[1])

		elif self.direccion == Direccion.izquierda :
			self.cuerpo[-1] = (self.cabeza[0],self.cabeza[1]-1) if self.cuerpo[-1][1] != 0 else (self.cabeza[0],self.ancho_tablero-1)

		elif self.direccion == Direccion.derecha :
			self.cuerpo[-1] = (self.cabeza[0],self.cabeza[1]+1) if self.cuerpo[-1][1] != self.ancho_tablero-1 else (self.cabeza[0],0)

		self.actualizar_extremos()

		#como es una vibora de longitud 5, el unico caso en el que se puede morir es cuando choca con cola
		if self.cabeza == self.cola :
			self.viva = False

	def modifica_direccion(self, nueva_dir):
		if self.movimiento_valido(nueva_dir):
			self.direccion = Direccion(nueva_dir)

	def movimiento_valido(self, direccion) :
		if Direccion(direccion) == Direccion.arriba or Direccion(direccion) == Direccion.abajo :
			return self.direccion == Direccion.izquierda or self.direccion == Direccion.derecha
		return self.direccion == Direccion.arriba or self.direccion == Direccion.abajo

	def actualizar_tamaño_ancho(self, ancho) :
		self.ancho_tablero = ancho
	
	def actualizar_tamaño_alto(self, alto) :
		self.alto_tablero = alto

	def actualizar_extremos(self) :
		self.cola = self.cuerpo[0]
		self.cabeza = self.cuerpo[-1] 



class Direccion(Enum):
	arriba = 0
	derecha = 1
	abajo = 2
	izquierda = 3


if __name__ == '__main__' :
	app = QtGui.QApplication(sys.argv)
	window = MyWindow()
	sys.exit(app.exec_())