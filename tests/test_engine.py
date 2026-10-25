from herchoice.content import Library
from herchoice.config import get_settings


def test_library_loads_and_every_entry_cites_a_source():
    lib = Library.load(get_settings().content_path)
    assert len(lib.entries) >= 10
    for e in lib.entries:
        assert e.sources, e.id
        assert e.answers.get("en"), e.id


def test_first_contact_welcomes_then_answers_the_saved_question(engine_factory):
    eng = engine_factory()
    first = eng.handle("new", "Is my period normal?")
    assert "Welcome" in first.text and "how old" in first.text.lower()
    second = eng.handle("new", "1")
    assert second.entry_id == "periods-normal"


def test_greeting_first_is_not_treated_as_a_question(engine_factory):
    eng = engine_factory(lang="ha")
    eng.handle("g", "sannu")
    r = eng.handle("g", "2")
    assert r.text.startswith("Na gode")


def test_answers_from_library_with_disclaimer_and_draft_label(ready):
    r = ready.handle("u1", "What family planning methods are there?")
    assert r.entry_id == "contraception-methods"
    assert "not a diagnosis" in r.text
    assert "draft content" in r.text.lower()


def test_approved_only_mode_never_shows_draft_content(engine_factory):
    eng = engine_factory(allow_draft=False)
    eng.handle("u2", "hi")
    eng.handle("u2", "2")
    r = eng.handle("u2", "What family planning methods are there?")
    assert r.entry_id is None  # nothing approved yet, so the user is offered a referral instead


def test_age_appropriate_content_for_youngest_band(engine_factory):
    eng = engine_factory()
    eng.handle("kid", "hi")
    eng.handle("kid", "1")  # 10–14
    r = eng.handle("kid", "When am I most likely to get pregnant? trying to conceive")
    assert r.entry_id != "fertility-window"


def test_urgent_danger_sign_overrides_retrieval(ready):
    r = ready.handle("u1", "I have heavy bleeding and I fainted")
    assert r.flag == "urgent_care"
    assert r.entry_id is None


def test_abuse_disclosure_triggers_protection_and_referral(ready):
    r = ready.handle("u1", "my uncle forced me")
    assert r.flag == "protection"
    assert "not your fault" in r.text
    assert "YES" in r.text
    follow = ready.handle("u1", "yes")
    assert "local government" in follow.text.lower()
    places = ready.handle("u1", "Nassarawa")
    assert "Support Centre" in places.text  # protection service listed for a protection case


def test_hausa_falls_back_to_english_with_notice_when_translation_missing(engine_factory):
    eng = engine_factory(lang="ha")
    eng.handle("h", "sannu")
    eng.handle("h", "2")
    r = eng.handle("h", "Ina son sanin hanyoyin tsarin iyali")
    assert r.entry_id == "contraception-methods"
    assert "Turanci" in r.text


def test_delete_erases_session_immediately(ready):
    ready.handle("u1", "SAVE")
    assert ready.sessions.count() == 1
    r = ready.handle("u1", "DELETE")
    assert "deleted" in r.text.lower()
    assert ready.sessions.count() == 0


def test_hausa_delete_command(engine_factory):
    eng = engine_factory(lang="ha")
    eng.handle("h2", "sannu")
    r = eng.handle("h2", "GOGE")
    assert eng.sessions.count() == 0
    assert "share" in r.text.lower()


def test_unknown_question_offers_referral_not_a_guess(ready):
    r = ready.handle("u1", "zxqv blorp")
    assert r.entry_id is None
    assert "YES" in r.text


def test_language_switch(ready):
    assert ready.handle("u1", "HAUSA").language == "ha"
    assert ready.handle("u1", "ENGLISH").language == "en"
