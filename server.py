from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_VERSION = "2022-06-28"
NOTION_API_URL = "https://api.notion.com/v1/pages"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

@app.route('/add-recipe', methods=['POST'])
def add_recipe():
    try:
        data = request.json

        # Construct Notion payload
        notion_payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Recipe Name": {"title": [{"text": {"content": data["name"]}}]},
                "Ingredients": {"rich_text": [{"text": {"content": data["ingredients"]}}]},
                "Instructions": {"rich_text": [{"text": {"content": data["instructions"]}}]},
                "Preparation Time": {"number": data["prep_time"]},
                "Difficulty Level": {"multi_select": [{"name": data["difficulty"]}]},
                "Chef Notes": {"rich_text": [{"text": {"content": data.get("notes", "")}}]}
            }
        }

        # Only add image if it's present
        if "image_url" in data and data["image_url"]:
            notion_payload["properties"]["Images"] = {
                "files": [{"name": "recipe_image", "external": {"url": data["image_url"]}}]
            }

        # Send request to Notion API
        response = requests.post(NOTION_API_URL, headers=HEADERS, json=notion_payload)

        if response.status_code == 200:
            return jsonify({"message": "Recipe added successfully!", "notion_response": response.json()}), 200
        else:
            return jsonify({"error": "Failed to add recipe", "notion_error": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
