#!/usr/bin/env python3
"""
ProjectFlow — Backend Flask
Lance avec : python server.py
Accès : http://localhost:5000
"""

import json
import os
from datetime import date
from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

DATA_FILE = "data.json"

# ─────────────────────────────────────────────
#  Données par défaut
# ─────────────────────────────────────────────
DEFAULT_DATA = {
    "users": [
        {
            "id": 1, "un": "Sacha", "pw": "$mila2012", "role": "admin",
            "fn": "Sacha", "ln": "Admin", "email": "sacha@pf.fr",
            "av": "SA", "avi": 0, "joined": "2024-01-10"
        },
        {
            "id": 2, "un": "Alexis", "pw": "0000", "role": "controleur",
            "fn": "Alexis", "ln": "Martin", "email": "alexis@pf.fr",
            "av": "AM", "avi": 1, "joined": "2024-02-15"
        },
        {
            "id": 3, "un": "Marie", "pw": "client123", "role": "client",
            "fn": "Marie", "ln": "Dupont", "email": "marie@ex.fr",
            "av": "MD", "avi": 3, "joined": "2024-03-01",
            "ps": "en cours", "web": "https://marie-portfolio.fr"
        },
        {
            "id": 4, "un": "Thomas", "pw": "pass456", "role": "client",
            "fn": "Thomas", "ln": "Bernard", "email": "thomas@ex.fr",
            "av": "TB", "avi": 5, "joined": "2024-04-10",
            "ps": "en attente", "web": ""
        },
        {
            "id": 5, "un": "Sophie", "pw": "soph789", "role": "client",
            "fn": "Sophie", "ln": "Laurent", "email": "sophie@ex.fr",
            "av": "SL", "avi": 2, "joined": "2024-02-20",
            "ps": "terminé", "web": "https://sophie-events.fr"
        }
    ],
    "questionnaires": [
        {
            "id": 101, "title": "Brief créatif", "cid": 3, "sentBy": 1,
            "sentAt": "2024-03-05", "status": "pending",
            "questions": [
                {"id": 1, "type": "short", "question": "Quel est l'objectif principal de votre site ?", "answer": ""},
                {"id": 2, "type": "mc", "question": "Votre cible principale ?", "options": ["Particuliers", "Professionnels", "Les deux"], "answer": ""},
                {"id": 3, "type": "scale", "question": "Budget global (1=faible, 10=élevé)", "min": 1, "max": 10, "answer": ""},
                {"id": 4, "type": "long", "question": "Citez 2–3 sites que vous admirez et expliquez pourquoi.", "answer": ""}
            ]
        }
    ],
    "timelines": {
        "3": [
            {"id": 1, "t": "Prise de contact", "s": "Réunion effectuée", "st": "done"},
            {"id": 2, "t": "Maquettes", "s": "3 versions validées", "st": "done"},
            {"id": 3, "t": "Développement", "s": "Phase front en cours", "st": "current"},
            {"id": 4, "t": "Tests & Recette", "s": "", "st": "todo"},
            {"id": 5, "t": "Mise en ligne", "s": "", "st": "todo"}
        ],
        "4": [
            {"id": 1, "t": "Prise de contact", "s": "", "st": "current"},
            {"id": 2, "t": "Devis", "s": "", "st": "todo"}
        ],
        "5": [
            {"id": 1, "t": "Prise de contact", "s": "", "st": "done"},
            {"id": 2, "t": "Maquettes", "s": "Validées", "st": "done"},
            {"id": 3, "t": "Développement", "s": "Terminé", "st": "done"},
            {"id": 4, "t": "Mise en ligne", "s": "Déployé le 10/04", "st": "done"}
        ]
    },
    "nid": 300
}

# ─────────────────────────────────────────────
#  Lecture / Écriture JSON
# ─────────────────────────────────────────────
def load_db():
    """Charge data.json ou crée le fichier avec les données par défaut."""
    if not os.path.exists(DATA_FILE):
        save_db(DEFAULT_DATA)
        print(f"[ProjectFlow] data.json créé avec les données par défaut.")
        return DEFAULT_DATA
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    """Sauvegarde toutes les données dans data.json (appelé à chaque modification)."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[ProjectFlow] data.json mis à jour — {date.today()}")

# ─────────────────────────────────────────────
#  Routes statiques
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "projectflow.html")

# ─────────────────────────────────────────────
#  API — Base de données complète
# ─────────────────────────────────────────────
@app.route("/api/db", methods=["GET"])
def get_db():
    """Retourne toute la base de données."""
    return jsonify(load_db())

@app.route("/api/db", methods=["POST"])
def set_db():
    """Remplace toute la base de données (sync depuis le front)."""
    data = request.get_json()
    if not data:
        abort(400)
    save_db(data)
    return jsonify({"ok": True})

# ─────────────────────────────────────────────
#  API — Utilisateurs
# ─────────────────────────────────────────────
@app.route("/api/users", methods=["GET"])
def get_users():
    db = load_db()
    return jsonify(db["users"])

@app.route("/api/users", methods=["POST"])
def create_user():
    db = load_db()
    user = request.get_json()
    user["id"] = db["nid"]
    db["nid"] += 1
    user.setdefault("joined", str(date.today()))
    db["users"].append(user)
    if user.get("role") == "client":
        db["timelines"][str(user["id"])] = []
    save_db(db)
    return jsonify(user), 201

@app.route("/api/users/<int:uid>", methods=["PUT"])
def update_user(uid):
    db = load_db()
    data = request.get_json()
    for i, u in enumerate(db["users"]):
        if u["id"] == uid:
            db["users"][i].update(data)
            save_db(db)
            return jsonify(db["users"][i])
    abort(404)

@app.route("/api/users/<int:uid>", methods=["DELETE"])
def delete_user(uid):
    db = load_db()
    db["users"] = [u for u in db["users"] if u["id"] != uid]
    save_db(db)
    return jsonify({"ok": True})

# ─────────────────────────────────────────────
#  API — Questionnaires
# ─────────────────────────────────────────────
@app.route("/api/questionnaires", methods=["GET"])
def get_questionnaires():
    db = load_db()
    return jsonify(db["questionnaires"])

@app.route("/api/questionnaires", methods=["POST"])
def create_questionnaire():
    db = load_db()
    q = request.get_json()
    q["id"] = db["nid"]
    db["nid"] += 1
    q.setdefault("sentAt", str(date.today()))
    q.setdefault("status", "pending")
    db["questionnaires"].append(q)
    save_db(db)
    return jsonify(q), 201

@app.route("/api/questionnaires/<int:qid>", methods=["PUT"])
def update_questionnaire(qid):
    db = load_db()
    data = request.get_json()
    for i, q in enumerate(db["questionnaires"]):
        if q["id"] == qid:
            db["questionnaires"][i].update(data)
            save_db(db)
            return jsonify(db["questionnaires"][i])
    abort(404)

@app.route("/api/questionnaires/<int:qid>", methods=["DELETE"])
def delete_questionnaire(qid):
    db = load_db()
    db["questionnaires"] = [q for q in db["questionnaires"] if q["id"] != qid]
    save_db(db)
    return jsonify({"ok": True})

# ─────────────────────────────────────────────
#  API — Timelines
# ─────────────────────────────────────────────
@app.route("/api/timelines", methods=["GET"])
def get_timelines():
    db = load_db()
    return jsonify(db["timelines"])

@app.route("/api/timelines/<int:uid>", methods=["POST"])
def add_timeline_step(uid):
    db = load_db()
    step = request.get_json()
    step["id"] = db["nid"]
    db["nid"] += 1
    key = str(uid)
    if key not in db["timelines"]:
        db["timelines"][key] = []
    db["timelines"][key].append(step)
    save_db(db)
    return jsonify(step), 201

@app.route("/api/timelines/<int:uid>", methods=["PUT"])
def update_timeline(uid):
    db = load_db()
    steps = request.get_json()
    db["timelines"][str(uid)] = steps
    save_db(db)
    return jsonify({"ok": True})

# ─────────────────────────────────────────────
#  Lancement
# ─────────────────────────────────────────────
if __name__ == "__main__":
    load_db()  # Crée data.json si absent
    print("=" * 50)
    print("  ProjectFlow — Serveur démarré")
    print("  Accès : http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
