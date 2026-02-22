import os
import time
from openai import OpenAI

PATH_TO_FRENCH_VOCAB_FOLDER = "/Users/zakick/desktop/french_code/output/vocab"
PATH_TO_FRENCH_CONVERSATION_FOLDER = "/Users/zakick/desktop/french_code/output/conversation"
PATH_TO_FRENCH_VOCAB_CATEGORIES_FOLDER = "/Users/zakick/Desktop/french_code/output/category/vocab"
PATH_TO_FRENCH_CONVERSATION_CATEGORIES_FOLDER = "/Users/zakick/Desktop/french_code/output/category/conversation"

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in your environment.")
client = OpenAI(api_key=api_key)

def get_txt_path(root_folder: str):
    txt_dict = {}
    for french_level_file in os.listdir(root_folder):
        if french_level_file.startswith("."):
            continue

        file_path = os.path.join(root_folder, french_level_file)

        if not os.path.isfile(file_path):
            continue

        if french_level_file.endswith(".txt"):
            french_level = french_level_file[:-4]
        else:
            continue
        
        txt_dict[french_level] = file_path

    return txt_dict

def call_gpt_vocab_categories(txt_file_path):
    # Read the .txt file
    with open(txt_file_path, "r", encoding="utf-8") as f:
        text_content = f.read()

    # Send to OpenAI
    response = client.responses.create(
        model="gpt-4o-mini", 
        prompt={
            "id": "",
            "version": "3"
        },
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": text_content}]
            }
        ]
    )

    return response.output_text or ""

def call_gpt_conversation_categories(txt_file_path):
    # Read the .txt file
    with open(txt_file_path, "r", encoding="utf-8") as f:
        text_content = f.read()

    # Send to OpenAI
    response = client.responses.create(
        model="gpt-4o-mini", 
        prompt={
            "id": "pmpt_6994b8e3d1d48197ab8911979991d57509cdae83d3d3cafe",
            "version": "2"
        },
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": text_content}]
            }
        ]
    )

    return response.output_text or ""

def validate_response(text):
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

def run_vocal_category():
    txt_dict = get_txt_path(PATH_TO_FRENCH_VOCAB_FOLDER)
    
    for level, txt in txt_dict.items():
        parsed = call_gpt_vocab_categories(txt)
        lines = validate_response(parsed)

        if lines:
            save_responce(PATH_TO_FRENCH_VOCAB_CATEGORIES_FOLDER, level, lines)
        
        time.sleep(1)

def run_conversation_category():
    txt_dict = get_txt_path(PATH_TO_FRENCH_CONVERSATION_FOLDER)
    
    for level, txt in txt_dict.items():
        parsed = call_gpt_conversation_categories(txt)
        lines = validate_response(parsed)

        if lines:
            save_responce(PATH_TO_FRENCH_CONVERSATION_CATEGORIES_FOLDER, level, lines)
        
        time.sleep(1)

if __name__ == "__main__":
    # run_vocal_category()
    # run_conversation_category()
    print("hello world")