from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_VERSION = "2022-06-28"
NOTION_URL = "https://api.notion.com/v1/pages"

@app.route('/')
def home():
    return "Notion Recipe Uploader is running!"

@app.route('/add-recipe', methods=['POST'])
def add_recipe():
    data = request.json

    # Check if required fields are present
    required_fields = ["name", "ingredients", "instructions", "prep_time", "difficulty"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Notion API payload
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Recipe Name": {"title": [{"text": {"content": data["name"]}}]},
            "Ingredients": {"rich_text": [{"text": {"content": data["ingredients"]}}]},
            "Instructions": {"rich_text": [{"text": {"content": data["instructions"]}}]},
            "Preparation Time": {"number": data["prep_time"]},
            "Difficulty Level": {"multi_select": [{"name": data["difficulty"]}]},
            "Chef Notes": {"rich_text": [{"text": {"content": data.get("notes", "")}}]},
        }
    }

    # If image is provided, add it
    if "image_url" in data and data["image_url"]:
        payload["properties"]["Images"] = {"files": [{"name": "recipe_image", "external": {"url": data["image_url"]}}]}

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

    response = requests.post(NOTION_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return jsonify({"message": "Recipe added successfully!", "notion_response": response.json()})
    else:
        return jsonify({"error": "Failed to add recipe", "notion_error": response.json()}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
