from flask import Flask, request, jsonify

# Celery
from celery import Celery
import redis

# Firebase
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Flask app setup
app = Flask(__name__)

# Redis and Celery setup
redis_url = 'redis://localhost:6379/0'
app.config['CELERY_BROKER_URL'] = redis_url
app.config['CELERY_RESULT_BACKEND'] = redis_url

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Firebase setup
cred = credentials.Certificate("firebase_service_account.json")
firebase_admin.initialize_app(cred)

# Firestore database instance (optional, if using Firestore)
# - make sure this is after the initialize_app() is called
db = firestore.client()


@celery.task
def process_file_task(file_url):
    """
    Task on celery to process the file
    """
    # Add your vectorization and RAG update logic here
    print(f"Processing file: {file_url}")
    # Mock processing
    import time
    time.sleep(5)
    return f"Processed file at {file_url}"


@app.route('/', methods=['GET'])
def home_page():
    return jsonify({"message": "landing page"})


@app.route('/process-file', methods=['POST'])
def process_file():
    """
    API Route that will be called
    """
    data = request.json
    file_url = data.get('fileURL')

    if not file_url:
        return jsonify({'error': 'No file URL provided'}), 400

    # Trigger Celery job
    task = process_file_task.delay(file_url)
    return jsonify({'message': 'File processing started', 'task_id': task.id})


@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    """
    Check status of task
    """
    task = process_file_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({'status': 'Pending'}), 200
    elif task.state == 'SUCCESS':
        return jsonify({'status': 'Completed', 'result': task.result}), 200
    else:
        return jsonify({'status': 'Processing'}), 200


@app.route('/get-event-data', methods=['GET'])
def get_event_data():
    try:
        all_events = db.collection('events').stream()
        res = []
        for event in all_events:
            res.append({event.id: event.to_dict()})
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Start application
if __name__ == '__main__':
    # Add "host="0.0.0.0"" to allow the app to be accessible outside the docker container
    app.run(host="0.0.0.0", debug=True, port=5000)
