from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

NOTION_API_KEY = "your_notion_secret"
NOTION_DATABASE_ID = "your_notion_database_id"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.route('/')
def home():
    return "Notion Recipe Uploader is Running"

@app.route('/add-recipe', methods=['POST'])
def add_recipe():
    data = request.json

    notion_data = {
        "parent": { "database_id": NOTION_DATABASE_ID },
        "properties": {
            "Recipe Name": { "title": [{ "text": { "content": data["name"] } }] },
            "Ingredients": { "rich_text": [{ "text": { "content": data["ingredients"] } }] },
            "Instructions": { "rich_text": [{ "text": { "content": data["instructions"] } }] },
            "Preparation Time": { "number": data["preparation_time"] },
            "Difficulty Level": { "select": { "name": data["difficulty_level"] } },
            "Chef Notes": { "rich_text": [{ "text": { "content": data["chef_notes"] } }] },
            "Images": {
                "files": [{"name": img, "external": {"url": img}} for img in data.get("images", [])]
            }
        }
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=HEADERS,
        json=notion_data
    )

    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
