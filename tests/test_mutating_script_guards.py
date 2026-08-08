import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "script",
    [
        "tests/test_repository.py",
        "tests/test_metric_repository.py",
        "tests/test_log_repository.py",
        "tests/test_trace_repository.py",
        "src/database/create_tables.py",
    ],
)
def test_direct_database_scripts_require_explicit_mutation_opt_in(script, monkeypatch):
    monkeypatch.delenv("OPENRCA_RUN_MUTATING_TESTS", raising=False)

    with pytest.raises(SystemExit, match="OPENRCA_RUN_MUTATING_TESTS=1"):
        runpy.run_path(str(ROOT / script), run_name="__main__")
