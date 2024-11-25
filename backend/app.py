from firebase_admin import credentials, auth, firestore
import firebase_admin
from scraper.scraper import scrape_website, scrape_anchors
from rag.rag import RAG
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Celery
from celery import Celery
import redis

# Configure Celery logging
logger = logging.getLogger("celery")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s: %(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Firebase

# Flask app setup
app = Flask(__name__)

# Enable CORS for all routes and origins (TODO: update for prod)
CORS(app)

# Redis and Celery setup
redis_url = 'redis://redis:6379/0'
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

rag_instance = RAG()


# URL PROCESSING
@celery.task
def process_file_task(file_url):
    """
    Task on celery to process the file
    """
    print(f"Processing file: {file_url}")

    try:
        # Scrape the site
        site_text = scrape_website(file_url)
        res = rag_instance.vectorize_and_store(site_text, "sites", 1000)
        print(f"Processed file at {file_url}")

        return res

    except Exception as e:
        return {"status": "failure", "error": str(e)}


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


@app.route('/ask-question', methods=['POST'])
def ask_question():
    data = request.json
    query = data.get('query')
    res = rag_instance.get_similar_results(query, "sites")
    ans = rag_instance.get_rag_response(query, "sites")
    return jsonify({"answer": str(ans), "similar_results": res})


# JOB SITE SCRAPING
@celery.task
def process_job_site_task(url):
    """
    Task on celery to process the job site
    """
    print(f"Processing url: {url}")
    all_urls = scrape_anchors(url)

    # Scrape the site
    for site_url in all_urls:
        if "href" not in site_url:
            print("Does not have href")
            continue
        logger.info("Scraping website..." + site_url["href"])
        site_text = scrape_website(site_url["href"])
        res = rag_instance.vectorize_and_store(
            site_text, "jobs", 1000000, site_url["text"])
        print(f"Processed website")
    return res


@app.route("/resume-match", methods=["POST"])
def resume_match():
    data = request.json
    resume_text = data.get('resume_text')
    res = rag_instance.get_similar_results(resume_text, "jobs")
    return jsonify(res)


@app.route('/scrape-jobs', methods=['POST'])
def process_recruitment_site():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No file URL provided'}), 400

    # Trigger Celery job
    task = process_job_site_task.delay(url)
    return jsonify({'message': 'File processing started', 'task_id': task.id})


# HOME
@app.route('/', methods=['GET'])
def home_page():
    return jsonify({"message": "landing page"})

# CELERY CHECK


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

# EVENTS FUNCTION


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

# CLEAR REDIS


@app.route('/clear-db', methods=['POST'])
def clear_db():
    data = request.json
    index_name = data.get('index_name')

    res = rag_instance.clear_keys(index_name)
    return res


# Start application
if __name__ == '__main__':
    # Add "host="0.0.0.0"" to allow the app to be accessible outside the docker container
    app.run(host="0.0.0.0", debug=True, port=5000)
