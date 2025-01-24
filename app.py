from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from analyzer import process_files

app = Flask(__name__)

@app.route("/analyze", methods=['POST'])
def analyze():
    try:
        # Get the uploaded files
        questionnaire_file = request.files.get('questionnaireFile')
        instagram_files = {
            'account_info': request.files.get('accountInfoFile'),
            'activity': request.files.get('activityFile'),
            'connections': request.files.get('connectionsFile'),
            'content': request.files.get('contentFile')
        }
        
        # Process files and get insights
        result = process_files(questionnaire_file, instagram_files)
        
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Create a folder to store uploaded files
UPLOAD_FOLDER = 'user_data'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def home_page():
    return render_template("home_page.html")

@app.route("/submit", methods=['POST'])
def submit():
    try:
        # Get the JSON data sent from the form
        data = request.get_json()
    
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save responses to a text file
        filename = f'responses_{timestamp}.txt'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": "Responses saved successfully",
            "filename": filename
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/upload-files", methods=['POST'])
def upload_files():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a timestamped folder to store the uploaded files
        session_folder = os.path.join(UPLOAD_FOLDER, f'upload_{timestamp}')
        os.makedirs(session_folder)
        
        # Save the uploaded files to the folder
        saved_files = []
        for file_key in request.files:
            file = request.files[file_key]
            if file:
                # Secure  the filename to prevent directory traversal
                filename = secure_filename(file.filename)
                filepath = os.path.join(session_folder, filename)
                file.save(filepath)
                saved_files.append(filename)
        
        return jsonify({
            "success": True,
            "message": f"Successfully saved {len(saved_files)} files",
            "files": saved_files
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/questionnaire")
def questionnaire():
    return render_template("questionnaire.html")

@app.route("/insights")
def insights():
    return render_template("insights.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)