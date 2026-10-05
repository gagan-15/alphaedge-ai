import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.market_data.update_process_lock import update_process_lock


def test_live_owner_cannot_be_displaced_by_run_age(tmp_path):
    from backend.services.market_data.dhan_incremental_update_service import DhanIncrementalUpdateService

    service = DhanIncrementalUpdateService.__new__(DhanIncrementalUpdateService)
    service.store = SimpleNamespace(path=tmp_path / "test.sqlite3")
    service._run_owned = Mock()
    with update_process_lock(service.store.path) as acquired:
        assert acquired
        assert service.run().status == "ALREADY_RUNNING"
        service._run_owned.assert_not_called()


def test_orphaned_recent_run_can_be_recovered_under_exclusive_lock(tmp_path):
    from backend.services.market_data.dhan_shadow_store import DhanShadowStore

    store = DhanShadowStore(tmp_path / "test.sqlite3")
    old_run = store.begin_incremental_update_run()
    with update_process_lock(store.path) as acquired:
        assert acquired
        new_run = store.begin_incremental_update_run(stale_after_seconds=0)
        assert new_run is not None and new_run != old_run
        assert store.incremental_update_status()["run_id"] == new_run


def test_lock_rejects_second_owner_and_releases(tmp_path):
    path = tmp_path / "test.sqlite3"
    with update_process_lock(path) as first:
        assert first
        with update_process_lock(path) as second:
            assert not second
    with update_process_lock(path) as recovered:
        assert recovered


def test_process_exit_releases_lock(tmp_path):
    path = tmp_path / "test.sqlite3"
    script = (
        "import os,sys; from pathlib import Path; "
        "from backend.services.market_data.update_process_lock import update_process_lock; "
        "guard=update_process_lock(Path(sys.argv[1])); "
        "assert guard.__enter__(); print('locked',flush=True); "
        "sys.stdin.readline(); os._exit(0)"
    )
    child = subprocess.Popen(
        [sys.executable, "-c", script, str(path)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    )
    try:
        assert child.stdout.readline().strip() == "locked"
        with update_process_lock(path) as acquired:
            assert not acquired
        child.communicate("exit\n", timeout=10)
        with update_process_lock(path) as acquired:
            assert acquired
    finally:
        if child.poll() is None:
            child.communicate("exit\n", timeout=10)
