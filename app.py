import os
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import storage

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
BUCKET_NAME = "flask-images-bucket"  # Replace with your GCP bucket name

# Ensure the upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize GCP Storage Client
storage_client = storage.Client()

@app.route("/")
def index():
    """Render the homepage with upload and list options."""
    blobs = list(storage_client.list_blobs(BUCKET_NAME))
    images = [{"filename": blob.name, "url": blob.public_url} for blob in blobs]
    return render_template("index.html", images=images)

@app.route("/upload", methods=["POST"])
def upload():
    """Handle image upload and store it in GCP Cloud Storage."""
    if "file" not in request.files:
        return "No file part in the request", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    if file:
        # Save file locally
        local_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        print("localpath",local_path)
        file.save(local_path)

        # Upload file to Cloud Storage
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file.filename)
        print("blob",blob)
        blob.upload_from_filename(local_path)

        # Make file publicly accessible
        blob.make_public()
        os.remove(local_path)  # Remove local copy

        return redirect(url_for("index"))

    return "File upload failed", 500


if __name__ == "__main__":
    app.run(debug=True)
