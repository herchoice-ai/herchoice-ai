import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture
def engine_factory(monkeypatch):
    def make(lang="en", allow_draft=True):
        monkeypatch.setenv("HERCHOICE_DEFAULT_LANG", lang)
        monkeypatch.setenv("HERCHOICE_ALLOW_DRAFT", "true" if allow_draft else "false")
        monkeypatch.setenv("HERCHOICE_ID_SECRET", "test-secret")
        from herchoice.config import get_settings
        from herchoice.engine import Engine

        return Engine(get_settings())

    return make


@pytest.fixture
def ready(engine_factory):
    """An engine where user 'u1' has already said she is 15–19."""
    eng = engine_factory()
    eng.handle("u1", "hello")
    eng.handle("u1", "2")
    return eng
