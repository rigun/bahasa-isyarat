from flask import Flask,jsonify,request
from Model.Dataseed import tasks
from Model.Petal import Petal
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)
@app.route('/get/task', methods=['GET'])
def getTask():
    """

    Ini adalah endpoint untuk mengambil seluruh data
    ---
    tags:
        - Rest Controller
    parameter:
    responses:
        200:
            description: Success get all data

    """
    return jsonify({'tasks': tasks})

@app.route("/input/task", methods=['POST'])
def inputTask():
    """
    Ini adalah endpoint untuk menambahkan data task
    ---
    tags:
        - Rest Controller
    parameters:
        - name: body
          in: body
          required:
            - petalLength
            - petalWidth
            - sepalLength
            - sepalWidth
          properties:
            petalLength:
                type: integer
                description: Masukkan data
                default: 0
            petalWidth:
                type: integer
                description: Masukkan data
                default: 0
            sepalLength:
                type: integer
                description: Masukkan data
                default: 0
            sepalWidth:
                type: integer
                description: Masukkan data
                default: 0
    responses:
        200:
            description: Sucess Input
    """
    new_task = request.get_json()

    petalLength = new_task['petalLength']
    peatlWidth = new_task['petalWidth']
    sepalLength = new_task['sepalLength']
    sepalWidth = new_task['sepalWidth']

    newPetal = Petal(sepalLength,sepalWidth,petalLength,peatlWidth)
    tasks.append(newPetal.__dict__)
    return jsonify({'meesaage': 'success'})

@app.route('/update/task/<int:id>', methods=['PUT'])
def updateTask(id):
    new_task = request.get_json()

    petalLength = new_task['petalLength']
    peatlWidth = new_task['petalWidth']
    sepalLength = new_task['sepalLength']
    sepalWidth = new_task['sepalWidth']

    newPetal = Petal(sepalLength, sepalWidth, petalLength, peatlWidth)
    tasks[id] = newPetal.__dict__
    return jsonify({'meesaage': 'success update'})

@app.route('/delete/task/<int:id>', methods=['DELETE'])
def deleteTask(id):
    del tasks[id]
    return jsonify({'meesaage': 'success delete'})



app.run(debug=True)