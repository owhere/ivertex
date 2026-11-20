# making sure this is run before running this script
# gcloud auth application-default set-quota-project your-gcp-project-id

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from dotenv import load_dotenv
import google.auth
import google.auth.transport.requests
from google import genai
from google.genai import types

# Load .env from the script's directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
TARGET_REGION = "europe-west2"  # London

CANDIDATE_TTS_MODELS = [
    "gemini-2.5-flash-tts",
    "gemini-2.5-pro-tts",
    "gemini-3.1-flash-tts-preview",
    "gemini-3.8-flash-lite-tts",
    "gemini-3.8-flash-tts",
]


def get_access_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def list_publisher_models(region: str, token: str) -> list[str]:
    """Queries the Vertex AI regional endpoint for all Google publisher models."""
    models = []
    page_token = None

    while True:
        url = f"https://{region}-aiplatform.googleapis.com/v1beta1/publishers/google/models?pageSize=100"
        if page_token:
            url += f"&pageToken={page_token}"

        req = urllib.request.Request(
              url,
              headers={
                "Authorization": f"Bearer {token}",
                "x-goog-user-project": PROJECT_ID,
              },
              )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[HTTP {e.code}] Failed to list models in {region}: {body}")
            return []

        for item in data.get("models", []):
            # Name format: publishers/google/models/<model_id>
            model_id = item.get("name", "").split("/")[-1]
            if model_id:
                models.append(model_id)

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return sorted(set(models))


def probe_tts_model(project_id: str, region: str, model_id: str) -> tuple[bool, str]:
    """Tests whether a specific TTS model can synthesize audio in the target region."""
    client = genai.Client(vertexai=True, project=project_id, location=region)
    try:
        response = client.models.generate_content(
            model=model_id,
            contents="Test",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                    )
                ),
            ),
        )
        audio_len = len(response.candidates[0].content.parts[0].inline_data.data)
        return True, f"AVAILABLE (returned {audio_len} audio bytes)"
    except Exception as e:
        err = str(e)
        if "404" in err or "NOT_FOUND" in err:
            return False, "NOT FOUND in europe-west2"
        if "403" in err or "PERMISSION_DENIED" in err:
            return False, "PERMISSION DENIED (check IAM/Org Policy)"
        return False, f"ERROR: {err.splitlines()[0]}"


def main():
    if not PROJECT_ID:
        print("[Error] GOOGLE_CLOUD_PROJECT is not set in .env or environment.")
        return

    print(f"Checking available models in {TARGET_REGION} (London) for project '{PROJECT_ID}'...\n")
    token = get_access_token()
    all_models = list_publisher_models(TARGET_REGION, token)

    tts_or_audio = [
        m for m in all_models
        if any(kw in m.lower() for kw in ("tts", "speech", "chirp", "audio", "live"))
    ]

    print(f"=== 1. Publisher Models Matching TTS/Speech/Audio in {TARGET_REGION} ===")
    if tts_or_audio:
        for m in tts_or_audio:
            print(f"  - {m}")
    else:
        print("  (None returned by the publisher list endpoint)")

    print(f"\n=== 2. All Gemini Models Listed in {TARGET_REGION} ===")
    gemini_models = [m for m in all_models if "gemini" in m.lower()]
    for m in gemini_models:
        print(f"  - {m}")

    print(f"\n=== 3. Live Synthesis Probe for Candidate Gemini-TTS Models in {TARGET_REGION} ===")
    # Combine known candidates with any discovered tts models
    models_to_probe = sorted(set(CANDIDATE_TTS_MODELS + [m for m in tts_or_audio if "tts" in m.lower()]))
    for model_id in models_to_probe:
        ok, status = probe_tts_model(PROJECT_ID, TARGET_REGION, model_id)
        marker = "[OK]" if ok else "[--]"
        print(f"  {marker} {model_id:<32} -> {status}")


if __name__ == "__main__":
    main()
