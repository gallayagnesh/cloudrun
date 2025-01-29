@app.route("/upload", methods=["POST"])
def upload():
    """Handle image upload and store it in GCP Cloud Storage."""
    try:
        if "file" not in request.files:
            return "No file part in the request", 400

        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400

        if file:
            # Save file locally
            local_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            print(f"Saving file locally: {local_path}")
            file.save(local_path)

            # Upload file to Cloud Storage
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(file.filename)
            print(f"Uploading {file.filename} to GCP Storage...")
            blob.upload_from_filename(local_path)

            # Make file publicly accessible
            blob.make_public()
            os.remove(local_path)  # Remove local copy

            print("Upload successful!")
            return redirect(url_for("index"))

        return "File upload failed", 500

    except Exception as e:
        print(f"Error: {e}")  # Log the actual error
        return f"Internal Server Error: {e}", 500
