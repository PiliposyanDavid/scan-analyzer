from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from services.analyzer_service import main

import os

app = Flask(__name__)


# load_fonts()

@app.route('/', methods=['GET'])
def initial():
    return render_template('index.html')


@app.route('/api/health-check', methods=['GET'])
def health_check():
    return {
        'status': 'success'
    }


@app.route('/api/font/upload', methods=['POST'])
def upload_font():
    if not os.path.exists('uploads'):
        os.mkdir('uploads')

    f = request.files['the_file']
    file_path = 'uploads/' + secure_filename(f.filename)
    f.save(file_path)

    response = main(file_path)
    os.remove(file_path)

    return response


if __name__ == "__main__":
    app.run()
