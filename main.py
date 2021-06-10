from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from services.analyzer_service import main, load_fonts
import os

app = Flask(__name__)

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
        render_template('await.html')
        load_fonts()
        return

    response = main(file_path)
    os.remove(file_path)

    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
