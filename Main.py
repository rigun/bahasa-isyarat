from flask import Flask, flash, request, redirect, jsonify, session
from werkzeug.utils import secure_filename
from flasgger import Swagger
from Model.Prediction import Prediction
from flask_cors import CORS
import tensorflow as tf
import base64
app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app, resources={r"/*": {"origins": "*"}})
Swagger(app)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def predictionData():
    # Loads label file, strips off carriage return
    label_lines = [line.rstrip() for line
                       in tf.gfile.GFile("logs/output_labels.txt")]
    with tf.gfile.FastGFile("logs/output_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        with tf.Graph().as_default() as graph:
            _ = tf.import_graph_def(graph_def, name="")
            with tf.Session() as sess:
                # Feed the image_data as input to the graph and get first prediction
                softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
                image_data = tf.gfile.FastGFile('test.jpg', 'rb').read()
                predictions = sess.run(softmax_tensor, \
                         {'DecodeJpeg/contents:0': image_data})
                # Sort to show labels of first prediction in order of confidence
                top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
                sess.close()
                tf.Variable(0)
                return [predictions[0][top_k[0]],label_lines[top_k[0]]]
@app.route("/predict", methods=['GET'])
def getPredictError():
    return 'error'
@app.route("/post/predict", methods=['POST'])
def inputTask():
    """
    Ini adalah endpoint untuk menambahkan data task
    ---
    tags:
    - Rest Controller
    parameters:
     - in: formData
       name: upfile
       type: file
       description: The file to upload.
    responses:
        200:
            description: Sucess Input
    """
    # check if the post request has the file part
    if 'upfile' not in request.files:
        flash('No file part')
        return jsonify({'message': 'no file part'})
    file = request.files['upfile']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return jsonify({'message': 'No selected file'})
    if file and allowed_file(file.filename):
        file.save('test.jpg')
        predict = predictionData()
        P = Prediction(str(predict[0]), predict[1])
        return jsonify({'message': [P.__dict__]})
    return jsonify({'message': 'error'})

def convert_and_save(data):
    with open("test.jpg", "wb") as fh:
        fh.write(base64.b64decode(data))
        
@app.route("/predict", methods=['POST'])
def inputTaskApi():
    data = request.get_json()
    imgBase64 = data['upfile'].replace('data:image/png;base64,', '')
    imgBase64 = imgBase64.replace(' ','+')
    convert_and_save(imgBase64)
    predict = predictionData()
    P = Prediction(str(predict[0]), predict[1])
    return jsonify({'message': [P.__dict__]})

@app.route("/", methods=['GET'])
def getTask():
    return app.send_static_file("index.html")

if __name__ == '__main__':
    app.debug = True
    app.run()