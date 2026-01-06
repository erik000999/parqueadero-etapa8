from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parqueadero.db')
        conn.row_factory = sqlite3.Row
            return conn

            def init_db():
                conn = get_db_connection()
                    # Creamos la tabla con trazabilidad de entrada y salida
                        conn.execute('''CREATE TABLE IF NOT EXISTS registros 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT, casa TEXT, entrada TEXT, salida TEXT)''')
                                    
                                        # Si la base está vacía, insertamos 97 vehículos para la prueba del semáforo
                                            check = conn.execute("SELECT COUNT(*) FROM registros WHERE salida IS NULL").fetchone()[0]
                                                if check == 0:
                                                        for i in range(1, 98):
                                                                    placa = f"DEM{str(i).zfill(3)}"
                                                                                casa = str(i)
                                                                                            # Simulamos que entraron en las últimas 8 horas
                                                                                                        hora = (datetime.now() - timedelta(minutes=random.randint(10, 480))).strftime("%Y-%m-%d %H:%M:%S")
                                                                                                                    conn.execute("INSERT INTO registros (placa, casa, entrada) VALUES (?, ?, ?)", (placa, casa, hora))
                                                                                                                        conn.commit()
                                                                                                                            conn.close()

                                                                                                                            @app.route('/')
                                                                                                                            def index():
                                                                                                                                conn = get_db_connection()
                                                                                                                                    # Conteo de ocupados para la lógica del semáforo
                                                                                                                                        ocupados = conn.execute("SELECT COUNT(*) FROM registros WHERE salida IS NULL").fetchone()[0]
                                                                                                                                            activos_raw = conn.execute("SELECT * FROM registros WHERE salida IS NULL ORDER BY id DESC").fetchall()
                                                                                                                                                
                                                                                                                                                    activos = []
                                                                                                                                                        ahora = datetime.now()
                                                                                                                                                            for row in activos_raw:
                                                                                                                                                                    entrada = datetime.strptime(row['entrada'], "%Y-%m-%d %H:%M:%S")
                                                                                                                                                                            duracion = ahora - entrada
                                                                                                                                                                                    horas, rem = divmod(duracion.seconds, 3600)
                                                                                                                                                                                            minutos, _ = divmod(rem, 60)
                                                                                                                                                                                                    item = dict(row)
                                                                                                                                                                                                            item['tiempo'] = f"{horas}h {minutos}m"
                                                                                                                                                                                                                    activos.append(item)
                                                                                                                                                                                                                        
                                                                                                                                                                                                                            conn.close()
                                                                                                                                                                                                                                return render_template('index.html', disponibles=105-ocupados, ocupados=ocupados, activos=activos)

                                                                                                                                                                                                                                @app.route('/ingreso', methods=['POST'])
                                                                                                                                                                                                                                def ingreso():
                                                                                                                                                                                                                                    placa = request.form['placa'].upper().replace(" ", "")
                                                                                                                                                                                                                                        casa = request.form['casa']
                                                                                                                                                                                                                                            conn = get_db_connection()
                                                                                                                                                                                                                                                # Validación de equidad: un cupo por casa
                                                                                                                                                                                                                                                    if conn.execute("SELECT * FROM registros WHERE casa=? AND salida IS NULL", (casa,)).fetchone():
                                                                                                                                                                                                                                                            conn.close()
                                                                                                                                                                                                                                                                    return "ERROR: Esta casa ya ocupa un lugar."
                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                                                                                                                                                                                                                                                conn.execute("INSERT INTO registros (placa, casa, entrada) VALUES (?, ?, ?)", (placa, casa, ahora))
                                                                                                                                                                                                                                                                                    conn.commit()
                                                                                                                                                                                                                                                                                        conn.close()
                                                                                                                                                                                                                                                                                            return redirect('/')

                                                                                                                                                                                                                                                                                            @app.route('/salida/<int:id>')
                                                                                                                                                                                                                                                                                            def salida(id):
                                                                                                                                                                                                                                                                                                conn = get_db_connection()
                                                                                                                                                                                                                                                                                                    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                                                                                                                                                                                                                                                                        conn.execute("UPDATE registros SET salida=? WHERE id=?", (ahora, id))
                                                                                                                                                                                                                                                                                                            conn.commit()
                                                                                                                                                                                                                                                                                                                conn.close()
                                                                                                                                                                                                                                                                                                                    return redirect('/')

                                                                                                                                                                                                                                                                                                                    @app.route('/exportar')
                                                                                                                                                                                                                                                                                                                    def exportar():
                                                                                                                                                                                                                                                                                                                        conn = get_db_connection()
                                                                                                                                                                                                                                                                                                                            df = pd.read_sql_query("SELECT * FROM registros", conn)
                                                                                                                                                                                                                                                                                                                                conn.close()
                                                                                                                                                                                                                                                                                                                                    df.to_csv('reporte_etapa8.csv', index=False)
                                                                                                                                                                                                                                                                                                                                        return send_file('reporte_etapa8.csv', as_attachment=True)

                                                                                                                                                                                                                                                                                                                                        if __name__ == '__main__':
                                                                                                                                                                                                                                                                                                                                            init_db()
                                                                                                                                                                                                                                                                                                                                                app.run(debug=True, host='0.0.0.0', port=5000)