import json
import tempfile
import threading
import unittest
from pathlib import Path

from pantheon.ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]


class SnapshotConcurrencyTests(unittest.TestCase):
    def test_show_returns_one_snapshot_while_approval_commits(self):
        proposal = json.loads((ROOT / 'examples/handoff.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'ledger.sqlite'
            setup = Ledger(path)
            setup.conn.execute('PRAGMA journal_mode=WAL')
            digest = setup.propose(proposal)['digest']
            setup.close()
            row_read = threading.Event()
            writer_done = threading.Event()
            outcomes = {}

            def read_in_thread():
                ledger = Ledger(path)
                original = ledger._row
                def pause_after_row(identifier):
                    row = original(identifier)
                    row_read.set()
                    if not writer_done.wait(10):
                        raise TimeoutError('writer did not finish')
                    return row
                ledger._row = pause_after_row
                try:
                    outcomes['snapshot'] = ledger.show(proposal['handoff_id'])
                except Exception as exc:
                    outcomes['error'] = repr(exc)
                finally:
                    ledger.close()

            reader = threading.Thread(target=read_in_thread)
            reader.start()
            try:
                self.assertTrue(row_read.wait(10), 'reader did not reach checkpoint')
                writer = Ledger(path)
                try:
                    writer.approve(proposal['handoff_id'], digest, 'operator', 60)
                finally:
                    writer.close()
            finally:
                writer_done.set()
                reader.join(15)
            self.assertFalse(reader.is_alive())
            self.assertNotIn('error', outcomes)
            snapshot = outcomes['snapshot']
            self.assertEqual(snapshot['state'], 'proposed')
            self.assertEqual([event['event'] for event in snapshot['events']], ['proposed'])

    def test_unknown_show_leaves_connection_usable(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = Ledger(Path(temp) / 'ledger.sqlite')
            try:
                with self.assertRaises(ValueError):
                    ledger.show('missing')
                self.assertFalse(ledger.conn.in_transaction)
                proposal = json.loads((ROOT / 'examples/handoff.json').read_text(encoding='utf-8'))
                self.assertEqual(ledger.propose(proposal)['state'], 'proposed')
            finally:
                ledger.close()
