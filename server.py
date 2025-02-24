from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_VERSION = "2022-06-28"
NOTION_API_URL = "https://api.notion.com/v1/pages"

@app.route("/")
def home():
    return "Notion Recipe Uploader is running!"

@app.route("/add-recipe", methods=["POST"])
def add_recipe():
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        return jsonify({"error": "Missing required environment variables: NOTION_API_KEY and/or DATABASE_ID"}), 500

    try:
        data = request.json
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        }

        # Build properties for the Notion payload
        properties = {
            "Recipe Name": {
                "title": [{"text": {"content": data["name"]}}]
            },
            "Ingredients": {
                "rich_text": [{"text": {"content": data["ingredients"]}}]
            },
            "Instructions": {
                "rich_text": [{"text": {"content": data["instructions"]}}]
            },
            "Preparation Time": {
                "number": data["preparation_time"]
            },
            "Difficulty Level": {
                "multi_select": [{"name": data["difficulty_level"]}]
            },
            "Chef Notes": {
                "rich_text": [{"text": {"content": data.get("chef_notes", "")}}]
            },
           "Portions": {
    "rich_text": [{"text": {"content": data["portions"]}}]
        }

        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": properties
        }

        response = requests.post(NOTION_API_URL, json=payload, headers=headers)
        notion_response = response.json()

        if response.status_code == 200:
            return jsonify({"message": "Recipe added successfully!", "notion_response": notion_response})
        else:
            return jsonify({"error": "Failed to add recipe", "notion_error": notion_response}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
