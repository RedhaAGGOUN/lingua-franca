from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
import requests
import threading
import webbrowser
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

# Initialisation de l'application Flask
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# URL du serveur LibreTranslate local
LIBRETRANSLATE_URL = "http://localhost:5001/translate"

# Vérifie si le serveur LibreTranslate est disponible
def check_libretranslate_availability():
    try:
        response = requests.get("http://localhost:5001", timeout=2)
        return response.status_code == 200
    except requests.RequestException as e:
        app.logger.error(f"LibreTranslate server not available: {str(e)}")
        return False

# Traduction avec Google Translator via deep_translator
def translate_with_google(text, source, target):
    try:
        src = source if source != "auto" else "auto"
        result = GoogleTranslator(source=src, target=target).translate(text)
        app.logger.debug(f"Google Translate successful: {result}")
        return result
    except Exception as e:
        app.logger.error(f"Google Translate error: {str(e)}")
        return f"Translation error: {str(e)}"

# Traduction avec LibreTranslate (serveur local requis)
def translate_with_libre(text, source, target):
    if not check_libretranslate_availability():
        return "Translation error: LibreTranslate server is not available"

    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text"
    }
    headers = {"Content-Type": "application/json"}

    try:
        app.logger.debug(f"Sending request to LibreTranslate with payload: {payload}")
        response = requests.post(LIBRETRANSLATE_URL, json=payload, headers=headers)
        response.raise_for_status()
        translated = response.json()["translatedText"]
        app.logger.debug(f"LibreTranslate successful: {translated}")
        return translated
    except requests.RequestException as e:
        app.logger.error(f"LibreTranslate error: {str(e)}")
        return f"Translation error: {str(e)}"

# Fonction générique de traduction
def translate(text, source, target, engine):
    if not text.strip():
        return "Error: No text provided"
    if engine == "googletranslate":
        return translate_with_google(text, source, target)
    elif engine == "libretranslate":
        return translate_with_libre(text, source, target)
    return "Error: Invalid translation engine"

# Route principale
@app.route("/", methods=["GET", "POST"])
def index():
    input_text = ""
    translated_text = ""
    src_lang = "auto"
    dest_lang = "en"
    engine = "libretranslate"

    if request.method == "POST":
        input_text = request.form.get("input_text", "")
        src_lang = request.form.get("src_lang", "auto")
        dest_lang = request.form.get("dest_lang", "en")
        engine = request.form.get("engine", "libretranslate")

        app.logger.debug(f"Input: '{input_text}', Source: {src_lang}, Target: {dest_lang}, Engine: {engine}")
        translated_text = translate(input_text, src_lang, dest_lang, engine)

    return render_template("index.html",
                           input_text=input_text,
                           translated_text=translated_text,
                           src_lang=src_lang,
                           dest_lang=dest_lang,
                           engine=engine)

# Lance automatiquement le navigateur
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

# Lancement de l'app
if __name__ == "__main__":
    threading.Timer(2.0, open_browser).start()
    app.run(debug=True)
