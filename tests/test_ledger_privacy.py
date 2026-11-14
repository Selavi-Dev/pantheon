"""Private reference evidence must not be world-readable on POSIX hosts."""
import os
from pathlib import Path
import stat
import tempfile
import unittest

from pantheon.ledger import Ledger


@unittest.skipUnless(os.name == 'posix', 'POSIX file mode contract')
class LedgerPrivacyTests(unittest.TestCase):
    def test_new_database_is_owner_only_with_permissive_umask(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'ledger.sqlite'
            previous = os.umask(0)
            try:
                ledger = Ledger(path)
                ledger.close()
            finally:
                os.umask(previous)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_existing_database_permissions_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'ledger.sqlite'
            ledger = Ledger(path)
            ledger.close()
            path.chmod(0o640)
            ledger = Ledger(path)
            ledger.close()
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
