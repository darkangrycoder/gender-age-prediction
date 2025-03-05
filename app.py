from flask import Flask, request, render_template_string, jsonify
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Define templates as strings
INDEX_HTML = """ 
<!DOCTYPE html>
<html>
<head>
    <title>Audio Prediction</title>
</head>
<body>
    <h1>Upload an Audio File</h1>
    {% if error %}<p style='color:red;'>{{ error }}</p>{% endif %}
    <form action="/" method="post" enctype="multipart/form-data">
        <input type="file" name="audio" required>
        <button type="submit">Upload</button>
    </form>
</body>
</html>
"""

RESULTS_HTML = """ 
<!DOCTYPE html>
<html>
<head>
    <title>Prediction Results</title>
</head>
<body>
    <h1>Prediction Result</h1>
    <p>{{ output_text }}</p>
    <a href="/">Go Back</a>
</body>
</html>
"""

def predict_audio(file_path):
    try:
        with open(file_path, "rb") as f:
            files = {"audio": f}
            response = requests.post(
                "https://tdnathmlenthusiast-gender-age-prediction.hf.space/gradio_api/call/predict",
                files=files
            )
        response.raise_for_status()
        data = response.json().get("data", [])
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        if 'audio' not in request.files:
            return render_template_string(INDEX_HTML, error="No file uploaded")
        
        audio_file = request.files['audio']
        if audio_file.filename == "":
            return render_template_string(INDEX_HTML, error="No selected file")
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
        audio_file.save(file_path)
        
        prediction_data = predict_audio(file_path)
        os.remove(file_path)  # Clean up the uploaded file
        
        if not prediction_data:
            return render_template_string(INDEX_HTML, error="Prediction failed")
        
        confidence_list = prediction_data[0].get('confidences', [])
        labels = [elem['label'] for elem in confidence_list if elem.get('confidence')]
        label_text = ", ".join(labels)
        
        return render_template_string(RESULTS_HTML, output_text=label_text)
    
    return render_template_string(INDEX_HTML)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)
