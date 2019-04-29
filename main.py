#!flask/bin/python

import os
from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for
from joblib import load
from werkzeug.utils import secure_filename
from plagiarism_logic import PlagiarismCheck


UPLOAD_FOLDER = '/Users/channa/Projects/plagiarism-check-on-image-docs/uploaded_imgs'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploader', methods = ['POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			print('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			print('No selected file')
			return redirect(request.url)
		if file:
			filename = secure_filename(file.filename)
			upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(upload_folder)

		obj = PlagiarismCheck()
		img_text = obj.get_text(upload_folder)

	return jsonify(return_value = img_text)

@app.route('/is-alive', methods=['GET'])
def index():
    return jsonify(return_value = "channa works on GCC project")

if __name__ == "__main__":
    print("Loading!")
    app.run()
