"""Refresh bundled constitution and skills from their canonical repository copies."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def main():
    shared=(ROOT/'governance/CHARTER.md').read_text().rstrip()
    for a in json.loads((ROOT/'registry/agents.json').read_text())['agents']:
        profile=ROOT/'profiles'/a['id']; soul=profile/'SOUL.md'; text=soul.read_text()
        marker='\n# '+a['id'].title()+' — '
        if marker not in text: raise ValueError(f'Missing specialist heading: {soul}')
        suffix=text[text.index(marker):]
        # Match canonical charter separation exactly.
        soul.write_text(shared+'\n\n'+suffix.lstrip('\n'))
        for s in a['skills']:
            target=profile/'skills'/s/'SKILL.md'; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes((ROOT/'skills'/s/'SKILL.md').read_bytes())
if __name__=='__main__': main()
