"""OS-owned update lock: released on process exit, never expired by age."""

from contextlib import contextmanager
import os
from pathlib import Path


def update_process_is_active(database_path: Path) -> bool:
    """Probe ownership without changing durable run state."""
    with update_process_lock(database_path) as acquired:
        return not acquired


@contextmanager
def update_process_lock(database_path: Path):
    path = Path(str(database_path) + ".update.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        acquired = False
        try:
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except (BlockingIOError, PermissionError):
                pass
            except OSError as error:
                if error.errno not in {11, 13, 35}:
                    raise
            yield acquired
        finally:
            if acquired:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
