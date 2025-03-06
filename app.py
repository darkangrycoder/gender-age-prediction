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
        return {"age": result[0], "gender": result[1]}
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=['GET'])
def index():
    return jsonify({"message": "Audio prediction API is running"})

@app.route("/predict", methods=['GET'])
def predict():
    file_name = request.args.get("file")
    if not file_name:
        return jsonify({"error": "No file provided"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file_name))
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    prediction = predict_audio(file_path)
    os.remove(file_path)  # Clean up the uploaded file
    
    return jsonify(prediction)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)
