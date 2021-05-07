from flask import Flask, request
from werkzeug.utils import secure_filename
from services.analyzer_service import main, load_fonts

import os

app = Flask(__name__)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)


# load_fonts()


@app.route('/', methods=['GET'])
def first():
    return {
        'status': 'success'
    }

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

