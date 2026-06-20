from datetime import datetime
import sqlite3

RutaDB="BD/Franquicias.db"

def Conectar():
	return sqlite3.connect(RutaDB)

def GuardarRes(categoria, confianza):
	conexion = Conectar()
	cursor = conexion.cursor()
	fecha = datetime.now().strftime("%Y-%m-%d %H:%M-%S")

	cursor.execute("""INSERT INTO Historial(Fecha,Categoria, Confianza) VALUES (?,?,?) """,(fecha,categoria,confianza))
	conexion.commit()
	conexion.close()

def ConsultaTot():
	conexion=Conectar()
	cursor=conexion.cursor()
	
	cursor.execute("""SELECT * FROM Historial ORDER BY id DESC """)
	datos = cursor.fetchall()
	conexion.close()
	return datos
