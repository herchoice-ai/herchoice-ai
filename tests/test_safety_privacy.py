from herchoice import llm, safety
from herchoice.privacy import SessionStore, anonymous_id


def test_phone_numbers_become_irreversible_codes():
    code = anonymous_id("+2348012345678", "secret")
    assert "234" not in code and len(code) == 32
    assert code == anonymous_id("+2348012345678", "secret")
    assert code != anonymous_id("+2348012345678", "other-secret")


def test_sessions_expire_unless_saved():
    store = SessionStore(ttl_seconds=0, default_language="ha")
    store.get("a")
    assert store.count() == 0
    s = store.get("b")
    s.save_history = True
    assert store.count() == 1


def test_history_kept_only_with_opt_in():
    store = SessionStore(ttl_seconds=60, default_language="en")
    store.get("a")
    store.remember("a", "private question")
    assert store.get("a").history == []


def test_safety_matches_whole_words_and_ignores_punctuation():
    assert safety.check("He raped me.").flag is safety.Flag.PROTECTION
    assert safety.check("I have HEAVY bleeding!").flag is safety.Flag.URGENT_CARE
    assert safety.check("What is a grape?").flag is safety.Flag.NONE


def test_hausa_safety_terms():
    assert safety.check("an yi min fyade").flag is safety.Flag.PROTECTION


def test_llm_rewrite_rejected_if_it_adds_numbers():
    approved = "Emergency pills work best within 3 days."
    assert llm.is_grounded("Take them within 3 days.", approved)
    assert not llm.is_grounded("Take 2 tablets within 3 days.", approved)
    assert not llm.is_grounded("", approved)
