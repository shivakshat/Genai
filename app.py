import streamlit as st
import google.generativeai as genai
# from datetime import datetime
# import csv
# import re
# import os
# Configure Gemini API
Api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=Api_key)

model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

st.title("Vocabulary Builder")

# User input
word = st.text_input("Enter a word")

if st.button("Get Meaning"):

    if word.strip() == "":
        st.warning("Please enter a word.")
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
            csv_file_path = "words.csv"

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

            st.success("Data saved to CSV.")

        else:
            st.error("Could not parse model response.")
            st.text(text)

st.divider()

csv_file_path = "words.csv"
if os.path.isfile(csv_file_path):
    with open(csv_file_path, "rb") as file:
        st.download_button(
            label="Download Vocabulary CSV",
            data=file,
            file_name="vocabulary.csv",
            mime="text/csv"
        )