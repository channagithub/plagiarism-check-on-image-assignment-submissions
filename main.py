#!flask/bin/python

import os
from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for
from flask import render_template
from joblib import load
from werkzeug.utils import secure_filename
from plagiarism_logic import PlagiarismCheck
import cgi, cgitb, jinja2
from google.cloud import datastore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "plagiarism-check-image-docs-596999b61703.json"

# UPLOAD_FOLDER = '/Users/channa/Projects/plagiarism-check-on-image-docs/uploaded_imgs'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

datastore_client = datastore.Client()


def get_entity(student_name, student_subject, student_submission):
	print(student_name, student_subject, student_submission)
	task_key = datastore_client.key(student_subject, student_name)
	task = datastore.Entity(key=task_key)
	task['description'] = student_submission
	return task

@app.route('/uploader', methods = ['POST'])
def upload_file():

	if request.method == 'POST':

		if 'subject-name' not in request.form:
			print('No subject name')
			return redirect(request.url)
		subject_name = request.form['subject-name']

		if 'student-name' not in request.form:
			print('No student name')
			return redirect(request.url)
		student_name = request.form['student-name']

		if 'assignment-file' not in request.form:
			print('No assignment file')
			return redirect(request.url)
		assignment_file = request.form['assignment-file']

		obj = PlagiarismCheck()
		img_text = obj.get_text(assignment_file)

		datastore_client.put(get_entity(str(student_name), str(subject_name), str(img_text)))

	return jsonify(return_value = img_text)

@app.route('/is-alive', methods=['GET'])
def index():
    return jsonify(return_value = "channa works on GCC project")

@app.route('/', methods=['GET', 'POST'])
def index_():
    return render_template('index.html')

if __name__ == "__main__":
    print("Loading!")
    app.run()
