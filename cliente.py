import sys
from PyQt4 import QtGui, uic, QtCore
from xmlrpc.client import ServerProxy
import time


class MyWindow(QtGui.QMainWindow):
	def __init__(self):
		super(MyWindow, self).__init__()
		self.ui = uic.loadUi('cliente.ui', self)
		self.ui.table_cliente.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.ui.table_cliente.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.ui.table_cliente.keyPressEvent = self.keyPressEvent_cliente
		self.proxy = None
		self.estado_actual = None
		self.identificador = None
		self.jugando = False

		self.ui.pushButton_ping.clicked.connect(self.ping)
		self.ui.pushButton_participar.clicked.connect(self.participar)	
		self.timer_actualizar_juego = QtCore.QTimer(self)
		self.timer_actualizar_juego.timeout.connect(self.actualizar_juego)

		self.show()

	def keyPressEvent_cliente(self, eventQKeyEvent) :
		if not self.jugando:
			return
		key = eventQKeyEvent.key()
		if key == QtCore.Qt.Key_Left:
			self.proxy.cambia_direccion(self.identificador,3)
		elif key == QtCore.Qt.Key_Up:
			self.proxy.cambia_direccion(self.identificador,0)
		elif key == QtCore.Qt.Key_Right:
			self.proxy.cambia_direccion(self.identificador,1)
		elif key == QtCore.Qt.Key_Down:
			self.proxy.cambia_direccion(self.identificador,2)

	def sigo_vivo(self, viboras):
		for vibora in viboras:
			if self.identificador == vibora["id"]:
				return True
		return False

	def actualiza_viboras(self, viboras_anteriores, viboras_actuales):
		for vibora in viboras_anteriores:
			sigue_viva = False
			for vibora_a in viboras_actuales:
				if vibora["id"] == vibora_a["id"]:
					sigue_viva = True
					break
			if not sigue_viva:
				cuerpo = vibora["camino"]
				for (x,y) in cuerpo:
					self.colorear(x, y, 255, 255, 255)

	def actualizar_juego(self):
		if not self.jugando:
			return
		viboras_anteriores = []
		if self.estado_actual != None:
			viboras_anteriores = self.estado_actual["viboras"]
			self.actualizar_colas(viboras_anteriores)
		self.estado_actual = self.proxy.estado_del_juego()
		viboras = self.estado_actual["viboras"]
		self.actualiza_viboras(viboras_anteriores, viboras)

		"""if not self.sigo_vivo(viboras):
									self.jugando = False
									print("has perdido")
									self.timer_actualizar_juego.stop()"""
									
		self.timer_actualizar_juego.setInterval(max(0,self.estado_actual["espera"]-50))
		columnas = self.estado_actual["tamY"]
		filas = self.estado_actual["tamX"]
		if columnas != self.ui.table_cliente.columnCount():
			self.modifica_columnas(columnas)
		if filas != self.ui.table_cliente.rowCount():
			self.modifica_filas(filas)
		
		self.dibuja_viboras(viboras)

	def actualizar_colas(self, viboras_anteriores):
		for vibora_anterior in viboras_anteriores:
			self.colorear(vibora_anterior["camino"][0][0], vibora_anterior["camino"][0][1], 255,255,255)
	
	def dibuja_viboras(self, viboras):
		for vibora in viboras:
			camino = vibora["camino"]
			color = vibora["color"]		
			for (x,y) in camino: 
				self.colorear(x,y,color["r"], color["g"], color["b"])
			

	def colorear(self, x, y, r, g, b) :
		if self.ui.table_cliente.item(x,y) == None :
			cell = QtGui.QTableWidgetItem()
			self.ui.table_cliente.setItem(x, y, cell)
		color = QtGui.QColor(r,g,b)
		try :
			self.ui.table_cliente.item(x,y).setBackground(QtGui.QBrush(color))
		except :
			#si hubo un error es porque el item en dicha posicion no existia (seguramente por mover cantidad de celdas)
			#No hacemos nada
			pass

	def modifica_columnas(self, columnas) :
		columnas_actuales = self.ui.table_cliente.columnCount()
		n = abs(columnas_actuales - columnas)
		if columnas_actuales < columnas :
			accion, siguiente = self.ui.table_cliente.insertColumn, 1 
		else :
			accion, siguiente = self.ui.table_cliente.removeColumn, -1
			columnas_actuales -= 1
		for i in range(n) :
			accion(columnas_actuales)
			columnas_actuales += siguiente		
		self.ui.table_cliente.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

	def modifica_filas(self, filas) :
		filas_actuales = self.ui.table_cliente.rowCount()
		n = abs(filas_actuales - filas)
		if filas_actuales < filas :
			accion, siguiente = self.ui.table_cliente.insertRow, 1 
		else :
			accion, siguiente = self.ui.table_cliente.removeRow, -1
			filas_actuales -= 1
		for i in range(n) :
			accion(filas_actuales)
			filas_actuales += siguiente		
		self.ui.table_cliente.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

		

	def ping(self):
		self.ui.pushButton_ping.setText("Pinging...")
		if not self.jugando :
			self.crea_proxy()
		try:
			if self.proxy.ping() == "¡Pong!":				
				self.ui.pushButton_ping.setText("¡Pong!")
		except :
			self.ui.pushButton_ping.setText("No pong :(")

	def participar(self):
		if not self.jugando :
			self.crea_proxy()	

		try:
			informacion = self.proxy.yo_juego()
		except:
			return

		self.jugando = True
		self.identificador = informacion["id"]
		self.ui.lineEdit_id.setText(self.identificador) 
		color = informacion["color"]
		(r, g, b) = (color["r"], color["g"], color["b"])
		self.ui.lineEdit_color.setText("r : "+str(r)+" g : "+str(g)+" b : "+str(b))
		self.timer_actualizar_juego.start()
		self.ui.lineEdit_url.setReadOnly(True) 
		self.ui.spinBox_puerto.setReadOnly(True)
		self.ui.pushButton_participar.setEnabled(False)

	def crea_proxy(self):
		url = self.ui.lineEdit_url.text()
		puerto = self.ui.spinBox_puerto.text()
		self.proxy = ServerProxy("http://"+url+":"+puerto)
		 

"""
		print(proxy.ping())
		print(proxy.cambia_direccion("0", 3))
		print(proxy.yo_juego())
		print(proxy.estado_del_juego())"""

		
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())