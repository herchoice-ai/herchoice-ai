"""Hausa speech in and out, using open-weight models.

* Speech-to-text: an open Whisper-family model (Whisper supports Hausa, language code "ha").
  Set HERCHOICE_ASR_MODEL to a Hausa fine-tuned checkpoint for better accuracy.
* Text-to-speech: Meta's open MMS-TTS Hausa voice ("facebook/mms-tts-hau").

Both are optional: install with `pip install -e ".[speech]"`. Without them, HerChoice works by text.
Models are loaded lazily, on first use, so the text service starts fast on small servers.
"""

from __future__ import annotations

import io
import os
from functools import lru_cache

ASR_MODEL = os.environ.get("HERCHOICE_ASR_MODEL", "openai/whisper-small")
TTS_MODEL = os.environ.get("HERCHOICE_TTS_MODEL", "facebook/mms-tts-hau")


class SpeechUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _asr():
    try:
        from transformers import pipeline
    except ImportError as e:
        raise SpeechUnavailable("Install speech extras: pip install -e '.[speech]'") from e
    return pipeline("automatic-speech-recognition", model=ASR_MODEL)


@lru_cache(maxsize=1)
def _tts():
    try:
        import torch
        from transformers import AutoTokenizer, VitsModel
    except ImportError as e:
        raise SpeechUnavailable("Install speech extras: pip install -e '.[speech]'") from e
    return AutoTokenizer.from_pretrained(TTS_MODEL), VitsModel.from_pretrained(TTS_MODEL), torch


def transcribe(audio: bytes, language: str = "ha") -> str:
    """Turn a voice note (any format ffmpeg can read) into text."""
    asr = _asr()
    kwargs = {"generate_kwargs": {"language": "hausa" if language == "ha" else "english", "task": "transcribe"}}
    return asr(audio, **kwargs)["text"].strip()


def synthesize(text: str) -> bytes:
    """Turn Hausa text into a WAV file (bytes) the user can listen to."""
    tokenizer, model, torch = _tts()
    import wave

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        waveform = model(**inputs).waveform[0].numpy()
    pcm = (waveform.clip(-1, 1) * 32767).astype("int16").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(model.config.sampling_rate)
        w.writeframes(pcm)
    return buf.getvalue()
