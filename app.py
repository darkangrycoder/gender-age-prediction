from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from gradio_client import Client, handle_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Gradio Client
client = Client("tdnathmlenthusiast/gender_age_prediction")

# Store the latest prediction result
latest_prediction = None

def predict_audio(file_path):
    try:
        result = client.predict(
            audio_path=handle_file(file_path),
            api_name="/predict"
        )
        return {"age": result[0], "gender": result[1]}
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=['GET'])
def index():
    return jsonify({"message": "Audio prediction API is running"})

@app.route("/predict", methods=['POST'])
def predict():
    global latest_prediction
    if 'audio' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
    audio_file.save(file_path)
    
    latest_prediction = predict_audio(file_path)
    os.remove(file_path)  # Clean up the uploaded file
    
    return jsonify({"message": "Prediction complete. Use GET /result to fetch."})

@app.route("/result", methods=['GET'])
def get_result():
    if latest_prediction:
        return jsonify(latest_prediction)
    return jsonify({"error": "No prediction available"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)
