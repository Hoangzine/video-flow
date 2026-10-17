"""Offline English short-video renderer. No paid APIs or automatic posting."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import shutil

os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = Path(__file__).resolve().parent
if not os.environ.get('SHORTS_STANDALONE') and Path('/workspace/video-flow/tts_voice.py').is_file():
    sys.path.insert(0, '/workspace/video-flow')
    import tts_voice as tts
else:
    import voice as tts
if not os.environ.get('SHORTS_STANDALONE') and Path('/workspace/openshorts/ffmpeg_utils.py').is_file():
    sys.path.insert(0, '/workspace/openshorts')
    from ffmpeg_utils import video_encode_args, QUALITY_FAST, LOUDNORM_FILTER
else:
    QUALITY_FAST = 'quality_fast'
    LOUDNORM_FILTER = 'loudnorm=I=-14:TP=-2.0:LRA=11'
    def video_encode_args(_):
        return ['-c:v','libx264','-preset','fast','-crf','18']
if (BASE/'models/kokoro-v1.0.onnx').exists():
    tts.MODEL = BASE/'models/kokoro-v1.0.onnx'
    tts.VOICES = BASE/'models/voices-v1.0.bin'

VOICES = ['af_heart', 'af_bella', 'af_nicole', 'am_michael', 'am_fenrir', 'am_puck', 'bf_emma', 'bm_george', 'bm_fable']
FONT = next((p for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf'] if Path(p).exists()), 'DejaVuSans.ttf')
BOLD = next((p for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'] if Path(p).exists()), FONT)


def command(args):
    if args[0] == 'ffmpeg' and not shutil.which('ffmpeg'):
        import imageio_ffmpeg
        args = [imageio_ffmpeg.get_ffmpeg_exe(), *args[1:]]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-4000:])
    return r.stdout


def validate(project):
    if not isinstance(project.get('title'), str):
        raise ValueError('Tiêu đề phải là văn bản.')
    for field in ('description', 'hashtags'):
        if field in project and not isinstance(project[field], str):
            raise ValueError(f'{field} phải là văn bản.')
    sources = project.get('sources', [])
    if not isinstance(sources, list) or len(sources) > 30 or any(not isinstance(s, str) or len(s)>1000 for s in sources):
        raise ValueError('Nguồn phải là danh sách tối đa 30 dòng văn bản.')
    if project.get('voice', 'af_heart') not in VOICES:
        raise ValueError('Giọng không hợp lệ.')
    speed = float(project.get('speed', .95))
    if not math.isfinite(speed) or not .7 <= speed <= 1.3:
        raise ValueError('Tốc độ phải từ 0.7 đến 1.3.')
    scenes = project.get('scenes')
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= 40:
        raise ValueError('Cần từ 1 đến 40 cảnh.')
    if not str(project.get('title', '')).strip() or len(str(project['title'])) > 160:
        raise ValueError('Cần tiêu đề, tối đa 160 ký tự.')
    for scene in scenes:
        if not isinstance(scene, dict) or not isinstance(scene.get('text'), str) or not scene['text'].strip():
            raise ValueError('Mỗi cảnh phải có lời đọc.')
        if len(scene['text']) > 500:
            raise ValueError('Mỗi cảnh tối đa 500 ký tự.')
        if len(str(scene.get('heading', ''))) > 80:
            raise ValueError('Tiêu đề cảnh tối đa 80 ký tự.')
        if scene.get('image'):
            image = (BASE / str(scene['image'])).resolve()
            if not image.is_relative_to(BASE / 'uploads') or not image.is_file():
                raise ValueError('Ảnh phải được tải lên Studio trước.')
    if sum(len(s['text']) for s in scenes) > 12000:
        raise ValueError('Kịch bản tối đa 12000 ký tự.')
    return project


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def lines_fit(draw, text, ft, max_width):
    lines, line = [], ''
    for word in str(text).split():
        candidate = (line + ' ' + word).strip()
        if line and draw.textlength(candidate, font=ft) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def text_block(draw, text, y, size=64, color='#f3f6ff', max_width=810, bold=True):
    ft = font(size, bold)
    for line in lines_fit(draw, text, ft, max_width):
        draw.text((92, y), line, font=ft, fill=color)
        y += size * 1.22
    return y


def artwork(scene, index, total, path):
    """Original vector-style illustrations; user-supplied photos can replace them."""
    image = Image.new('RGB', (1080, 1920), '#0b1120')
    d = ImageDraw.Draw(image)
    accent = ['#75f5ce', '#95baff', '#f8c78e'][index % 3]
    for y in range(1920):
        v = y / 1920
        d.line((0, y, 1080, y), fill=(int(11 + 6*v), int(17 + 9*v), int(32 + 17*v)))
    for x in range(92, 1000, 64):
        for y in range(370, 1280, 64):
            d.ellipse((x, y, x+2, y+2), fill='#293246')
    d.rounded_rectangle((92, 170, 150, 178), radius=4, fill=accent)
    d.text((172, 153), 'A LITTLE MORE CURIOUS', font=font(23, True), fill=accent)
    text_block(d, scene.get('heading') or 'Look a little closer.', 255, size=70)
    kind = scene.get('visual', 'wave')
    if scene.get('image'):
        with Image.open(BASE / scene['image']) as src:
            photo = ImageOps.fit(src.convert('RGB'), (896, 760))
        image.paste(photo, (92, 540))
        d = ImageDraw.Draw(image)
    elif kind == 'phone':
        d.rounded_rectangle((345, 550, 735, 1200), radius=56, fill='#1e2b42', outline=accent, width=7)
        d.rounded_rectangle((372, 605, 708, 1120), radius=22, fill='#0b1120')
        d.ellipse((500, 1140, 580, 1180), fill='#425270')
        d.rounded_rectangle((470, 705, 610, 925), radius=70, fill=accent)
        d.arc((435, 800, 645, 980), 0, 180, fill='#f3f6ff', width=9)
        d.line((540, 980, 540, 1035), fill='#f3f6ff', width=9)
        d.line((495, 1035, 585, 1035), fill='#f3f6ff', width=9)
    elif kind in ('head', 'ear'):
        d.ellipse((310, 575, 760, 1030), fill='#22314a', outline=accent, width=7)
        d.polygon([(720, 760), (820, 850), (735, 885)], fill='#22314a')
        d.rounded_rectangle((390, 960, 625, 1170), radius=25, fill='#22314a')
        d.ellipse((460, 750, 610, 950), outline=accent, width=9)
        d.arc((485, 780, 590, 920), 210, 520, fill=accent, width=7)
        for r in (105, 155, 205):
            d.arc((540-r, 850-r, 540+r, 850+r), 170, 250, fill='#7595c3', width=5)
        d.ellipse((690, 735, 705, 750), fill='#f3f6ff')
    elif kind == 'compare':
        for x, label, amp in [(280, 'AIR', 55), (700, 'BONE', 110)]:
            d.rounded_rectangle((x-180, 630, x+180, 1130), radius=30, outline='#344863', width=3)
            d.text((x-90, 700), label, font=font(38, True), fill=accent)
            pts=[(x-145+t, 905 + math.sin(t/24)*amp) for t in range(291)]
            d.line(pts, fill=accent, width=7)
    elif kind == 'check':
        d.ellipse((300, 640, 780, 1120), fill='#183f3d', outline=accent, width=6)
        d.line([(415, 875), (510, 965), (680, 780)], fill=accent, width=24)
    else:
        for i in range(39):
            x = 130 + i*21
            h = 45 + abs(math.sin(i*.53))*180 + abs(math.cos(i*.19))*80
            d.rounded_rectangle((x, 875-h, x+10, 875+h), radius=5, fill=accent)
    if scene.get('label'):
        ft = font(32, True)
        for n, line in enumerate(lines_fit(d, scene['label'], ft, 820)[:2]):
            d.text((92, 1310+n*42), line, font=ft, fill=accent)
    d.rounded_rectangle((92, 1720, 920, 1726), radius=3, fill='#2d3c53')
    d.rounded_rectangle((92, 1720, 92+max(4,int(828*(index+1)/total)), 1726), radius=3, fill=accent)
    d.text((92, 1760), f'{index+1:02d} / {total:02d}', font=font(22), fill='#9cabc4')
    image.save(path)


def ass_time(t):
    cs = round(t*100)
    return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'


def subtitle_text(text):
    # Plain input cannot inject ASS override tags.
    clean = text.replace('\\', '/').replace('{', '(').replace('}', ')')
    return r'\N'.join(textwrap.wrap(clean, width=32))


def render(project, out, progress=print):
    validate(project)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    project = dict(project)
    (out/'project.json').write_text(json.dumps(project, ensure_ascii=False, indent=2))
    progress('Đang nạp mô hình Kokoro tại máy…')
    model = tts.Kokoro(str(tts.MODEL), str(tts.VOICES))
    style, lang = tts.resolve_voice(model, project.get('voice', 'af_heart'))
    chunks, timeline, captions, cursor, sr = [], [], [], 0., 24000
    for i, scene in enumerate(project['scenes']):
        progress(f'Đang tạo giọng cảnh {i+1}/{len(project["scenes"])}…')
        start = cursor
        for para in tts.split_script(scene['text']):
            for sentence in para:
                audio, sr = tts.synth(model, sentence, style, lang, float(project.get('speed', .95)))
                if len(audio) == 0 or not np.isfinite(audio).all():
                    raise RuntimeError('Mô hình trả về audio rỗng hoặc lỗi.')
                duration = len(audio)/sr
                captions.append({'start':cursor, 'end':cursor+duration, 'text':sentence})
                chunks.extend([audio, tts.silence(sr, .18)])
                cursor += duration+.18
        chunks.append(tts.silence(sr, .2))
        cursor += .2
        # Align scene boundaries to 30 fps so picture/audio cannot drift.
        pad = round((math.ceil(cursor*30)/30-cursor)*sr)
        if pad:
            chunks.append(np.zeros(pad, dtype=np.float32))
            cursor += pad/sr
        timeline.append({'index':i+1, 'start':start, 'end':cursor, 'text':scene['text']})
    audio = np.concatenate(chunks)
    sf.write(out/'voice.wav', audio, sr, subtype='PCM_16')
    (out/'timeline.json').write_text(json.dumps(timeline, indent=2))
    def srt_time(t):
        return tts.srt_time(t)
    (out/'captions.srt').write_text('\n'.join(f'{i+1}\n{srt_time(c["start"])} --> {srt_time(c["end"])}\n{c["text"]}\n' for i,c in enumerate(captions)), encoding='utf-8')
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,48,&H00FFFFFF,&H00FFFFFF,&H00101724,&H70101724,-1,0,0,0,100,100,0,0,1,4,1,2,100,145,340,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    (out/'captions.ass').write_text(header+'\n'.join(f'Dialogue: 0,{ass_time(c["start"])},{ass_time(c["end"])},Default,,0,0,0,,{subtitle_text(c["text"])}' for c in captions), encoding='utf-8')
    parts = []
    for i, (scene, segment) in enumerate(zip(project['scenes'], timeline)):
        progress(f'Đang dựng hình cảnh {i+1}/{len(timeline)}…')
        frame, clip = out/f'scene_{i:02d}.png', out/f'scene_{i:02d}.mp4'
        artwork(scene, i, len(timeline), frame)
        frames = max(1, math.ceil((segment['end']-segment['start'])*30))
        # Gentle movement; 30 fps duration is quantised per scene.
        vf = f"zoompan=z='1+0.018*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1080x1920:fps=30,setsar=1"
        command(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-i',str(frame),'-vf',vf,'-frames:v',str(frames),*video_encode_args(QUALITY_FAST),'-threads','2','-filter_threads','2','-pix_fmt','yuv420p',str(clip)])
        parts.append(clip)
    (out/'concat.txt').write_text('\n'.join(f"file '{p.name}'" for p in parts))
    progress('Đang ghép video và cân bằng âm lượng…')
    # Work in output directory, with generated neutral names in filter expressions.
    command(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(out/'concat.txt'),'-c','copy',str(out/'picture.mp4')])
    old = Path.cwd()
    try:
        os.chdir(out)
        command(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-i','picture.mp4','-i','voice.wav','-vf','ass=captions.ass','-af',LOUDNORM_FILTER,*video_encode_args(QUALITY_FAST),'-threads','2','-filter_threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-t',str(len(audio)/sr),'-movflags','+faststart','-metadata','comment=Original illustrations; synthetic narration by Kokoro; locally rendered.','video.mp4'])
    finally:
        os.chdir(old)
    # Cover uses the opening scene; no fake external footage or unlicensed music.
    Image.open(out/'scene_00.png').save(out/'cover.jpg', quality=94)
    (out/'publish.txt').write_text(project['title']+'\n\n'+project.get('description','')+'\n\n'+project.get('hashtags','#shorts #learnsomethingnew')+'\n\nProduction: original illustrated explainer, synthetic English narration (Kokoro).\n'+ '\n'.join(project.get('sources',[])), encoding='utf-8')
    for file in [out/'picture.mp4', *parts]:
        file.unlink(missing_ok=True)
    progress(f'Hoàn tất: {len(audio)/sr:.1f} giây; video.mp4, captions.srt, cover.jpg, publish.txt')
    return {'duration':len(audio)/sr, 'video':str(out/'video.mp4'), 'scenes':len(timeline)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    print(json.dumps(render(json.loads(Path(args.project).read_text()), Path(args.out).resolve())))
