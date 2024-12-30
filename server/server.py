from flask import Flask, request, send_from_directory, jsonify
import os

app = Flask(__name__)

# Directory to store files
UPLOAD_FOLDER = 'server/uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for uploading files
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400
    
    files = request.files.getlist('files')  # Get list of files
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No selected files'}), 400
    
    uploaded_files = []
    for file in files:
        if file and file.filename:  # Ensure file has a name
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            uploaded_files.append(file.filename)
    
    return jsonify({'message': 'Files uploaded successfully!', 'files': uploaded_files})


# Route for downloading files
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# List all files on server at home
@app.route('/')
def show_files():
    files = [file.name for file in os.scandir(app.config['UPLOAD_FOLDER'])]
    return files

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
