import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Ensure API key and database ID are set
if NOTION_API_KEY is None:
    raise ValueError("❌ ERROR: NOTION_API_KEY is missing. Set it in Railway variables.")
if NOTION_DATABASE_ID is None:
    raise ValueError("❌ ERROR: NOTION_DATABASE_ID is missing. Set it in Railway variables.")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.route("/")
def home():
    return jsonify({"message": "Notion Recipe Uploader API is running."})

@app.route("/add-recipe", methods=["POST"])
def add_recipe():
    """Receive recipe data and upload it to Notion."""
    try:
        data = request.json

        # Validate required fields
        required_fields = ["name", "ingredients", "instructions", "prep_time", "difficulty"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Prepare payload for Notion
        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Recipe Name": {"title": [{"text": {"content": data["name"]}}]},
                "Ingredients": {"rich_text": [{"text": {"content": data["ingredients"]}}]},
                "Instructions": {"rich_text": [{"text": {"content": data["instructions"]}}]},
                "Preparation Time": {"number": data["prep_time"]},
                "Difficulty Level": {"multi_select": [{"name": data["difficulty"]}]},
                "Chef Notes": {"rich_text": [{"text": {"content": data.get("notes", "")}}]}
            }
        }

        # If images exist, add them (but don't make it mandatory)
        if "image_url" in data and data["image_url"]:
            payload["properties"]["Images"] = {
                "files": [{"name": "recipe_image", "external": {"url": data["image_url"]}}]
            }

        # Send data to Notion
        notion_response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=NOTION_HEADERS,
            json=payload
        )

        if notion_response.status_code == 200:
            return jsonify({
                "message": "Recipe added successfully!",
                "notion_response": notion_response.json()
            })
        else:
            return jsonify({
                "error": "Failed to add recipe",
                "notion_error": notion_response.json()
            }), notion_response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
