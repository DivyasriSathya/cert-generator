import requests

API_KEY = "AIzaSyCkDmdbw_76Ee37snKFwB4Sytg2EbetKng"  # Replace with your actual Gemini API key
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

def generate_message(name, event, cert_type, event_date):
    prompt = (
        f"You are a formal certificate generator for a university. Generate a polished, impressive 3-line message in a formal tone.\n"
        f"Line 1: Begin with 'This is to certify that {name} from GSSSIETW' and formally state their role as a {cert_type.lower()} in the event '{event}'.\n"
        f"Line 2: Use a more elegant phrase than 'event was held' — e.g., 'conducted on', 'organized on', followed by {event_date}.\n"
        f"Line 3: Write a highly motivational, certificate-worthy sentence to inspire the participant — elegant and unique, less than 15 words.\n"
        f"Only return the message with 3 clean lines separated by newlines — no headings, commentary, or extra output."
    )

    data = {
        "contents": [
            {
                "parts": [
                    { "text": prompt }
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        raw_text = result['candidates'][0]['content']['parts'][0]['text']

        # Clean any unintended Gemini explanations
        lines = raw_text.strip().split("\n")
        clean_lines = [line.strip() for line in lines if not line.lower().startswith("here's")]
        return "\n".join(clean_lines[:3])

    except Exception as e:
        print(f"❌ Gemini API call failed: {e}")
        return (
            f"This is to certify that {name} from GSSSIETW has demonstrated excellence as a {cert_type.lower()} in the event '{event}'.\n"
            f"The event was conducted on {event_date}.\n"
            f"Your pursuit of greatness sets you apart — continue reaching higher."
        )
