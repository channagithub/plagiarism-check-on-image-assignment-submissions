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
import google.cloud.vision as vision
import cgi, cgitb, jinja2
from google.cloud import datastore
import re
import heapq
import io

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "plagiarism-check-image-docs-596999b61703.json"

# UPLOAD_FOLDER = '/Users/channa/Projects/plagiarism-check-on-image-docs/uploaded_imgs'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__)) + '/temp'
datastore_client = datastore.Client()

class PlagiarismCheck(object):
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def get_text(self, path):
        with io.open(path, 'rb') as image_file:
            content = image_file.read()
        image = vision.types.Image(content=content)
        resp = self.client.text_detection(image=image)
        text = ' '.join([d.description for d in resp.text_annotations])
        #print(text)
        return text

def get_entity(student_name, student_subject, student_submission):
	# print(student_name, student_subject, student_submission)
	task_key = datastore_client.key(student_subject, student_name)
	task = datastore.Entity(key=task_key)
	task['description'] = student_submission
	return task

def get_plagiarism_report(current_three_gram, query, top_n = 5):
	heap = []
	n = len(current_three_gram)
	ret_report = {}
	if n:
		# loop through all students
		for a in query.fetch(): 

			other_student_name = a.key.name
			other_student_submission = a['description']

			match_count = 0

			# loop through each gram of current submission and check how many match
			for a_gram in current_three_gram:
				if a_gram in other_student_submission:
					match_count += 1

			# calculate percentage plagiarism
			plagiarism_val = round((float(match_count) / n) * 100, 2) if match_count else 0

			# add to heap for top 5
			heapq.heappush(heap, (plagiarism_val, other_student_name))

	ret_report = dict([(k, v) for v, k in heapq.nlargest(top_n, heap)])
	return ret_report

def get_three_gram(img_text):
	shingleLength = 2
	tokens = re.findall(r"[\w']+", img_text)
	three_gram = ['_'.join(tokens[i:i+shingleLength]) for i in range(len(tokens) - shingleLength + 1)]
	return three_gram

@app.route('/uploader', methods = ['POST'])
def uploader():

	if request.method == 'POST':

		if 'subject-name' not in request.form:
			print('No subject name')
			return redirect(request.url)
		subject_name = request.form['subject-name']

		if 'student-name' not in request.form:
			print('No student name')
			return redirect(request.url)
		student_name = request.form['student-name']

		# check if the post request has the file part
		if 'assignment-file' not in request.files:
			print('No file part')
			return redirect(request.url)
		file = request.files['assignment-file']

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

		# remove the file
		os.remove(upload_folder)
		
		# convert to ascii
		img_text = str(img_text.encode('ascii', 'ignore'))
		three_gram = get_three_gram(img_text)

		# query exisiting entities for the given subject
		query = datastore_client.query(kind=subject_name)
		plagiarism_report = get_plagiarism_report(three_gram, query)
		
		# add this submission to database
		datastore_client.put(get_entity(str(student_name), str(subject_name), three_gram))

		ret_val = {
		"subject_name": subject_name,
		"plagiarism_report": plagiarism_report
		}
		result = [""]*5
		percentage = [None]*5
		i=0
		for key, val in plagiarism_report.items():
			if val>0:
				result[i]=str(key)
				percentage[i]=str(val)
				i+=1
		



	return render_template('index.html', student_name= "Student Name: " + student_name, 
								subject_name = "Subject Name: " +subject_name,  
								result1=result[0],result2=result[1],result3=result[2],result4=result[3], result5=result[4],
								percentage1=percentage[0],percentage2=percentage[1],percentage3=percentage[2]
								,percentage4=percentage[3],percentage5=percentage[4])

								#jsonify(return_value = ret_val)

@app.route('/is-alive', methods=['GET'])
def index():
    return jsonify(return_value = "channa works on GCC project")

@app.route('/', methods=['GET', 'POST'])
def index_():
    return render_template('index.html')

if __name__ == "__main__":
    print("Loading!")
    app.run()
