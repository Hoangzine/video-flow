"""Local Vietnamese UI for the zero-API-cost companion workflow."""
import json
from pathlib import Path
import subprocess
import sys
import threading
import uuid
import zipfile

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from render import BASE, VOICES, validate

app = FastAPI(title='Shorts Studio — Kokoro local')
(BASE/'exports').mkdir(exist_ok=True)
(BASE/'uploads').mkdir(exist_ok=True)
app.mount('/exports', StaticFiles(directory=BASE/'exports'), name='exports')
app.mount('/uploads', StaticFiles(directory=BASE/'uploads'), name='uploads')
lock = threading.Lock()


@app.get('/', response_class=HTMLResponse)
def home():
    return (BASE/'index.html').read_text()


@app.get('/api/health')
def health():
    return {'ok':True, 'workflow':'local-kokoro-illustrated-shorts', 'voices':VOICES, 'paid_apis':False}


@app.get('/api/sample')
def sample():
    return json.loads((BASE/'projects/voice-science.json').read_text())


@app.post('/api/upload')
async def upload(file: UploadFile):
    data = await file.read(12*1024*1024+1)
    if len(data) > 12*1024*1024:
        raise HTTPException(413, 'Ảnh tối đa 12 MB.')
    name = f'{uuid.uuid4().hex}.jpg'
    path = BASE/'uploads'/name
    try:
        from io import BytesIO
        with Image.open(BytesIO(data)) as image:
            if image.width*image.height > 25000000:
                raise ValueError('Ảnh tối đa 25 megapixel.')
            image.convert('RGB').save(path, quality=94)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as e:
        raise HTTPException(400, 'Ảnh không hợp lệ hoặc quá lớn.') from e
    return {'image':f'uploads/{name}'}


def save_status(out, state, **extra):
    temp = out/'status.tmp'
    temp.write_text(json.dumps({'id':out.name, 'state':state, **extra}, ensure_ascii=False))
    temp.replace(out/'status.json')


def work(out):
    try:
        with (out/'render.log').open('w') as log:
            p = subprocess.run([sys.executable,'-u',str(BASE/'render.py'),str(out/'project.json'),'--out',str(out)],stdout=log,stderr=subprocess.STDOUT,timeout=1800)
        if p.returncode:
            save_status(out,'failed',message='Dựng video lỗi. Xem render.log trong gói dự án.')
            return
        with zipfile.ZipFile(out/'publish-pack.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for name in ['video.mp4','voice.wav','captions.srt','cover.jpg','publish.txt','project.json','timeline.json']:
                archive.write(out/name,name)
        save_status(out,'done',video=f'/exports/{out.name}/video.mp4',pack=f'/exports/{out.name}/publish-pack.zip')
    except Exception as e:
        save_status(out,'failed',message=str(e)[:200])
    finally:
        lock.release()


@app.post('/api/render')
def submit(project: dict):
    try:
        validate(project)
    except (ValueError, TypeError) as e:
        raise HTTPException(400,str(e)) from e
    if not lock.acquire(blocking=False):
        raise HTTPException(409,'Đang dựng một video. Đợi video hiện tại hoàn tất rồi thử lại.')
    out = BASE/'exports'/uuid.uuid4().hex[:12]
    try:
        out.mkdir()
        (out/'project.json').write_text(json.dumps(project, ensure_ascii=False, indent=2))
        save_status(out,'running')
        threading.Thread(target=work,args=(out,),daemon=True).start()
    except Exception:
        lock.release()
        raise
    return {'id':out.name}


@app.get('/api/jobs/{job_id}')
def status(job_id: str):
    if len(job_id)!=12 or any(c not in '0123456789abcdef' for c in job_id):
        raise HTTPException(404)
    out = BASE/'exports'/job_id
    if not (out/'status.json').is_file():
        raise HTTPException(404)
    state = json.loads((out/'status.json').read_text())
    state['progress'] = (out/'render.log').read_text(errors='replace')[-1400:] if (out/'render.log').exists() else ''
    return state


@app.get('/api/outputs')
def outputs():
    return [{'name':p.parent.name,'video':f'/exports/{p.parent.name}/video.mp4'} for p in sorted((BASE/'exports').glob('*/video.mp4'))]
