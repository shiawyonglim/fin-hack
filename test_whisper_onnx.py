from optimum.onnxruntime import ORTModelForSpeechSeq2Seq
from transformers import AutoProcessor, pipeline
import librosa
import time

model_id = "whisper-tiny-onnx"

print("Loading ONNX model and processor (this proves the models load correctly in ONNX)...")
model = ORTModelForSpeechSeq2Seq.from_pretrained(model_id)
processor = AutoProcessor.from_pretrained(model_id)

print("Setting up inference pipeline...")
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor
)

print("Loading synthesized audio file...")
# Whisper expects 16kHz sampling rate
audio, sr = librosa.load("sample_voice.wav", sr=16000)

print(f"Loaded audio: {len(audio)/sr:.2f} seconds")

print("\n--- Starting Translation ---")
start_time = time.time()
result = pipe(audio)
end_time = time.time()

print(f"Transcription   : {result['text'].strip()}")
print(f"Inference Time  : {end_time - start_time:.4f} seconds!")
print("--- End of Translation ---")
