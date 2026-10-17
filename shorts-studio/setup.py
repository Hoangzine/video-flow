"""Download official model assets over verified HTTPS, verify SHA-256."""
import hashlib
from pathlib import Path
import urllib.request

BASE = Path(__file__).resolve().parent
ASSETS = {
    'kokoro-v1.0.onnx':'beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a',
    'voices-v1.0.bin':'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d'
}


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda:file.read(1048576),b''):
            h.update(block)
    return h.hexdigest()


if __name__=='__main__':
    (BASE/'models').mkdir(exist_ok=True)
    for name,expected in ASSETS.items():
        target=BASE/'models'/name
        if target.exists() and digest(target)==expected:
            print('Verified:',name)
            continue
        print('Downloading:',name)
        temp=target.with_suffix('.download')
        urllib.request.urlretrieve('https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'+name,temp)
        if digest(temp)!=expected:
            temp.unlink(missing_ok=True)
            raise RuntimeError('Checksum mismatch: '+name)
        temp.replace(target)
        print('Verified:',name)
