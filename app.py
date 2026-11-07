
from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime, timezone

app = Flask(__name__)

DATA_DIR = Path("verification/data")
QUEUE_FILE = DATA_DIR / "review_queue.json"
AUDIT_FILE = DATA_DIR / "audit_log.json"


def load_queue():
    with open(QUEUE_FILE, encoding="utf-8") as file:
        return json.load(file)


def save_queue(items):
    temp_file = QUEUE_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)

    temp_file.replace(QUEUE_FILE)


def load_audit_log():
    if not AUDIT_FILE.exists():
        return []

    with open(AUDIT_FILE, encoding="utf-8") as file:
        return json.load(file)


def save_audit_log(entries):
    temp_file = AUDIT_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2, ensure_ascii=False)

    temp_file.replace(AUDIT_FILE)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/proposals")
def get_proposals():
    return jsonify(load_queue())


@app.route("/api/audit")
def get_audit_log():
    return jsonify(load_audit_log())


@app.route("/api/proposals/<proposal_id>/decision", methods=["POST"])
def decide_proposal(proposal_id):

    data = request.get_json(silent=True) or {}

    decision = data.get("decision")
    reviewer = data.get("reviewer_name", "").strip()
    ownership_verified = data.get("ownership_verified")

    if decision not in ("APPROVED", "REJECTED"):
        return jsonify({"error": "Invalid decision"}), 400

    if not reviewer:
        return jsonify({"error": "Reviewer name is required."}), 400

    if len(reviewer) > 100:
        return jsonify({"error": "Reviewer name is too long."}), 400

    if decision == "APPROVED" and ownership_verified is not True:
        return jsonify({
            "error": "Ownership verification is required before approval."
        }), 400

    items = load_queue()

    for item in items:

        if item["proposal_id"] == proposal_id:

            if item["approval_status"] != "PENDING":
                return jsonify({
                    "error": "Proposal already decided."
                }), 409

            timestamp = datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            )

            audit_entry = {
                "proposal_id": proposal_id,
                "facility_name": item["facility_name"],
                "decision": decision,
                "reviewer_name": reviewer,
                "ownership_verified": ownership_verified is True,
                "decided_at": timestamp,
                "crm_updated": False
            }

            item["approval_status"] = decision
            item["approved"] = decision == "APPROVED"
            item["ownership_verified"] = ownership_verified is True
            item["reviewer_name"] = reviewer
            item["decided_at"] = timestamp

            audit_entries = load_audit_log()
            audit_entries.append(audit_entry)

            save_queue(items)
            save_audit_log(audit_entries)

            return jsonify({
                "message": "Decision saved locally.",
                "approval_status": decision,
                "decided_at": timestamp,
                "crm_updated": False
            })

    return jsonify({"error": "Proposal not found."}), 404


if __name__ == "__main__":
    app.run(debug=False)
