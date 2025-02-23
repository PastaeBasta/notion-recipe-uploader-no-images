from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Notion API Config
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Notion API Headers
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.route("/", methods=["GET"])
def home():
    return "Notion Recipe Uploader is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    notion_payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Recipe Name": {"title": [{"text": {"content": data.get("name")}}]},
            "Ingredients": {"rich_text": [{"text": {"content": data.get("ingredients")}}]},
            "Instructions": {"rich_text": [{"text": {"content": data.get("instructions")}}]},
            "Difficulty Level": {"select": {"name": data.get("difficulty")}},
            "Preparation Time": {"number": data.get("time")},
            "Chef Notes": {"rich_text": [{"text": {"content": data.get("chef_notes", "")}}]},
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=notion_payload)

    if response.status_code == 200:
        return jsonify({"status": "success", "message": "Recipe added to Notion!"}), 200
    else:
        return jsonify({"status": "error", "message": response.json()}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
