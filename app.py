import os
from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import certifi

app = Flask(__name__, template_folder='templates')

# Render proporcionará la URI de MongoDB Atlas en esta variable de entorno
MONGO_URI = os.environ.get('MONGO_URI')

try:
    # Conectamos a MongoDB usando el certificado seguro de certifi
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    # Accedemos a la base de datos llamada 'cluster_render' (se crea automáticamente)
    db = client['cluster_render']
    # Usamos la colección 'tareas'
    tareas_collection = db['tareas']
    print("Conexión exitosa a MongoDB Atlas")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")

@app.route('/')
def index():
    return render_template('index.html')

# API: Obtener todas las tareas
@app.route('/api/tareas', methods=['GET'])
def get_tareas():
    try:
        tareas = []
        # Buscamos todos los documentos e invertimos el orden por ID interno (_id)
        for tarea in tareas_collection.find().sort('_id', -1):
            tareas.append({
                'id': str(tarea['_id']), # Convertimos el ObjectId de Mongo a texto
                'titulo': tarea['titulo']
            })
        return jsonify(tareas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Agregar una nueva tarea
@app.route('/api/tareas', methods=['POST'])
def add_tarea():
    try:
        datos = request.get_json()
        nuevo_documento = {'titulo': datos.get('titulo')}
        
        # Insertamos en la colección de MongoDB
        resultado = tareas_collection.insert_one(nuevo_documento)
        
        return jsonify({
            'id': str(resultado.inserted_id),
            'titulo': nuevo_documento['titulo']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
