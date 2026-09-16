#!/usr/bin/env python3
"""
Robust Git Tree API push via Maton Gateway.
- Creates blobs in parallel-efficient batches
- Creates tree from blobs
- Creates commit and updates branch
"""
import os, sys, json, base64, subprocess, tempfile
from urllib.request import Request, urlopen
from urllib.error import HTTPError

PROJECT = "/home/admin/.openclaw/canvas/games/hot-games"
MATON_KEY = os.environ.get("MATON_API_KEY") or open("/home/admin/.openclaw/workspace/.env").read().split("MATON_API_KEY=")[1].split("\n")[0].strip()
API = "https://gateway.maton.ai/github"
OWNER = "VIP-881"
REPO = "hot-h5-games"
BRANCH = "main"

def gh(method, path, data=None):
    """Call GitHub API via Maton gateway."""
    url = f"{API}/repos/{OWNER}/{REPO}/{path}"
    body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
    req = Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {MATON_KEY}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        resp = urlopen(req)
        return json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f"  ❌ {method} {path}: HTTP {e.code}")
        if e.code == 422:
            print(f"     Detail: {err_body[:300]}")
        return None

def step(msg):
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")

# Collect files
def get_files():
    files = []
    for root, dirs, fnames in os.walk(PROJECT):
        if '.git' in root.split(os.sep):
            continue
        rel = os.path.relpath(root, PROJECT)
        if rel == '.':
            rel = ''
        for f in fnames:
            if f.endswith('.pyc') or f in ('deploy_sync.py', 'deploy_put.py'):
                continue
            path = os.path.join(rel, f) if rel else f
            if path.startswith('.git/') or path.startswith('.github/'):
                continue
            with open(os.path.join(root, f), 'rb') as fh:
                content = fh.read()
            files.append((path, content))
    files.sort(key=lambda x: x[0])
    return files

step("STEP 1: Run build.py")
os.chdir(PROJECT)
result = subprocess.run([sys.executable, "build.py"], capture_output=True, text=True, timeout=60)
for line in result.stdout.strip().split('\n'):
    print(f"  {line}")

step("STEP 2: Collect files")
files = get_files()
print(f"  📦 {len(files)} files to push")

step("STEP 3: Get current HEAD")
ref = gh("GET", f"git/refs/heads/{BRANCH}")
if not ref:
    print("  ❌ Cannot get HEAD ref")
    sys.exit(1)
head_sha = ref["object"]["sha"]
print(f"  📍 HEAD: {head_sha[:12]}")

commit = gh("GET", f"git/commits/{head_sha}")
if not commit:
    print("  ❌ Cannot get commit")
    sys.exit(1)
base_tree_sha = commit["tree"]["sha"]
print(f"  🌳 Base tree: {base_tree_sha[:12]}")

step("STEP 4: Create blobs (batches of 30)")
blob_map = {}  # path -> sha
BATCH = 30
for i in range(0, len(files), BATCH):
    batch = files[i:i+BATCH]
    for path, content in batch:
        ext = os.path.splitext(path)[1].lower()
        text_exts = {'.html', '.js', '.css', '.py', '.json', '.xml', '.yml', '.yaml', '.md', '.txt', '.svg'}
        if ext in text_exts:
            blob_data = {"content": content.decode('utf-8', errors='replace'), "encoding": "utf-8"}
        else:
            blob_data = {"content": base64.b64encode(content).decode('ascii'), "encoding": "base64"}
        
        blob = gh("POST", "git/blobs", blob_data)
        if blob:
            blob_map[path] = blob["sha"]
        else:
            print(f"  ❌ Blob failed for: {path}")
    
    print(f"  📦 Blob batch {i//BATCH+1}/{(len(files)-1)//BATCH+1}: {len(batch)} created")

print(f"  ✅ {len(blob_map)}/{len(files)} blobs created")

step("STEP 5: Create tree from blobs")
tree_items = [{"path": p, "mode": "100644", "type": "blob", "sha": s} for p, s in blob_map.items()]

# Build tree incrementally if needed
BATCH_TREE = 100
current_tree_sha = base_tree_sha
for i in range(0, len(tree_items), BATCH_TREE):
    batch = tree_items[i:i+BATCH_TREE]
    tree_data = {"base_tree": current_tree_sha, "tree": batch}
    tree_result = gh("POST", "git/trees", tree_data)
    if not tree_result:
        # Try without base_tree for first batch
        if i == 0:
            tree_data.pop("base_tree", None)
            tree_result = gh("POST", "git/trees", tree_data)
        if not tree_result:
            print(f"  ❌ Tree batch {i//BATCH_TREE+1} failed")
            sys.exit(1)
    current_tree_sha = tree_result["sha"]
    print(f"  🌳 Tree batch {i//BATCH_TREE+1}/{(len(tree_items)-1)//BATCH_TREE+1}: {current_tree_sha[:12]}")

new_tree_sha = current_tree_sha

step("STEP 6: Create commit")
commit_data = {
    "message": "🎮 Deploy 136 games: lightweight static + Maton developer games, SEO/GEO optimized",
    "tree": new_tree_sha,
    "parents": [head_sha]
}
new_commit = gh("POST", "git/commits", commit_data)
if not new_commit:
    print("  ❌ Commit failed")
    sys.exit(1)
commit_sha = new_commit["sha"]
print(f"  ✅ Commit: {commit_sha[:12]}")

step("STEP 7: Update branch")
update = gh("PATCH", f"git/refs/heads/{BRANCH}", {"sha": commit_sha, "force": False})
if not update:
    print("  ❌ Branch update failed")
    sys.exit(1)
print(f"  ✅ Branch updated to {commit_sha[:12]}")

step("✅ DEPLOYMENT COMPLETE")
print(f"  📍 Commit: {commit_sha}")
print(f"  🎮 Files: {len(files)}")
print(f"  🌐 GitHub Pages: https://vip-881.github.io/hot-h5-games/")
print(f"  🌐 Netlify mirror: https://hot-h5-games.netlify.app/")