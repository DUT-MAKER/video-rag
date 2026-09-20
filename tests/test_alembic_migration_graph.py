import subprocess
import sys
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parents[1]
D4_REVISION = "d4e9a2c1f7b0"
SCHEDULE_REVISION = "e2f3a4b5c6d7"
CRAWLER_BASE_REVISION = "7b93f28d9c1a"
MERGE_REVISION = "f1a2b3c4d5e6"


def test_recovered_crawler_revision_is_joined_into_one_head() -> None:
    recovered = ROOT / "alembic" / "versions" / f"{D4_REVISION}_make_crawler_enrichment_optional.py"
    assert recovered.exists(), f"Missing Alembic revision {D4_REVISION}"

    config = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(config)
    revision = script.get_revision(D4_REVISION)

    assert revision is not None
    assert revision.down_revision == CRAWLER_BASE_REVISION

    heads = script.get_heads()
    assert len(heads) == 1
    merge = script.get_revision(MERGE_REVISION)
    assert merge is not None
    assert set(merge.down_revision) == {D4_REVISION, SCHEDULE_REVISION}

    ancestry = {item.revision for item in script.walk_revisions(base="base", head=heads[0])}
    assert {D4_REVISION, SCHEDULE_REVISION, MERGE_REVISION} <= ancestry


def test_migrations_support_offline_sql_generation() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert MERGE_REVISION in result.stdout
