from flask import Flask, jsonify, request

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import uuid
from datetime import datetime

from detector import get_llm_score
from heuristics import get_stylometric_score
from confidence import calculate_confidence, get_attribution
from labels import generate_label
from audit import add_entry, get_log

app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

@app.route("/", methods=["GET"])

# Simple endpoint used to verify the API is running
def home():
    return jsonify({
        "message": "Provenance Guard API is running"
    })


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")


# Process a new content submission
def submit():
    # Read the incoming JSON request
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    # Extract the required fields from the request
    text = data.get("text")
    creator_id = data.get("creator_id")

    # Make sure both required fields are provided
    if not text or not creator_id:
        return jsonify({"error": "text and creator_id are required"}), 400

    # Create a unique ID for this submission
    content_id = str(uuid.uuid4())

    # Run both detection signals
    llm_score = get_llm_score(text)
    stylometric_score = get_stylometric_score(text)

    # Combine the signal scores into a final confidence score
    confidence = calculate_confidence(llm_score, stylometric_score)
    attribution = get_attribution(confidence)

    # Generate the transparency label shown to the user
    label = generate_label(attribution, confidence)

    # Create an audit log entry for this submission
    entry = {
        "event_type": "submission",
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "stylometric_score": stylometric_score,
        "status": "classified",
        "label": label
    }

    # Save the submission to the audit log
    add_entry(entry)

    # Return the analysis results to the client
    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "status": "classified",
        "signals": {
            "llm_score": llm_score,
            "stylometric_score": stylometric_score
        }
    })

# Return all audit log entries
@app.route("/log", methods=["GET"])
def log():
    return jsonify({
        "entries": get_log()
    })

# Allow creators to appeal a previous classification
@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    content_id = data.get("content_id")
    creator_reasoning = data.get("creator_reasoning")

    if not content_id or not creator_reasoning:
        return jsonify({"error": "content_id and creator_reasoning are required"}), 400

    appeal_entry = {
        "event_type": "appeal",
        "content_id": content_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "under_review",
        "appeal_reasoning": creator_reasoning
    }
    from audit import update_status
    update_status(content_id, "under_review")

    add_entry(appeal_entry)

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Appeal received and marked for review."
    })

# Return summary statistics about previous submissions
@app.route("/analytics", methods=["GET"])
def analytics():
    entries = get_log()

    submissions = [e for e in entries if e.get("event_type") == "submission"]
    appeals = [e for e in entries if e.get("event_type") == "appeal"]

    total_submissions = len(submissions)
    total_appeals = len(appeals)

    likely_ai = len([e for e in submissions if e.get("attribution") == "likely_ai"])
    likely_human = len([e for e in submissions if e.get("attribution") == "likely_human"])
    uncertain = len([e for e in submissions if e.get("attribution") == "uncertain"])

    if total_submissions > 0:
        appeal_rate = total_appeals / total_submissions
        average_confidence = sum(e.get("confidence", 0) for e in submissions) / total_submissions
    else:
        appeal_rate = 0
        average_confidence = 0

    return jsonify({
        "total_submissions": total_submissions,
        "detection_pattern": {
            "likely_ai": likely_ai,
            "likely_human": likely_human,
            "uncertain": uncertain
        },
        "total_appeals": total_appeals,
        "appeal_rate": round(appeal_rate, 2),
        "average_confidence": round(average_confidence, 2)
    })

if __name__ == "__main__":
    app.run(debug=True)