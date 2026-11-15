"""Refresh bundled constitution and skills from their canonical repository copies."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def main():
    shared=(ROOT/'governance/CHARTER.md').read_text(encoding='utf-8').rstrip()
    for a in json.loads((ROOT/'registry/agents.json').read_text(encoding='utf-8'))['agents']:
        profile=ROOT/'profiles'/a['id']; soul=profile/'SOUL.md'; text=soul.read_text(encoding='utf-8')
        marker='\n# '+a['id'].title()+' — '
        if marker not in text: raise ValueError(f'Missing specialist heading: {soul}')
        suffix=text[text.index(marker):]
        # Match canonical charter separation exactly.
        soul.write_text(shared+'\n\n'+suffix.lstrip('\n'), encoding='utf-8')
        for s in a['skills']:
            source=ROOT/'skills'/s
            for resource in source.rglob('*'):
                if resource.is_symlink(): raise ValueError(f'Skill symlink is not distributable: {resource}')
                if resource.is_file():
                    target=profile/'skills'/s/resource.relative_to(source)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(resource.read_bytes())
if __name__=='__main__': main()
