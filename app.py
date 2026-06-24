import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import os
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Configure Gemini API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Updated prompt
PROMPT = """You are a YouTube video summarizer.
Summarize the following transcript into key bullet points (max 250 words).
Focus on clarity and important insights:
"""

def extract_transcript_details(youtube_video_url):
    try:
# CRITICAL: Strip out the exact 11-character video ID depending on standard or short URL formats
        if "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            st.error("Invalid YouTube URL")
            return None

        api = YouTubeTranscriptApi()
# IMPORTANT: Try fetching English captions first; if that fails, immediately fall back to Hindi
        try:
            transcript_data = api.fetch(video_id, languages=["en"])
        except Exception:
            try:
                transcript_data = api.fetch(video_id, languages=["hi"])
            except Exception:
                st.error("❌ No transcript available")
                return None
# Loop through the subtitle chunks and stitch them into a single clean paragraph
        transcript = " ".join([item.text for item in transcript_data])

        return transcript

    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Extract transcript
def generate_groq_content(transcript_text):
# Defining a primary fast model and a smarter backup model in case of rate limits
    models = [
        "llama-3.3-8b-instant",     
        "llama-3.3-70b-versatile"
    ]

    for model in models:
        try:
# Hit the Groq endpoint with the prompt and combined transcript text
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a YouTube video summarizer."},
                    {"role": "user", "content": PROMPT + transcript_text}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
# If the current model fails or throws a rate limit error, silently skip to the next one
            continue

    st.error("All models failed. Please check API or model names.")
    return None


# Generate summary using Gemini (UPDATED MODEL)
def generate_gemini_content(transcript_text):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=PROMPT + transcript_text
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"


# Streamlit UI
st.title("🎥 YouTube Transcript to Notes Converter")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    if "v=" in youtube_link:
        video_id = youtube_link.split("v=")[1].split("&")[0]
    elif "youtu.be/" in youtube_link:
        video_id = youtube_link.split("youtu.be/")[1].split("?")[0]
    else:
        video_id = None

    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", width="stretch")

if st.button("Get Detailed Notes"):
    if not youtube_link:
        st.warning("Please enter a valid YouTube link.")
    else:
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
# SAFETY GUARD: Hard crop the text at 15k characters to prevent blowing past the LLM's token context window
            if len(transcript_text) > 15000:
                transcript_text = transcript_text[:15000]
    # summary = generate_gemini_content(transcript_text)
            summary = generate_groq_content(transcript_text)
            st.markdown("## 📝 Detailed Notes:")
            st.write(summary)
            