from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)
DATA_FILE = "data.json"

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"expenses": {}, "categories": {}}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/data")
def get_data():
    return jsonify(load())

@app.route("/api/check_items", methods=["POST"])
def check_items():
    items = request.json.get("items", [])
    data = load()
    cats = data.get("categories", {})
    unknown, known = [], {}
    for item in items:
        key = item.strip().lower()
        if key in cats:
            known[item] = cats[key]
        else:
            unknown.append(item)
    return jsonify({"unknown": unknown, "known": known})

@app.route("/api/add_entry", methods=["POST"])
def add_entry():
    body = request.json
    date = body.get("date")
    raw = body.get("input", "")
    item_categories = body.get("item_categories", {})
    data = load()

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    parsed = []
    for part in parts:
        tokens = part.strip().rsplit(" ", 1)
        if len(tokens) == 2:
            try:
                parsed.append({"name": tokens[0].strip(), "amount": float(tokens[1].strip())})
            except:
                pass

    for item, cat in item_categories.items():
        data["categories"][item.strip().lower()] = cat

    if date not in data["expenses"]:
        data["expenses"][date] = []

    existing_count = len(data["expenses"][date])
    for i, p in enumerate(parsed):
        key = p["name"].strip().lower()
        cat = data["categories"].get(key, item_categories.get(p["name"], "Others"))
        data["categories"][key] = cat
        data["expenses"][date].append({
            "id": f"{date}_{existing_count + i}_{p['name']}",
            "name": p["name"],
            "amount": p["amount"],
            "category": cat
        })

    save(data)
    return jsonify({"success": True})

@app.route("/api/delete_item", methods=["POST"])
def delete_item():
    body = request.json
    date, item_id = body.get("date"), body.get("id")
    data = load()
    if date in data["expenses"]:
        data["expenses"][date] = [e for e in data["expenses"][date] if e.get("id") != item_id]
        if not data["expenses"][date]:
            del data["expenses"][date]
    save(data)
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
