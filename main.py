from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from services.analyzer_service import main, load_fonts
import os
import threading

app = Flask(__name__)
download_thread = None


# @app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


@app.route('/', methods=['GET'])
def initial():
    return render_template('index.html')


@app.route('/run', methods=['GET'])
def run():
    print("run")
    load_fonts()
    return {"status": "loaded"}


@app.route('/api/health-check', methods=['GET'])
def health_check():
    return {
        'status': 'success'
    }


@app.route('/api/font/upload', methods=['POST'])
def upload_font():
    if not os.path.exists('uploads'):
        os.mkdir('uploads')

    f = request.files['file']
    file_path = 'uploads/' + secure_filename(f.filename)
    f.save(file_path)

    if not os.path.exists('pa_fonts.json'):
        print("Here")
        if download_thread is not None and download_thread.isAlive():
            download_thread = threading.Thread(target=load_fonts(), name="LoadFonts")
            download_thread.daemon = True
            download_thread.start()

        return render_template('await.html')

    response = main(file_path)
    os.remove(file_path)

    return response


def load_fonts_background():
    download_thread = threading.Thread(target=load_fonts(), name="LoadFonts")
    download_thread.start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
