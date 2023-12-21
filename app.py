from flask import Flask, jsonify, send_file, make_response
import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
import io
from flask_cors import CORS
import os

load_dotenv()  # Load environment variables from the .env file

app = Flask(__name__)
CORS(app)

# Initialize the S3 client
s3 = boto3.client('s3', region_name=os.environ['AWS_REGION'])  # Use the region from environment variables

# Specify the S3 bucket
bucket_name = 'statusi-build-aps1'

def get_s3_object(key):
    try:
        print(f"Fetching S3 object with key: {key}")
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read()
        return content
    except Exception as e:
        print(f"Error fetching S3 object: {e}")
        return None


@app.route("/")
def index():
    html_file_key = 'statusi-ui-temp-build-aps1/build/index.html'
    content = get_s3_object(html_file_key)
    return send_file(io.BytesIO(content), mimetype='text/html')

@app.route("/manifest.json")
def manifest():
    manifest_file_key = 'statusi-ui-temp-build-aps1/build/manifest.json'
    content = get_s3_object(manifest_file_key)
    return send_file(io.BytesIO(content), mimetype='application/json')


# Add a route to serve static files from S3
@app.route('/static/<path:folder>/<path:filename>')
def serve_static(folder, filename):
    key = f'statusi-ui-temp-build-aps1/build/static/{folder}/{filename}'
    content = get_s3_object(key)

    if content is None:
        print(f"File not found for key: {key}")
        return "File not found", 404

    # Create a Flask response with the correct headers
    response = make_response(content)

    # Set the Content-Type dynamically based on the file type
    _, extension = os.path.splitext(filename)
    response.headers['Content-Type'] = f'text/{extension[1:]}'

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response  # Return the response object, not the content

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port= 8000)