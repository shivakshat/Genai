import streamlit as st
import google.generativeai as genai
from datetime import datetime
import csv
import re
import os
import io
# Configure Gemini API
# print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
Api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=Api_key)

model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

st.title("Vocabulary Builder")

# Initialize session state for user's words
if "user_words" not in st.session_state:
    st.session_state.user_words = []

# User input
word = st.text_input("Enter a word")

if st.button("Get Meaning"):

    if word.strip() == "":
        st.warning("Please enter a word.")
    else:
        word_to_check = word.strip().lower()
        word_exists = False
        csv_file_path = "words.csv"
        
        if os.path.isfile(csv_file_path):
            with open(csv_file_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("word", "").strip().lower() == word_to_check:
                        word_exists = True
                        break
        
        if word_exists:
            st.info(f"The word '{word.strip()}' is already in your vocabulary!")
        else:
            prompt = f"""
            Return ONLY in this exact format:

            part of speech='',
            meaning='',
            example sentence=''

            Word: {word}
            """

            response = model.generate_content(prompt)

            text = response.text.strip()

            # Regex extraction
            match = re.search(
                r"part of speech\s*=\s*['\"](.*?)['\"]\s*,?\s*"
                r"meaning\s*=\s*['\"](.*?)['\"]\s*,?\s*"
                r"example sentence\s*=\s*['\"](.*?)['\"]",
                text,
                re.IGNORECASE | re.DOTALL
            )

            if match:

                data = {
                    "word": word,
                    # x = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    "date added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "part of speech": match.group(1).strip(),
                    "meaning": match.group(2).strip(),
                    "example sentence": match.group(3).strip()
                }

                # Display on screen
                st.subheader("Result")
                st.write(f"**Word:** {data['word']}")
                st.write(f"**Part of Speech:** {data['part of speech']}")
                st.write(f"**Meaning:** {data['meaning']}")
                st.write(f"**Example Sentence:** {data['example sentence']}")

                # CSV saving
                fieldnames = [
                    "word",
                    "date added",
                    "part of speech",
                    "meaning",
                    "example sentence"
                ]

                file_exists = os.path.isfile(csv_file_path)
                file_is_empty = (
                    not file_exists or os.path.getsize(csv_file_path) == 0
                )

                with open(csv_file_path, "a", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)

                    if file_is_empty:
                        writer.writeheader()

                    writer.writerow(data)

                st.session_state.user_words.append(data)

                st.success("Data saved to CSV.")

            else:
                st.error("Could not parse model response.")
                st.text(text)

st.divider()

if os.path.exists("words.csv"):
    with open("words.csv", "rb") as f:
        csv_data = f.read()
    
    custom_file_name = st.text_input("Enter custom file name (without .csv):", value="my_vocabulary")
    file_name_to_save = f"{custom_file_name}.csv" if custom_file_name else "my_vocabulary.csv"
    
    st.download_button(
        label="Download All Saved Words (CSV)",
        data=csv_data,
        file_name=file_name_to_save,
        mime="text/csv"
    )
