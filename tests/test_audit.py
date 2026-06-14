from __future__ import annotations

import sqlite3
import tempfile
from contextlib import closing
import unittest
from pathlib import Path

from ai_real_estate_fund.production.audit import AuditEvent, SQLiteAuditLog


class AuditLogTest(unittest.TestCase):
    def test_append_and_verify_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "audit.db"
            log = SQLiteAuditLog(db)
            first = log.append(AuditEvent(actor="tester", action="create", resource_type="property", resource_id="one", payload={"score": 1}))
            second = log.append(AuditEvent(actor="tester", action="update", resource_type="property", resource_id="one", payload={"score": 2}))
            self.assertNotEqual(first.event_hash, second.event_hash)
            ok, errors = log.verify_chain()
            self.assertTrue(ok, errors)

    def test_tampering_breaks_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "audit.db"
            log = SQLiteAuditLog(db)
            log.append(AuditEvent(actor="tester", action="create", resource_type="property", resource_id="one", payload={"score": 1}))
            with closing(sqlite3.connect(db)) as conn:
                conn.execute("UPDATE audit_events SET payload_json = ? WHERE id = 1", ('{"score":99}',))
                conn.commit()
            ok, errors = log.verify_chain()
            self.assertFalse(ok)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
