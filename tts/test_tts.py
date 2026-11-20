import os
import subprocess
from datetime import datetime
from google.cloud import texttospeech


def play_audio(file_path: str) -> None:
    """Plays an MP3 file through Windows audio directly from WSL."""
    # Convert WSL Linux path (e.g. /home/user/...) to Windows path (\\wsl.localhost\...)
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
    print("Initializing Gemini Text-to-Speech client...")
    client = texttospeech.TextToSpeechClient()

    output_dir = "tts_outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Available Gemini prebuilt voices: Kore, Aoede, Charon, Callirrhoe, Fenrir, Puck
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="Kore",
        model_name="gemini-2.5-flash-tts",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    print("\n=== Gemini TTS Interactive Console ===")
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

            synthesis_input = texttospeech.SynthesisInput(
                text=text,
                prompt=style_prompt if style_prompt else None,
            )

            print("Synthesizing audio...")
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"speech_{timestamp}.mp3")

            with open(filename, "wb") as out:
                out.write(response.audio_content)

            print(f"Saved to {filename} — Playing now...")
            play_audio(filename)
            print("Done.\n")

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n[Error] {e}\n")


if __name__ == "__main__":
    main()
