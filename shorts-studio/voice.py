"""Portable Kokoro adapter used outside the preconfigured cloud workspace."""
from pathlib import Path
import re
import numpy as np
from kokoro_onnx import Kokoro

MODEL = Path(__file__).resolve().parent/'models/kokoro-v1.0.onnx'
VOICES = Path(__file__).resolve().parent/'models/voices-v1.0.bin'


def resolve_voice(model, name):
    return name, ('en-gb' if name.startswith('b') else 'en-us')


def split_script(text):
    return [[s.strip() for s in re.split(r'(?<=[.!?])\s+', paragraph) if s.strip()]
            for paragraph in text.splitlines() if paragraph.strip()]


def synth(model, text, style, lang, speed):
    audio, rate = model.create(text, voice=style, lang=lang, speed=speed)
    return np.asarray(audio, dtype=np.float32), rate


def silence(rate, duration):
    return np.zeros(int(rate*duration), dtype=np.float32)


def srt_time(seconds):
    ms = round(seconds*1000)
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
