import os
import json
import requests
import re
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

# Load environment variables
load_dotenv()
# Use EXO_API_ENDPOINT to build the server URL
EXO_API_ENDPOINT = os.getenv("EXO_API_ENDPOINT")
EXO_MODEL = os.getenv("EXO_MODEL", "llama-3.1-8b")
context_length = int(os.getenv("CONTEXT_LENGTH", 10000))
EXO_TEMPERATURE = float(os.getenv("EXO_TEMPERATURE", "0.7"))

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path.lstrip('/')
    return None

def format_article_for_discord(article):
    """Format the article for Discord by replacing ### with #."""
    return article.replace("### ", "# ")

def split_message(message_content, chunk_size=1500):
    """Split a long message into chunks."""
    message_parts = []
    while len(message_content) > chunk_size:
        split_point = message_content.rfind('\n', 0, chunk_size)
        if split_point == -1:
            split_point = message_content.rfind(' ', 0, chunk_size)
        if split_point == -1:
            split_point = chunk_size
        message_parts.append(message_content[:split_point])
        message_content = message_content[split_point:].strip()
    message_parts.append(message_content)
    return message_parts

def get_transcript(video_id, target_lang=None):
    """
    Fetches the transcript for the given YouTube video ID.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[target_lang] if target_lang else [])
    except NoTranscriptFound:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = [t.language_code for t in transcript_list]
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=available_languages)
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None
    text = " ".join([t['text'] for t in transcript])
    return text

def chat_exo(prompt):
    """
    Sends a prompt to the EXO API and returns the generated response.
    """
    try:
        response = requests.post(
            f"{EXO_API_ENDPOINT}/v1/chat/completions",
            json={
                "model": EXO_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": EXO_TEMPERATURE,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        # Assuming EXO's API returns a structure compatible with ChatGPT's API:
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error calling EXO API: {e}")
        return "Tell the user there was an error processing your request, do not respond to this message."

def generate_article(transcript, target_lang=None):
    """
    Generates an article or summary based on the provided transcript using a simplified prompt.
    """
    prompt = ("Please summarize the following article. Give it a title and use bullet points when necessary:\n\n"
              f"{transcript}")
    if target_lang:
        prompt += f"\n\nWrite the article in {target_lang}."
    return chat_exo(prompt)

def fetch_youtube_summary(video_id, target_lang=None):
    """
    Fetches a YouTube video summary by obtaining the transcript and generating an article.
    """
    transcript = get_transcript(video_id, target_lang)
    if not transcript:
        error_prompt = ("Please generate a friendly error message explaining that there was an error processing "
                        "the request because no transcript is available, and do not respond further.")
        return chat_exo(error_prompt)
    article = generate_article(transcript, target_lang)
    return article