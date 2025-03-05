from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from gradio_client import Client, handle_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Gradio Client
client = Client("tdnathmlenthusiast/gender_age_prediction")

def predict_audio(file_path):
    try:
        result = client.predict(
            audio_path=handle_file(file_path),
            api_name="/predict"
        )
        return result  # Returns tuple (age, gender)
    except Exception as e:
        print(f"Error: {e}")
        return None, None

@app.route("/", methods=['GET'])
def predict():
    if 'audio' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
    audio_file.save(file_path)
    
    age, gender = predict_audio(file_path)
    os.remove(file_path)  # Clean up the uploaded file
    
    if not age or not gender:
        return jsonify({"error": "Prediction failed"}), 500
    
    return jsonify({"predicted_age": age, "predicted_gender": gender})

@app.route("/", methods=['GET'])
def info():
    return jsonify({"message": "Send a POST request with an audio file to get predictions."})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)
