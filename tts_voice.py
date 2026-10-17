"""
tts_voice.py — Đọc kịch bản tiếng Anh bằng Kokoro (miễn phí, chạy trên máy, dùng thương mại được).

Đầu vào : file kịch bản .txt (văn xuôi thuần — như Stage 2 của form prompt xuất ra)
Đầu ra  (cùng thư mục với kịch bản):
    <tên>_voice.wav        giọng đọc
    <tên>_timestamps.txt   "[mm:ss] câu" — dán thẳng vào Claude ở Stage 3
    <tên>_timeline.json    mốc thời gian chính xác (cho công cụ ghép video)
    <tên>.srt              phụ đề (tùy chọn, dùng trong CapCut)

Ví dụ:
    python tts_voice.py script.txt --voice af_heart --speed 0.95
    python tts_voice.py script.txt --voice "am_michael:60,am_fenrir:40"   (trộn 2 giọng)
    python tts_voice.py --samples                                          (nghe thử các giọng)
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "kokoro-v1.0.onnx"
VOICES = HERE / "models" / "voices-v1.0.bin"

# Giọng tốt nhất theo bảng chấm điểm của Kokoro (VOICES.md)
SAMPLE_VOICES = [
    "af_heart", "af_bella", "af_nicole", "bf_emma",
    "am_michael", "am_fenrir", "am_puck", "bm_george", "bm_fable",
    "am_michael:50,am_fenrir:50", "af_heart:60,af_bella:40",
]
SAMPLE_TEXT = (
    "You check your phone before you even open your eyes. Not because you want to. "
    "Because somewhere deep in your brain, a habit has learned that something might be waiting for you. "
    "Psychologists call this a variable reward. It is the same trick that keeps people pulling the lever "
    "on a slot machine. So why does one tiny red dot feel almost impossible to ignore?"
)

PAUSE_SENTENCE = 0.25   # giây nghỉ giữa 2 câu
PAUSE_PARAGRAPH = 0.6   # giây nghỉ giữa 2 đoạn
LEAD_IN = 0.2           # giây im lặng đầu file

# ---------- Tách câu ----------
DOT = "․"  # ký tự tạm thay cho dấu chấm không phải cuối câu
ABBREV = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "St.", "Jr.", "Sr.", "vs.", "etc.",
          "e.g.", "i.e.", "a.m.", "p.m.", "U.S.", "U.K.", "B.C.", "A.D."]


def protect(text):
    for a in ABBREV:
        text = text.replace(a, a.replace(".", DOT))
    text = re.sub(r"(?<=\d)\.(?=\d)", DOT, text)                       # 3.5
    text = re.sub(r"\b([A-Z])\.(?= ?[A-Z]\.)", r"\1" + DOT, text)      # B. F.
    text = re.sub(r"(?<=\b[A-Z]" + DOT + r" )([A-Z])\.", r"\1" + DOT, text)
    return text


def split_script(raw):
    """Trả về list các đoạn, mỗi đoạn là list câu."""
    paragraphs = []
    for para in re.split(r"\n+", raw):
        para = re.sub(r"\s+", " ", para).strip()
        if not para:
            continue
        para = protect(para)
        sents = re.findall(r"[^.!?]+(?:[.!?]+[\"'”’)\]]*|$)", para)
        sents = [s.strip().replace(DOT, ".") for s in sents if s.strip()]
        if sents:
            paragraphs.append(sents)
    return paragraphs


# ---------- Giọng ----------
def resolve_voice(kokoro, spec):
    """'af_heart' hoặc trộn 'am_michael:60,am_fenrir:40'. Trả về (style, lang)."""
    names = []
    if "," in spec or ":" in spec:
        parts, total = [], 0.0
        for p in spec.split(","):
            name, _, w = p.partition(":")
            w = float(w or 1)
            parts.append((name.strip(), w))
            total += w
            names.append(name.strip())
        style = sum(kokoro.get_voice_style(n) * (w / total) for n, w in parts)
    else:
        style = spec.strip()
        names.append(style)
    lang = "en-gb" if names[0].startswith("b") else "en-us"
    return style, lang


def silence(sr, sec):
    return np.zeros(int(sr * sec), dtype=np.float32)


# ---------- Định dạng thời gian ----------
def stamp(t):
    t = int(t)
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"[{h}:{m:02d}:{s:02d}]" if h else f"[{m:02d}:{s:02d}]"


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ---------- Gộp câu thành dòng timestamp ----------
def group_lines(segs, min_sec):
    """Gộp các câu quá ngắn để mỗi dòng (= 1 ảnh) dài ít nhất min_sec giây."""
    lines, cur = [], None
    for seg in segs:
        if cur is None:
            cur = dict(start=seg["start"], end=seg["end"], text=seg["text"])
        else:
            cur["end"] = seg["end"]
            cur["text"] += " " + seg["text"]
        dur = cur["end"] - cur["start"]
        if dur >= min_sec or (seg["para_end"] and dur >= min_sec * 0.5):
            lines.append(cur)
            cur = None
    if cur:
        if lines and cur["end"] - cur["start"] < min_sec * 0.5:
            lines[-1]["end"] = cur["end"]
            lines[-1]["text"] += " " + cur["text"]
        else:
            lines.append(cur)
    return lines


def synth(kokoro, text, style, lang, speed):
    audio, sr = kokoro.create(text, voice=style, speed=speed, lang=lang)
    return np.asarray(audio, dtype=np.float32), sr


def run_script(kokoro, script_path, voice, speed, min_sec):
    raw = script_path.read_text(encoding="utf-8-sig")
    paragraphs = split_script(raw)
    total = sum(len(p) for p in paragraphs)
    if total == 0:
        sys.exit("Kịch bản trống.")
    style, lang = resolve_voice(kokoro, voice)
    print(f"Giọng: {voice} | tốc độ {speed} | {total} câu, {len(paragraphs)} đoạn")

    chunks, segs, t, sr, done = [], [], 0.0, 24000, 0
    t0 = time.time()
    for pi, sents in enumerate(paragraphs):
        for si, s in enumerate(sents):
            audio, sr = synth(kokoro, s, style, lang, speed)
            if not chunks:
                chunks.append(silence(sr, LEAD_IN))
                t = LEAD_IN
            start = t
            chunks.append(audio)
            t += len(audio) / sr
            is_para_end = si == len(sents) - 1
            segs.append(dict(start=start, end=t, text=s, para_end=is_para_end))
            gap = PAUSE_PARAGRAPH if is_para_end else PAUSE_SENTENCE
            chunks.append(silence(sr, gap))
            t += gap
            done += 1
            if done % 10 == 0 or done == total:
                el = time.time() - t0
                eta = el / done * (total - done)
                print(f"  {done}/{total} câu — đã đọc {stamp(t)} — còn ~{int(eta)} giây")

    audio = np.concatenate(chunks)
    duration = len(audio) / sr
    stem = script_path.stem
    out_dir = script_path.parent
    wav = out_dir / f"{stem}_voice.wav"
    sf.write(wav, audio, sr, subtype="PCM_16")

    lines = group_lines(segs, min_sec)
    for i, ln in enumerate(lines):
        ln["end"] = lines[i + 1]["start"] if i + 1 < len(lines) else duration

    (out_dir / f"{stem}_timestamps.txt").write_text(
        "\n".join(f"{stamp(ln['start'])} {ln['text']}" for ln in lines) + "\n", encoding="utf-8")
    (out_dir / f"{stem}_timeline.json").write_text(json.dumps({
        "audio": wav.name, "duration": round(duration, 3), "voice": voice, "speed": speed,
        "lines": [dict(index=i + 1, stamp=stamp(ln["start"]), start=round(ln["start"], 3),
                       end=round(ln["end"], 3), text=ln["text"]) for i, ln in enumerate(lines)],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / f"{stem}.srt").write_text("\n".join(
        f"{i + 1}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text']}\n"
        for i, s in enumerate(segs)), encoding="utf-8")

    print(f"\nXong trong {int(time.time() - t0)} giây. Độ dài audio: {stamp(duration)}"
          f" | {len(lines)} dòng timestamp (= {len(lines)} ảnh)")
    print(f"  Giọng đọc : {wav}")
    print(f"  Timestamps: {out_dir / (stem + '_timestamps.txt')}  <- dán vào Claude ở Stage 3")


def run_samples(kokoro, out_dir, speed):
    out_dir.mkdir(parents=True, exist_ok=True)
    for v in SAMPLE_VOICES:
        style, lang = resolve_voice(kokoro, v)
        t0 = time.time()
        audio, sr = synth(kokoro, SAMPLE_TEXT, style, lang, speed)
        name = v if ":" not in v else "tron_" + v.replace(":", "").replace(",", "_")
        path = out_dir / f"{name}.wav"
        sf.write(path, audio, sr, subtype="PCM_16")
        print(f"  {path.name:<32} {len(audio) / sr:5.1f}s audio, tạo trong {time.time() - t0:4.1f}s")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Đọc kịch bản tiếng Anh bằng Kokoro")
    ap.add_argument("script", nargs="?", help="file kịch bản .txt")
    ap.add_argument("--voice", default="af_heart", help="tên giọng, hoặc trộn: am_michael:60,am_fenrir:40")
    ap.add_argument("--speed", type=float, default=0.95, help="tốc độ đọc (1.0 = bình thường)")
    ap.add_argument("--min-sec", type=float, default=3.0, help="mỗi dòng timestamp dài tối thiểu (giây)")
    ap.add_argument("--samples", action="store_true", help="tạo file nghe thử các giọng")
    args = ap.parse_args()

    kokoro = Kokoro(str(MODEL), str(VOICES))
    if args.samples:
        run_samples(kokoro, HERE / "samples", args.speed)
    elif args.script:
        run_script(kokoro, Path(args.script).resolve(), args.voice, args.speed, args.min_sec)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
