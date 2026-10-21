#!/usr/bin/env python3
"""Read-only verification of the kit's regular files and symbolic links."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST.json').read_text())
errors=[]
for entry in manifest['files']:
    rel=Path(entry['path'])
    if rel.is_absolute() or '..' in rel.parts:
        errors.append(str(rel)+': invalid manifest path');continue
    p=root/rel
    if entry['type']=='symlink':
        if not p.is_symlink() or str(p.readlink())!=entry['target']:
            errors.append(str(rel)+': symbolic link differs')
        elif not p.exists() or not p.resolve().is_relative_to(root):
            errors.append(str(rel)+': broken or external symbolic link')
    elif not p.is_file() or p.is_symlink():
        errors.append(str(rel)+': missing regular file')
    else:
        digest=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
        if digest!=entry['sha256']:errors.append(str(rel)+': SHA-256 differs')
for error in errors:print(error)
print(f"Checked {len(manifest['files'])} entries; {len(errors)} errors.")
sys.exit(bool(errors))
