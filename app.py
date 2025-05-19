
import os
import fitz  # PyMuPDF
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

def translate_with_google(text, source, target):
    try:
        src = source if source != "auto" else "auto"
        return GoogleTranslator(source=src, target=target).translate(text)
    except Exception as e:
        return f"Translation error: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def api_translate():
    data = request.json
    text = data.get("text", "")
    source = data.get("source", "auto")
    target = data.get("target", "en")

    if not text.strip():
        return jsonify({"error": "Empty text"}), 400

    result = translate_with_google(text, source, target)
    return jsonify({"translation": result})

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("pdf_file")
    source = request.form.get("src_lang", "auto")
    target = request.form.get("dest_lang", "en")

    if not file or not file.filename.endswith(".pdf"):
        return jsonify({"error": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        doc = fitz.open(filepath)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        translated = translate_with_google(text, source, target)
        return jsonify({"translation": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
