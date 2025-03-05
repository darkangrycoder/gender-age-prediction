from flask import Flask, request, render_template_string
import os
from werkzeug.utils import secure_filename
from gradio_client import Client, handle_file

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
    <p>Predicted Age: {{ age }}</p>
    <p>Predicted Gender: {{ gender }}</p>
    <a href="/">Go Back</a>
</body>
</html>
"""

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
        
        age, gender = predict_audio(file_path)
        os.remove(file_path)  # Clean up the uploaded file
        
        if not age or not gender:
            return render_template_string(INDEX_HTML, error="Prediction failed")
        
        return render_template_string(RESULTS_HTML, age=age, gender=gender)
    
    return render_template_string(INDEX_HTML)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)
