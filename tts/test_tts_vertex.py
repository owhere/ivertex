import os
import subprocess
import wave
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from the script's directory and override any pre-existing shell variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "eu")
MODEL_ID = os.getenv("GEMINI_TTS_MODEL", "gemini-3.8-flash-lite-tts")
VOICE_NAME = os.getenv("GEMINI_TTS_VOICE", "Kore")
DELETE_AFTER_PLAY = os.getenv("DELETE_AFTER_PLAY", "false").lower() == "true"


def save_pcm_to_wav(pcm_bytes: bytes, file_path: str) -> None:
    """Wraps raw 24kHz 16-bit mono PCM audio from Vertex AI into a playable WAV file."""
    with wave.open(file_path, "wb") as wf:
        wf.setnchannels(1)       # Mono
        wf.setsampwidth(2)       # 16-bit (2 bytes)
        wf.setframerate(24000)   # 24 kHz
        wf.writeframes(pcm_bytes)


def play_audio_wsl(file_path: str) -> None:
    """Plays a WAV file through Windows audio directly from WSL."""
    win_path = subprocess.check_output(["wslpath", "-w", os.path.abspath(file_path)]).decode().strip()

    ps_script = f"""
    Add-Type -AssemblyName presentationCore
    $player = New-Object System.Windows.Media.MediaPlayer
    $player.Open([Uri]"{win_path}")
    $player.Play()
    Start-Sleep -Milliseconds 500
    while ($player.NaturalDuration.HasTimeSpan -eq $false) {{ Start-Sleep -Milliseconds 100 }}
    $duration = $player.NaturalDuration.TimeSpan.TotalSeconds
    Start-Sleep -Seconds $duration
    $player.Close()
    """
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_script], check=True)


def main():
    if not PROJECT_ID:
        print("[Error] GOOGLE_CLOUD_PROJECT is missing. Please define it in your .env file.")
        return

    print(f"Initializing Vertex AI client (Project: {PROJECT_ID}, Region: {LOCATION}, Model: {MODEL_ID}, Voice: {VOICE_NAME})...")
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

    output_dir = Path(__file__).resolve().parent / "tts_outputs"
    output_dir.mkdir(exist_ok=True)

    print("\n=== Vertex AI Gemini-TTS Interactive Console (Fixed) ===")
    print("Type your text and press Enter to generate and play speech.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            text = input("Text to speak > ").strip()
            if not text:
                continue
            if text.lower() in {"quit", "exit"}:
                print("Exiting...")
                break

            style_prompt = input("Style/tone prompt (optional, press Enter to skip) > ").strip()
            full_prompt = f"{style_prompt}: {text}" if style_prompt else text

            print("Synthesizing audio via Vertex AI...")
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=VOICE_NAME
                            )
                        )
                    ),
                ),
            )

            audio_bytes = response.candidates[0].content.parts[0].inline_data.data

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"vertex_speech_{timestamp}.wav"

            save_pcm_to_wav(audio_bytes, str(filename))
            print(f"Saved to {filename} — Playing now...")

            play_audio_wsl(str(filename))

            if DELETE_AFTER_PLAY:
                filename.unlink(missing_ok=True)
                print("Deleted local audio file (GDPR cleanup).\n")
            else:
                print("Done.\n")

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n[Error] {e}\n")


if __name__ == "__main__":
    main()
