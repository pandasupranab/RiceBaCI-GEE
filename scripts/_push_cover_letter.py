"""Push the updated cover letter (md + docx + pdf) to GitHub main."""
import base64, json, subprocess
from pathlib import Path

REPO = 'pandasupranab/RiceBaCI-GEE'
ROOT = Path('/home/user/workspace/RiceBaCI-GEE')
FILES = [
    'manuscript/00_cover_letter.md',
    'manuscript/Cover_Letter.docx',
    'manuscript/Cover_Letter.pdf',
    'scripts/_push_cover_letter.py',
]
# We also added a host-side build script:
HOST_FILES = [
    ('/home/user/workspace/build_cover_letter.py', 'scripts/build_cover_letter.py'),
]

MSG = 'docs(cover-letter): update with v1.0.0-submission empirical findings + reproducibility statement'

def put(path, content_bytes):
    b64 = base64.b64encode(content_bytes).decode('ascii')
    r = subprocess.run(['gh', 'api', f'/repos/{REPO}/contents/{path}?ref=main'],
                       capture_output=True, text=True)
    sha = json.loads(r.stdout).get('sha') if r.returncode == 0 else None
    payload = {'message': MSG, 'content': b64, 'branch': 'main'}
    if sha:
        payload['sha'] = sha
    tmp = Path(f'/tmp/_payload.json')
    tmp.write_text(json.dumps(payload))
    r2 = subprocess.run(
        ['gh', 'api', '--method', 'PUT', f'/repos/{REPO}/contents/{path}', '--input', str(tmp)],
        capture_output=True, text=True
    )
    ok = r2.returncode == 0
    print(f"{'OK ' if ok else 'ERR'} {path}")
    if not ok:
        print(r2.stderr[:500])
    return ok

ok_all = True
for rel in FILES:
    p = ROOT / rel
    if not p.exists():
        print(f"SKIP (missing) {rel}")
        continue
    ok_all &= put(rel, p.read_bytes())

for host_path, repo_path in HOST_FILES:
    p = Path(host_path)
    if not p.exists():
        print(f"SKIP host {host_path}")
        continue
    ok_all &= put(repo_path, p.read_bytes())

print("\nALL OK" if ok_all else "\nSOME FAILED")
