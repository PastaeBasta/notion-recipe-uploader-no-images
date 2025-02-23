import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load Notion API Key from Railway Variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # Add this to Railway Variables

# Notion API Endpoint
NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.route("/", methods=["GET"])
def home():
    return "Notion Recipe Uploader is running!", 200

@app.route("/add-recipe", methods=["POST"])
def add_recipe():
    # Get JSON data from request
    data = request.json

    # Validate required fields
    required_fields = ["name", "ingredients", "instructions", "preparation_time", "difficulty_level"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Prepare Notion API request payload
    notion_payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Recipe Name": {"title": [{"text": {"content": data["name"]}}]},
            "Ingredients": {"rich_text": [{"text": {"content": data["ingredients"]}}]},
            "Instructions": {"rich_text": [{"text": {"content": data["instructions"]}}]},
            "Preparation Time": {"number": data["preparation_time"]},
            "Difficulty Level": {"select": {"name": data["difficulty_level"]}}
        }
    }

    # Optional Fields
    if "chef_notes" in data:
        notion_payload["properties"]["Chef Notes"] = {"rich_text": [{"text": {"content": data["chef_notes"]}}]}

    if "images" in data and isinstance(data["images"], list) and len(data["images"]) > 0:
        notion_payload["properties"]["Images"] = {
            "files": [{"name": "Recipe Image", "external": {"url": img}} for img in data["images"]]
        }

    # Send data to Notion
    response = requests.post(NOTION_API_URL, headers=NOTION_HEADERS, json=notion_payload)

    # Return response
    if response.status_code == 200:
        return jsonify({"message": "Recipe added successfully!", "notion_response": response.json()}), 200
    else:
        return jsonify({"error": "Failed to add recipe", "notion_error": response.json()}), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
