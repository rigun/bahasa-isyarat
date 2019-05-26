from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flasgger import Swagger
# import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
import tensorflow as tf
from scipy.ndimage import imread

app = Flask(__name__)
Swagger(app)

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def predictionData(filename,sign):
    # Loads label file, strips off carriage return
    label_lines = [line.rstrip() for line
                       in tf.gfile.GFile("logs/"+sign+"_labels.txt")]
    with tf.gfile.FastGFile("logs/"+sign+"_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        with tf.Graph().as_default() as graph:
            _ = tf.import_graph_def(graph_def, name="")
            with tf.Session() as sess:
                # Feed the image_data as input to the graph and get first prediction
                softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
                image_data = tf.gfile.FastGFile(filename, 'rb').read()
                predictions = sess.run(softmax_tensor, \
                         {'DecodeJpeg/contents:0': image_data})
                # Sort to show labels of first prediction in order of confidence
                top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
                sess.close()
                tf.Variable(0)
                return [predictions[0][top_k[0]],label_lines[top_k[0]]]

@app.route("/post/task", methods=['POST'])
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
        return redirect(request.url)
    file = request.files['upfile']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        result1 = predictionData(filename, 'asl')
        result2 = predictionData(filename, 'bisindo')
        if result1[0] > result2[0]:
            predict = result1
        else:
            predict = result2
        return jsonify({'score': predict[0],'result': predict[1],'message': 'success'})
    return jsonify({'message': 'error'})



if __name__ == '__main__':
    app.run(debug=False)