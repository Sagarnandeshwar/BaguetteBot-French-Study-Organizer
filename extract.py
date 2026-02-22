import os
import base64
import time
from openai import OpenAI
import json


PATH_TO_FRENCH_VOCAB_SS = "/Users/zakick/desktop/french_backup/french_vocab"
PATH_TO_FRENCH_CONVERSATION_SS = "/Users/zakick/desktop/french_backup/french_coversation"
PATH_TO_FRENCH_VOCAB_FOLDER = "/Users/zakick/desktop/french_code/output/vocab"
PATH_TO_FRENCH_CONVERSATION_FOLDER = "/Users/zakick/desktop/french_code/output/conversation"

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in your environment.")
client = OpenAI(api_key=api_key)

def get_ss_path(root_folder: str):
    ss_dict = {}
    for french_level in os.listdir(root_folder):
        if french_level.startswith("."):
            continue

        level_path = os.path.join(root_folder, french_level)
        if not os.path.isdir(level_path):
            continue

        ss_path_list = []
        for name in os.listdir(level_path):
            if name.startswith("."):
                continue
            p = os.path.join(level_path, name)
            if os.path.isfile(p) and name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                ss_path_list.append(p)

        # ss_path_list.sort()
        ss_dict[french_level] = ss_path_list

    return ss_dict


def call_gpt_vocab(ss_path: str):
    with open(ss_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")

    response = client.responses.create(
        model="gpt-4o-mini",
        prompt={
            "id": "",
            "version": "3"
        },
        input=[{
            "role": "user",
            "content": [
                {"type": "input_image", "image_url": f"data:image/png;base64,{base64_image}"}
            ]
        }],
        text={
            "format": {
                "type": "json_schema",
                "name": "flashcards",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "cards": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "french": {"type": "string"},
                                    "english": {"type": "string"}
                                },
                                "required": ["french", "english"]
                            }
                        }
                    },
                    "required": ["cards"]
                }
            }
        }
    )

    return json.loads(response.output_text or "{}")


def call_gpt_conversation(ss_path: str):
    with open(ss_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")

    response = client.responses.create(
        model="gpt-4o-mini",
        prompt={
            "id": "pmpt_69948baacb648190bae6620cad0013a701c6e5cc75fc8cea",
            "version": "3"
        },
        input=[{
            "role": "user",
            "content": [
                {"type": "input_image", "image_url": f"data:image/png;base64,{base64_image}"}
            ]
        }], 
    )

    return response.output_text or ""

def validate_response_vocab(data):
    clean_lines = []

    if not isinstance(data, dict):
        return clean_lines
    cards = data.get("cards")
    if not isinstance(cards, list):
        return clean_lines

    for item in cards:
        if not isinstance(item, dict):
            continue
        french = str(item.get("french", "")).strip()
        english = str(item.get("english", "")).strip()
        if french and english:
            clean_lines.append(f"{french}\t{english}\n")  # newline here

    return clean_lines

def validate_response_conversation(text):
    clean_lines = []

    if not isinstance(text, str):
        return clean_lines

    # Normalize line endings
    t = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    if not t:
        return clean_lines

    lines = t.split("\n")

    for line in lines:
        s = line.strip()
        if not s:
            continue

        # Prevent accidental double newlines in file
        clean_lines.append(s + "\n")

    return clean_lines

def save_responce(folder_path, french_level, responce_data):
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{french_level}.txt")

    with open(file_path, "a", encoding="utf-8") as f:
        f.writelines(responce_data)

def run_vocab():
    ss_dict = get_ss_path(PATH_TO_FRENCH_VOCAB_SS)

    for level, images in ss_dict.items():
        total = len(images)
        print(f"\n Starting level {level} ({total} images)")

        for i, ss_path in enumerate(images, start=1):
            parsed = call_gpt_vocab(ss_path)
            lines = validate_response_vocab(parsed)

            if lines:
                save_responce(PATH_TO_FRENCH_VOCAB_FOLDER, level, lines)

            time.sleep(1)

            if i % 10 == 0 or i == total:
                print(f"Level {level}: {i}/{total} processed")

        print(f"Finished level {level}")


def run_conversation():
    ss_dict = get_ss_path(PATH_TO_FRENCH_CONVERSATION_SS)
    
    for level, images in ss_dict.items():
        total = len(images)
        print(f"\n Starting level {level} ({total} images)")

        for i, ss_path in enumerate(images, start=1):
            parsed = call_gpt_conversation(ss_path)
            lines = validate_response_conversation(parsed)

            if lines:
                save_responce(PATH_TO_FRENCH_CONVERSATION_FOLDER, level, lines)

            time.sleep(1)

            if i % 10 == 0 or i == total:
                print(f"Level {level}: {i}/{total} processed")

        print(f"Finished level {level}")

if __name__ == "__main__":
    # run_vocab()
    # run_conversation()
    print("hello world")