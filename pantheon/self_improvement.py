"""Local, single-writer improvement review aid. Never deploys changes."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

AGENTS = frozenset({'hermes', 'athena', 'argus', 'themis', 'hephaestus', 'apollo', 'mnemosyne', 'socrates'})


def require(condition, message):
    if not condition:
        raise ValueError(message)


def string(d, key):
    value = d.get(key)
    require(isinstance(value, str) and bool(value.strip()), f'{key}: nonempty string required')
    return value


def number(d, key):
    value = d.get(key)
    require(type(value) in (int, float) and math.isfinite(value), f'{key}: finite number required')
    return value


def integer(d, key):
    value = d.get(key)
    require(type(value) is int and value > 0, f'{key}: positive integer required')
    return value


def boolean(d, key):
    value = d.get(key)
    require(type(value) is bool, f'{key}: boolean required')
    return value


def digest(d):
    value = string(d, 'candidate_sha256')
    require(re.fullmatch(r'[0-9a-f]{64}', value) is not None, 'candidate_sha256: 64 lowercase hexadecimal characters required')
    return value


def evidence(value):
    require(isinstance(value, str) and bool(value.strip()), 'evidence reference required')
    return value


def has_synthetic(record):
    return 'synthetic:' in json.dumps(record).lower()


def record_id(value):
    require(isinstance(value, str) and re.fullmatch(r'SI-[A-Z0-9-]{1,48}', value) is not None, 'invalid proposal ID')
    return value


def add(state, proposal):
    p = copy.deepcopy(proposal)
    pid = record_id(p.get('id'))
    require(pid not in state, 'proposal already exists')
    for field in ('title', 'workflow', 'finding_key', 'scope', 'hypothesis', 'metric', 'rollback'):
        string(p, field)
    require(p.get('author') == 'hephaestus', 'candidate author must be hephaestus')
    require(p.get('direction') in ('lower', 'higher'), 'direction must be lower or higher')
    require(number(p, 'minimum_improvement') > 0, 'minimum_improvement must be positive')
    integer(p, 'minimum_samples')
    digest(p)
    refs = p.get('evidence_refs')
    require(isinstance(refs, list) and len(refs) > 0, 'evidence_refs must be nonempty')
    for ref in refs:
        evidence(ref)
    for existing in state.values():
        prior = existing['proposal']
        require(existing['status'] in ('rejected', 'closed') or (prior['workflow'], prior['finding_key']) != (p['workflow'], p['finding_key']), 'duplicate active finding')
    state[pid] = {'proposal': p, 'status': 'proposed'}
    return state[pid]


def evaluate(state, pid, evaluation):
    row = state[record_id(pid)]
    require(row['status'] in ('proposed', 'evaluation_failed'), 'proposal not open for evaluation')
    p, e = row['proposal'], copy.deepcopy(evaluation)
    require(e.get('evaluator') == 'argus' and e['evaluator'] != p['author'], 'independent Argus evaluation required')
    require(digest(e) == digest(p), 'candidate digest mismatch')
    base, candidate = number(e, 'baseline'), number(e, 'candidate')
    samples = integer(e, 'sample_count')
    evidence(e.get('comparison_ref'))
    string(e, 'limitations')
    regression = boolean(e, 'regressions_pass')
    guardrail = boolean(e, 'guardrails_pass')
    improvement = (base - candidate) if p['direction'] == 'lower' else (candidate - base)
    require(math.isfinite(improvement), 'improvement overflow')
    passed = improvement >= p['minimum_improvement'] and samples >= p['minimum_samples'] and regression and guardrail
    row['evaluation'] = {**e, 'observed_improvement': improvement, 'threshold_pass': passed}
    row['status'] = 'evaluated' if passed else 'evaluation_failed'
    return row


def review(state, pid, review_data):
    row = state[record_id(pid)]
    require(row['status'] == 'evaluated', 'passing evaluation required')
    r = copy.deepcopy(review_data)
    require(r.get('reviewer') == 'themis', 'Themis review required')
    require(digest(r) == digest(row['proposal']), 'candidate digest mismatch')
    evidence(r.get('evidence_ref'))
    string(r, 'notes')
    governance = boolean(r, 'governance_pass')
    overlap = boolean(r, 'grokbot_overlap')
    row['review'] = r
    row['status'] = 'reviewed' if governance and not overlap else 'rejected'
    return row


def approve(state, pid, decision):
    """Record a human decision. Does not authenticate anyone or authorize deployment."""
    row = state[record_id(pid)]
    require(row['status'] == 'reviewed', 'passing independent evaluation and governance review required')
    a = copy.deepcopy(decision)
    admin = string(a, 'administrator')
    identity = admin.strip().casefold()
    require(identity not in AGENTS and identity not in {f'pantheon-{agent}' for agent in AGENTS}, 'agent cannot be administrator')
    require(digest(a) == digest(row['proposal']), 'candidate digest mismatch')
    require(string(a, 'scope') == row['proposal']['scope'], 'approval scope mismatch')
    evidence(a.get('evidence_ref'))
    require(a.get('decision') in ('approve', 'reject'), 'invalid decision')
    require(not has_synthetic(row) and not has_synthetic(a), 'synthetic records cannot receive an administrator decision')
    row['administrator_decision'] = a
    row['status'] = 'approval_recorded' if a['decision'] == 'approve' else 'rejected'
    return row


def lesson(state, pid):
    row = state[record_id(pid)]
    p = row['proposal']
    # A code fence with a unique, sufficiently long delimiter keeps untrusted
    # free text from becoming live Obsidian directives or Markdown embeds.
    payload = json.dumps(row, indent=2, ensure_ascii=False, allow_nan=False)
    fence = '`' * max(3, max((len(x) + 1 for x in re.findall(r'`+', payload)), default=3))
    return (f'# {pid} — Improvement record\n\n'
            f'Status: {row["status"]}\n\n'
            'Review classification: candidate evidence, not a validated production outcome. '
            'Review for sensitive content before exporting.\n\n'
            f'{fence}json\n{payload}\n{fence}\n')


def export_lesson(state, pid, directory):
    require(directory.is_dir(), 'explicit existing vault inbox directory required')
    path = directory / f'{record_id(pid)}.md'
    rendered = lesson(state, pid)
    with path.open('x', encoding='utf-8') as handle:
        handle.write(rendered)
    return path


def load_json(path):
    with path.open(encoding='utf-8') as handle:
        data = json.load(handle)
    require(isinstance(data, dict), 'JSON object required')
    return data


def validate_state(state):
    """Replay stored evidence to reject incomplete or inconsistent local records.

    This detects malformed state; it cannot authenticate or protect a writable
    file against a party capable of replacing the complete evidence chain.
    """
    require(isinstance(state, dict), 'state must be a JSON object')
    active_findings = set()
    for pid, row in state.items():
        record_id(pid)
        require(isinstance(row, dict) and isinstance(row.get('proposal'), dict), 'invalid state record')
        require(row['proposal'].get('id') == pid, 'state proposal ID mismatch')
        replayed = {}
        add(replayed, row['proposal'])
        for key, operation in (('evaluation', evaluate), ('review', review), ('administrator_decision', approve)):
            if key in row:
                require(isinstance(row[key], dict), f'invalid state {key}')
                operation(replayed, pid, row[key])
        require(replayed[pid] == row, 'state evidence or status mismatch')
        if row['status'] != 'rejected':
            finding = (row['proposal']['workflow'], row['proposal']['finding_key'])
            require(finding not in active_findings, 'duplicate active finding')
            active_findings.add(finding)
    return state


def save(path, state):
    # Atomic replacement protects against partial writes; concurrent writers
    # are intentionally unsupported. Parent must already exist.
    require(path.parent.is_dir(), 'state parent directory must already exist')
    validate_state(state)
    fd, tmp = tempfile.mkstemp(prefix='.improvement-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(state, handle, indent=2, allow_nan=False)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True, help='private single-writer JSON state path')
    sub = parser.add_subparsers(dest='command', required=True)
    add_cmd = sub.add_parser('add')
    add_cmd.add_argument('file', type=Path)
    for command in ('evaluate', 'review', 'approve'):
        cmd = sub.add_parser(command)
        cmd.add_argument('id')
        cmd.add_argument('file', type=Path)
    sub.add_parser('report')
    note = sub.add_parser('lesson')
    note.add_argument('id')
    exp = sub.add_parser('export-lesson')
    exp.add_argument('id')
    exp.add_argument('directory', type=Path)
    args = parser.parse_args(argv)
    try:
        state = validate_state(load_json(args.state)) if args.state.exists() else {}
        cmd = args.command
        if cmd == 'report':
            print(json.dumps([{'id': key, 'status': row['status'], 'title': row['proposal']['title']} for key, row in state.items()], indent=2))
            return 0
        if cmd == 'lesson':
            print(lesson(state, args.id), end='')
            return 0
        if cmd == 'export-lesson':
            print(export_lesson(state, args.id, args.directory))
            return 0
        data = load_json(args.file)
        row = add(state, data) if cmd == 'add' else {'evaluate': evaluate, 'review': review, 'approve': approve}[cmd](state, args.id, data)
        save(args.state, state)
        print(json.dumps({'id': row['proposal']['id'], 'status': row['status']}))
        return 0
    except (ValueError, KeyError, OSError, TypeError, OverflowError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
