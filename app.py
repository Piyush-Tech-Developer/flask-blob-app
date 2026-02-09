from flask import Flask, request, send_file, jsonify
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
import tempfile

app = Flask(__name__)

STORAGE_ACCOUNT_URL = os.getenv("STORAGE_ACCOUNT_URL")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url=STORAGE_ACCOUNT_URL,
    credential=credential
)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    blob_client = container_client.get_blob_client(file.filename)
    blob_client.upload_blob(file, overwrite=True)
    return jsonify({"message": "File uploaded successfully"})

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    blob_client = container_client.get_blob_client(filename)
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(blob_client.download_blob().readall())
        return send_file(temp.name, as_attachment=True, download_name=filename)

@app.route("/update/<filename>", methods=["PATCH"])
def update(filename):
    file = request.files['file']
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file, overwrite=True)
    return jsonify({"message": "File updated successfully"})

@app.route("/delete/<filename>", methods=["DELETE"])
def delete(filename):
    blob_client = container_client.get_blob_client(filename)
    blob_client.delete_blob()
    return jsonify({"message": "File deleted successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
