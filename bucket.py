import os
from openai import OpenAI
import shutil
import json

PATH_TO_FRENCH_VOCAB_FOLDER = "/Users/zakick/desktop/french_code/output/vocab"
PATH_TO_FRENCH_CONVERSATION_FOLDER = "/Users/zakick/desktop/french_code/output/conversation"
PATH_TO_FRENCH_VOCAB_CATEGORIES_FOLDER = "/Users/zakick/Desktop/french_code/output/category/vocab"
PATH_TO_FRENCH_CONVERSATION_CATEGORIES_FOLDER = "/Users/zakick/Desktop/french_code/output/category/conversation"
PATH_TO_BUCKET_VOCAB_FOLDER = "/Users/zakick/Desktop/french_code/output/bucket/vocab"
PATH_TO_BUCKET_CONVERSATION_FOLDER = "/Users/zakick/Desktop/french_code/output/bucket/conversation"

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in your environment.")
client = OpenAI(api_key=api_key)

def get_meta_data():
    meta_data = []
    for a_french_level_txt_file in os.listdir(PATH_TO_FRENCH_VOCAB_FOLDER):
        if a_french_level_txt_file.startswith("."):
            continue

        if a_french_level_txt_file.endswith(".txt"):
            french_level = a_french_level_txt_file[:-4]
        else:
            continue
        
        meta_data.append({
            "type": "vocab",
            "level" : french_level,
            "data" : os.path.join(PATH_TO_FRENCH_VOCAB_FOLDER, a_french_level_txt_file),
            "category" : os.path.join(PATH_TO_FRENCH_VOCAB_CATEGORIES_FOLDER, a_french_level_txt_file),
            "bucket" : os.path.join(PATH_TO_BUCKET_VOCAB_FOLDER, french_level),
        })

    for a_french_level_txt_file in os.listdir(PATH_TO_FRENCH_CONVERSATION_FOLDER):
        if a_french_level_txt_file.startswith("."):
            continue

        if a_french_level_txt_file.endswith(".txt"):
            french_level = a_french_level_txt_file[:-4]
        else:
            continue
        
        meta_data.append({
            "type": "conversation",
            "level" : french_level,
            "data" : os.path.join(PATH_TO_FRENCH_CONVERSATION_FOLDER, a_french_level_txt_file),
            "category" : os.path.join(PATH_TO_FRENCH_CONVERSATION_CATEGORIES_FOLDER, a_french_level_txt_file),
            "bucket" : os.path.join(PATH_TO_BUCKET_CONVERSATION_FOLDER, french_level),
        })

    return meta_data


def read_categories(file_path):
    categories = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()           # remove spaces/newlines
            if not clean:
                continue                   # skip empty lines

            if clean.startswith("-"):
                clean = clean[1:].strip()  # remove "-" and extra space

            categories.append(clean)

    return categories

def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        return
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)  # delete file or symlink
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # delete folder and its contents
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")

def bootstrap():
    clear_folder(PATH_TO_BUCKET_VOCAB_FOLDER)
    clear_folder(PATH_TO_BUCKET_CONVERSATION_FOLDER)


def call_gpt_categories(txt_path: str, categories: list[str]):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()  # keeps empty lines as ""

    numbered = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))

    response = client.responses.create(
        prompt={"id": "", "version": "1"},
        input=[{
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": (
                    "CATEGORIES (use ONLY these):\n"
                    + "\n".join(f"- {c}" for c in categories)
                    + "\n\n"
                    "TXT CONTENT (USE THE LINE NUMBERS SHOWN; include empty lines too):\n"
                    + numbered
                )
            }]
        }],
        text={ "format": { "type": "json_schema", "name": "line_categorization", "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "assignments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "category": {"type": "string"},
                            "lines": {"type": "array", "items": {"type": "integer", "minimum": 1}}
                        },
                        "required": ["category", "lines"]
                    }
                }
            },
            "required": ["assignments"]
        }}}
    )

    try:
        return json.loads(response.output_text or "{}")
    except json.JSONDecodeError as e:
        print("Invalid JSON from model:", e)
        print("Raw output:", response.output_text)
        return {}



def validate_response(data):
    # Must be dict
    if not isinstance(data, dict):
        return {}

    assignments = data.get("assignments")
    if not isinstance(assignments, list):
        return {}

    for item in assignments:
        if not isinstance(item, dict):
            return {}

        if "category" not in item or "lines" not in item:
            return {}

        if not isinstance(item["category"], str):
            return {}

        if not isinstance(item["lines"], list):
            return {}

        for n in item["lines"]:
            if not isinstance(n, int):
                return {}
    return data


def save_response(destination_folder_path, label, list_of_num, data_file):
    label = label.replace("/", "_")

    os.makedirs(destination_folder_path, exist_ok=True)
    file_path = os.path.join(destination_folder_path, f"{label}.txt")

    # Read all lines from source file
    with open(data_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data_to_save = []

    # 1-based indexing
    for n in list_of_num:
        if isinstance(n, int) and 1 <= n <= len(lines):
            data_to_save.append(lines[n - 1])  # convert to 0-based index

    # Append extracted lines
    with open(file_path, "a", encoding="utf-8") as f:
        f.writelines(data_to_save)

def run(meta_data):
    for a_dict in meta_data:
        type = a_dict["type"]
        level = a_dict["level"]
        data_file = a_dict["data"]
        category = read_categories(a_dict["category"])
        destination_folder = a_dict["bucket"]

        parse = call_gpt_categories(data_file, category)
        response = validate_response(parse)

        for item in response.get("assignments", []):
            save_response(destination_folder, item["category"], item["lines"], data_file)

if __name__ == "__main__":
    bootstrap()
    meta_data = get_meta_data()
    run(meta_data)