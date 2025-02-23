from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load Notion API Key and Database ID from Environment Variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Notion API URL
NOTION_API_URL = "https://api.notion.com/v1/pages"

@app.route("/", methods=["GET"])
def home():
    return "Notion Recipe Uploader is running!"

@app.route("/add-recipe", methods=["POST"])
def add_recipe():
    try:
        # Get JSON data from request
        data = request.json

        # Ensure required fields exist
        required_fields = ["name", "ingredients", "instructions", "images", "preparation_time", "difficulty_level", "chef_notes"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Construct the Notion payload
        notion_payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Recipe Name": {"title": [{"text": {"content": data["name"]}}]},
                "Ingredients": {"rich_text": [{"text": {"content": data["ingredients"]}}]},
                "Instructions": {"rich_text": [{"text": {"content": data["instructions"]}}]},
                "Images": {"files": [{"name": "Recipe Image", "external": {"url": data["images"][0]}}]} if data["images"] else {},
                "Preparation Time": {"rich_text": [{"text": {"content": str(data["preparation_time"]) + " minutes"}}]},
                "Difficulty Level": {"multi_select": [{"name": data["difficulty_level"]}]},
                "Chef Notes": {"rich_text": [{"text": {"content": data["chef_notes"]}}]}
            }
        }

        # Debugging: Print the request payload before sending to Notion
        print("Sending Payload to Notion:")
        print(notion_payload)

        # Send data to Notion API
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        response = requests.post(NOTION_API_URL, headers=headers, json=notion_payload)

        # Return Notion's response
        if response.status_code == 200:
            return jsonify({"success": True, "message": "Recipe added successfully!", "notion_response": response.json()}), 200
        else:
            return jsonify({"error": "Failed to add recipe", "notion_error": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
