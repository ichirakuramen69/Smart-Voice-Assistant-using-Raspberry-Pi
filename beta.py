#!/usr/bin/env python3
import os, sys, time, json, queue, threading, signal, subprocess, tempfile, logging, requests
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from gpiozero import LED, PWMOutputDevice
import time
from datetime import datetime

# Optional LLM
try:
    import google.generativeai as genai
    has_genai = True
except ImportError:
    has_genai = False

# ---------------- CONFIG ----------------
os.environ["VOSK_LOG_LEVEL"] = "0"
logging.basicConfig(level=logging.WARNING)

VOSK_MODEL_PATH   = "/home/pi/vosk-model-small-en-us-0.15"
SAMPLE_RATE       = 48000
BLOCK_SIZE        = 24000
WAKE_WORD         = "assistant"
SILENCE_TIMEOUT   = 2.0
MIN_CONFIDENCE    = 0.80

LED1_PIN, LED2_PIN, SERVO_PIN = 17, 26, 18
servo_speed, SERVO_MIN, SERVO_MAX = 7.5, 5.0, 10.0

GEMINI_MODEL_NAME = "gemini-1.5-flash"
RESPONSE_TYPE = "respond short with human like sentences with simple grammar and syntax"
RHASSPY_TTS_URL   = "http://localhost:12101/api/text-to-speech"
RHASSPY_INTENT_URL= "http://localhost:12101/api/text-to-intent"

led1 = LED(LED1_PIN)
led2 = LED(LED2_PIN)
servo = PWMOutputDevice(SERVO_PIN, frequency=50); servo.value = 0

# ---- Global state ----
online_llm = False
cmd_mode = False
cmd_buf = ""
last_spk = 0
blinking = False

# --- Recording mode state ---
recording_mode = False
recorded_text = []
recording_filename = None

# -------------- Gemini ------------------
if has_genai and os.environ.get("GOOGLE_API_KEY"):
    try:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        online_llm = True
        print("✅ Gemini API ready.")
    except Exception as e:
        print("⚠️ Gemini setup failed:", e)
        online_llm = False
else:
    print("ℹ️ Running in offline mode (no Google API key)")

# -------------- TTS ---------------------
def speak(text:str):
    if not text: return
    try:
        subprocess.run(["pkill","-f","aplay"], stderr=subprocess.DEVNULL)
        r = requests.post(RHASSPY_TTS_URL,
                          headers={"Content-Type":"text/plain","Accept":"audio/wav"},
                          data=text.encode(), timeout=10); r.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(r.content); tmp=f.name
        # subprocess.run(["aplay","-D","plughw:2,0", tmp], check=True)
        os.remove(tmp)
    except Exception as e:
        print("TTS error:", e)

# ------------- Blink --------------------
def _blink():
    while blinking:
        led2.toggle(); time.sleep(0.1)
def start_blink():
    global blinking
    blinking = True
    threading.Thread(target=_blink,daemon=True).start()
def stop_blink():
    global blinking
    blinking = False; led2.off()

# ------------- Cleanup ------------------
def cleanup(*_):
    stop_blink(); led1.off(); led2.off(); servo.value=0; servo.close(); sys.exit(0)
signal.signal(signal.SIGINT, cleanup)

# ---------- Intent Execution -----------
def execute_intent(intent:str):
    global servo_speed
    if intent=="TurnOnLight":
        stop_blink(); led2.on();  speak("LED two turned on")
    elif intent=="TurnOffLight":
        stop_blink(); led2.off(); speak("LED two turned off")
    elif intent=="BlinkLight":
        start_blink();            speak("LED two blinking")
    elif intent=="TurnOnFan":
        servo.value = servo_speed/100; speak(f"Fan on at {servo_speed:.1f}")
    elif intent=="TurnOffFan":
        servo.value = 0;          speak("Fan turned off")
    elif intent=="IncreaseSpeed":
        if servo_speed < SERVO_MAX:
            servo_speed = min(SERVO_MAX, servo_speed + 0.5)
            servo.value = servo_speed/100
            speak(f"Increased fan to {servo_speed:.1f}")
        else: speak("Fan already at max.")
    elif intent=="DecreaseSpeed":
        if servo_speed > SERVO_MIN:
            servo_speed = max(SERVO_MIN, servo_speed - 0.5)
            servo.value = servo_speed/100
            speak(f"Decreased fan to {servo_speed:.1f}")
        else: speak("Fan already at min.")
    else:
        speak("Unknown command")

# -------- Gemini Fallback -------------
def gemini_reply(prompt):
    try:
        rep = gemini_model.generate_content(prompt + RESPONSE_TYPE,
                generation_config=genai.GenerationConfig(
                    temperature=0.5, max_output_tokens=256))
        print(rep.text)
        return rep.text
    except Exception as e:
        print("Gemini error:", e); return None

# -------------- Vosk -------------------
model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
audio_q = queue.Queue()

def audio_cb(indata, frames, t, status):
    audio_q.put(bytes(indata))

# ---------- Command Logic --------------
def process_command(text):
    global cmd_mode, cmd_buf, recording_mode, recorded_text, recording_filename
    print("\n🔹 Command →", text)
    intent, conf = None, 0
    # --- Recording mode enable/disable logic ---
    if text.strip().lower() == "enable recording mode" or text.strip().lower() == "enable recording mod" :
        if not recording_mode:
            recording_mode = True
            recorded_text = []
            recording_filename = f"recording_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.txt"
            speak("Recording mode enabled. All speech will be saved.")
        else:
            speak("Recording mode is already enabled.")
        cmd_mode = False
        cmd_buf = ""
        recognizer.Reset()
        with audio_q.mutex: audio_q.queue.clear()
        return
        
    elif text.strip().lower() == "disable recording mode":
        if recording_mode:
            recording_mode = False
            # Save recorded text to file
            try:
                with open(recording_filename or f"recording_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.txt", "w") as f:
                    f.write("\n".join(recorded_text))
                speak(f"Recording mode disabled. Text saved to {recording_filename}.")
            except Exception as e:
                speak("Error saving recording.")
        else:
            speak("Recording mode is not enabled.")
        cmd_mode = False
        cmd_buf = ""
        recognizer.Reset()
        with audio_q.mutex: audio_q.queue.clear()
        return
    # --- End recording mode logic ---
    try:
        r = requests.post(RHASSPY_INTENT_URL,
                          headers={"Content-Type":"text/plain"},
                          data=text, timeout=5).json()
        intent = r.get("intent", {}).get("name")
        conf   = r.get("intent", {}).get("confidence", 0)
    except Exception as e:
        print("Rhasspy intent error:", e)

    if intent and conf >= MIN_CONFIDENCE:
        print(f"✅ Intent '{intent}' (conf={conf:.2f})")
        execute_intent(intent)
    elif online_llm:
        reply = gemini_reply(text) or "Sorry, I didn't understand."
        speak(reply)
    else:
        speak("Sorry, I didn't understand.")

    # Reset
    cmd_mode = False
    cmd_buf = ""
    recognizer.Reset()
    with audio_q.mutex: audio_q.queue.clear()

# --------------- MAIN ------------------
def main():
    global cmd_mode, cmd_buf, last_spk, recording_mode, recorded_text
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE,
                           dtype='int16', channels=1, device=1,
                           callback=audio_cb):
        print(f"🎧 Say '{WAKE_WORD}' to issue a command")
        while True:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())
                text = res.get("text","").strip().lower()
                if not text: continue
                print("📝", text)
                if recording_mode:
                    recorded_text.append(text)
                if not cmd_mode:
                    words = text.split()
                    if words and words[0] == WAKE_WORD:
                        cmd_mode = True
                        cmd_buf = " ".join(words[1:]).strip()
                        last_spk = time.time()
                        led1.on(); recognizer.Reset()
                else:
                    cmd_buf = (cmd_buf + " " + text).strip()
                    last_spk = time.time()
            if cmd_mode and time.time() - last_spk > SILENCE_TIMEOUT:
                led1.off()
                if cmd_buf:
                    process_command(cmd_buf)

if __name__ == "__main__":
    main()