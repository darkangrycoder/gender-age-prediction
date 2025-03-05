from flask import Flask, request, jsonify
from gradio_client import Client, handle_file

app = Flask(__name__)
client = Client("tdnathmlenthusiast/gender_age_prediction")

data_store = {}  # Temporary in-memory storage for inputs

@app.route("/input", methods=["GET"])
def get_input():
    audio_url = request.args.get("audio_url")
    if not audio_url:
        return jsonify({"error": "Missing audio_url parameter"}), 400
    
    data_store["audio_url"] = audio_url  # Store input temporarily
    return jsonify({"message": "Input received", "audio_url": audio_url})

@app.route("/predict", methods=["GET"])
def get_prediction():
    if "audio_url" not in data_store:
        return jsonify({"error": "No input found, send data to /input first"}), 400
    
    audio_url = data_store.pop("audio_url")  # Retrieve and remove stored input
    result = client.predict(audio_path=handle_file(audio_url), api_name="/predict")
    
    return jsonify({"prediction": result})

if __name__ == "__main__":
    app.run(debug=True)
