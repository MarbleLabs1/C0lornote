"""
Tests for src/models/note.py — Note, Category, Tag ORM models.
"""

import datetime
import pytest
from sqlalchemy.exc import IntegrityError

from src.models.note import Note, Category, Tag


# ===========================================================================
# Category
# ===========================================================================

class TestCategory:

    def test_create_returns_object(self, db):
        cat = Category.create(name="Work", color="#FF0000")
        assert isinstance(cat, Category)
        assert cat.name == "Work"
        assert cat.color == "#FF0000"
        assert cat.id is not None
        assert len(cat.id) == 36  # UUID

    def test_create_without_color(self, db):
        cat = Category.create(name="NoColor")
        assert cat.color is None

    def test_create_persists_to_db(self, db):
        Category.create(name="Persist")
        assert Category.get_by_name("Persist") is not None

    def test_get_all_empty(self, db):
        assert Category.get_all() == []

    def test_get_all_returns_sorted_by_name(self, db):
        Category.create(name="Zebra")
        Category.create(name="Alpha")
        Category.create(name="Middle")
        names = [c.name for c in Category.get_all()]
        assert names == ["Alpha", "Middle", "Zebra"]

    def test_get_by_id_found(self, db, sample_category):
        result = Category.get_by_id(sample_category.id)
        assert result is not None
        assert result.name == "Work"

    def test_get_by_id_not_found(self, db):
        assert Category.get_by_id("nonexistent-uuid") is None

    def test_get_by_name_found(self, db, sample_category):
        assert Category.get_by_name("Work") is not None

    def test_get_by_name_not_found(self, db):
        assert Category.get_by_name("Ghost") is None

    def test_duplicate_name_raises_integrity_error(self, db):
        Category.create(name="Unique")
        with pytest.raises(Exception):  # IntegrityError from SQLAlchemy
            Category.create(name="Unique")


# ===========================================================================
# Tag
# ===========================================================================

class TestTag:

    def test_create_returns_object(self, db):
        tag = Tag.create(name="urgent")
        assert isinstance(tag, Tag)
        assert tag.name == "urgent"

    def test_get_all_sorted(self, db):
        Tag.create(name="z_tag")
        Tag.create(name="a_tag")
        Tag.create(name="m_tag")
        names = [t.name for t in Tag.get_all()]
        assert names == ["a_tag", "m_tag", "z_tag"]

    def test_get_by_id_found(self, db, sample_tag):
        result = Tag.get_by_id(sample_tag.id)
        assert result is not None
        assert result.name == "important"

    def test_get_by_id_not_found(self, db):
        assert Tag.get_by_id("fake-id") is None

    def test_get_by_name_found(self, db, sample_tag):
        assert Tag.get_by_name("important") is not None

    def test_get_by_name_not_found(self, db):
        assert Tag.get_by_name("nope") is None

    def test_get_or_create_creates_new(self, db):
        assert Tag.get_by_name("brandnew") is None
        Tag.get_or_create("brandnew")
        assert Tag.get_by_name("brandnew") is not None

    def test_get_or_create_returns_existing(self, db):
        Tag.create(name="existing")
        t1 = Tag.get_or_create("existing")
        t2 = Tag.get_or_create("existing")
        assert t1.id == t2.id
        assert len(Tag.get_all()) == 1


# ===========================================================================
# Note — creation
# ===========================================================================

class TestNoteCreate:

    def test_create_minimal(self, db):
        note = Note.create()
        assert isinstance(note, Note)
        assert note.id is not None
        assert len(note.id) == 36

    def test_create_with_all_fields(self, db, sample_category):
        note = Note.create(
            title="My Note",
            content="<p>Rich</p>",
            plain_content="Rich",
            color="#FFFFFF",
            category_id=sample_category.id,
        )
        assert note.title == "My Note"
        assert note.color == "#FFFFFF"
        assert note.category_id == sample_category.id

    def test_create_with_tags(self, db):
        note = Note.create(title="Tagged", tags=["alpha", "beta"])
        fetched = Note.get_by_id(note.id, include_tags=True)
        assert {t.name for t in fetched.tags} == {"alpha", "beta"}

    def test_create_with_tags_persists_tags(self, db):
        Note.create(title="Persist Tags", tags=["persist_me"])
        assert Tag.get_by_name("persist_me") is not None

    def test_create_with_existing_tag_no_duplicate(self, db, sample_tag):
        Note.create(title="Reuse", tags=["important"])
        assert len(Tag.get_all()) == 1

    def test_create_assigns_unique_uuids(self, db):
        n1 = Note.create()
        n2 = Note.create()
        assert n1.id != n2.id

    def test_create_default_not_pinned(self, db):
        note = Note.create()
        assert note.is_pinned is False


# ===========================================================================
# Note — retrieval
# ===========================================================================

class TestNoteRead:

    def test_get_all_empty(self, db):
        assert Note.get_all() == []

    def test_get_all_returns_all(self, db):
        Note.create(title="A")
        Note.create(title="B")
        Note.create(title="C")
        assert len(Note.get_all()) == 3

    def test_get_all_pinned_first(self, db):
        normal = Note.create(title="Normal")
        pinned = Note.create(title="Pinned")
        Note.get_by_id(pinned.id).toggle_pin()
        results = Note.get_all()
        assert results[0].is_pinned is True

    def test_get_by_id_found(self, db, sample_note):
        result = Note.get_by_id(sample_note.id)
        assert result is not None
        assert result.title == "Hello"

    def test_get_by_id_not_found(self, db):
        assert Note.get_by_id("missing-id") is None

    def test_get_by_category(self, db, sample_category):
        Note.create(title="In Cat", category_id=sample_category.id)
        Note.create(title="In Cat 2", category_id=sample_category.id)
        Note.create(title="No Cat")
        results = Note.get_by_category(sample_category.id)
        assert len(results) == 2

    def test_get_by_tag(self, db, sample_tag):
        tagged = Note.create(title="Tagged")
        Note.get_by_id(tagged.id).add_tag("important")
        Note.create(title="Untagged")
        results = Note.get_by_tag(sample_tag.id)
        assert len(results) == 1
        assert results[0].title == "Tagged"

    def test_get_recent_respects_limit(self, db):
        for i in range(5):
            Note.create(title=f"Note {i}")
        assert len(Note.get_recent(limit=3)) == 3

    def test_get_recent_ordered_newest_first(self, db):
        Note.create(title="First")
        Note.create(title="Second")
        results = Note.get_recent()
        assert results[0].title == "Second"


# ===========================================================================
# Note — update
# ===========================================================================

class TestNoteUpdate:

    def test_update_title(self, db, sample_note):
        sample_note.update(title="Updated Title")
        fetched = Note.get_by_id(sample_note.id)
        assert fetched.title == "Updated Title"

    def test_update_color(self, db, sample_note):
        sample_note.update(color="#123456")
        assert Note.get_by_id(sample_note.id).color == "#123456"

    def test_update_pin_status(self, db, sample_note):
        sample_note.update(is_pinned=True)
        assert Note.get_by_id(sample_note.id).is_pinned is True

    def test_update_tags_replaces_existing(self, db):
        note = Note.create(title="Tags", tags=["old"])
        Note.get_by_id(note.id).update(tag_names=["new1", "new2"])
        fetched = Note.get_by_id(note.id, include_tags=True)
        assert {t.name for t in fetched.tags} == {"new1", "new2"}
        assert "old" not in {t.name for t in fetched.tags}

    def test_update_nonexistent_raises_value_error(self, db):
        ghost = Note()
        ghost.id = "00000000-0000-0000-0000-000000000000"
        with pytest.raises(ValueError):
            ghost.update(title="x")


# ===========================================================================
# Note — deletion
# ===========================================================================

class TestNoteDelete:

    def test_delete_instance_method(self, db, sample_note):
        note_id = sample_note.id
        result = sample_note.delete()
        assert result is True
        assert Note.get_by_id(note_id) is None

    def test_delete_missing_returns_false(self, db):
        ghost = Note()
        ghost.id = "00000000-0000-0000-0000-000000000001"
        assert ghost.delete() is False

    def test_delete_by_id_found(self, db, sample_note):
        note_id = sample_note.id
        assert Note.delete_by_id(note_id) is True
        assert Note.get_by_id(note_id) is None

    def test_delete_by_id_not_found(self, db):
        assert Note.delete_by_id("fake-uuid") is False


# ===========================================================================
# Note — pin toggle
# ===========================================================================

class TestNotePin:

    def test_toggle_pin_false_to_true(self, db, sample_note):
        assert sample_note.is_pinned is False
        new_state = Note.get_by_id(sample_note.id).toggle_pin()
        assert new_state is True
        assert Note.get_by_id(sample_note.id).is_pinned is True

    def test_toggle_pin_twice_restores_original(self, db, sample_note):
        note = Note.get_by_id(sample_note.id)
        note.toggle_pin()
        note2 = Note.get_by_id(sample_note.id)
        note2.toggle_pin()
        assert Note.get_by_id(sample_note.id).is_pinned is False


# ===========================================================================
# Note — tag management
# ===========================================================================

class TestNoteTagManagement:

    def test_add_tag_to_note(self, db, sample_note):
        result = sample_note.add_tag("work")
        assert result is True
        fetched = Note.get_by_id(sample_note.id, include_tags=True)
        assert "work" in {t.name for t in fetched.tags}

    def test_add_tag_idempotent(self, db, sample_note):
        sample_note.add_tag("work")
        sample_note.add_tag("work")
        fetched = Note.get_by_id(sample_note.id, include_tags=True)
        assert len(fetched.tags) == 1

    def test_add_tag_case_insensitive_dedup(self, db, sample_note):
        sample_note.add_tag("Work")
        result = Note.get_by_id(sample_note.id).add_tag("work")
        assert result is True
        fetched = Note.get_by_id(sample_note.id, include_tags=True)
        assert len(fetched.tags) == 1

    def test_remove_tag_from_note(self, db, sample_note):
        sample_note.add_tag("removeme")
        result = Note.get_by_id(sample_note.id).remove_tag("removeme")
        assert result is True
        fetched = Note.get_by_id(sample_note.id, include_tags=True)
        assert "removeme" not in {t.name for t in fetched.tags}

    def test_remove_tag_not_present_returns_false(self, db, sample_note):
        assert sample_note.remove_tag("ghost") is False


# ===========================================================================
# Note — search
# ===========================================================================

class TestNoteSearch:

    def test_search_by_title(self, db):
        Note.create(title="Python Notes", plain_content="python")
        Note.create(title="Java Notes", plain_content="java")
        Note.create(title="Recipes", plain_content="food")
        results = Note.search("Python")
        assert len(results) == 1
        assert results[0].title == "Python Notes"

    def test_search_by_plain_content(self, db):
        Note.create(title="Shopping", plain_content="buy milk and eggs")
        results = Note.search("milk")
        assert len(results) == 1

    def test_search_multi_word_and_logic(self, db):
        Note.create(title="Python async notes", plain_content="async")
        results = Note.search("Python async")
        assert len(results) == 1
        assert len(Note.search("Python Java")) == 0

    def test_search_empty_query_returns_all(self, db):
        Note.create(title="A")
        Note.create(title="B")
        Note.create(title="C")
        assert len(Note.search("")) == 3

    def test_search_filter_by_category(self, db, sample_category):
        Note.create(title="In Cat", plain_content="x", category_id=sample_category.id)
        Note.create(title="In Cat 2", plain_content="x", category_id=sample_category.id)
        Note.create(title="No Cat", plain_content="x")
        results = Note.search("", category_id=sample_category.id)
        assert len(results) == 2

    def test_search_filter_by_tag(self, db, sample_tag):
        tagged = Note.create(title="Tagged", plain_content="x")
        Note.get_by_id(tagged.id).add_tag("important")
        Note.create(title="Untagged", plain_content="x")
        results = Note.search("", tag_ids=[sample_tag.id])
        assert len(results) == 1

    def test_search_pinned_only(self, db):
        Note.create(title="Normal")
        Note.create(title="Normal 2")
        pinned = Note.create(title="Pinned")
        Note.get_by_id(pinned.id).toggle_pin()
        results = Note.search("", pinned_only=True)
        assert len(results) == 1
        assert results[0].title == "Pinned"

    def test_search_no_results(self, db):
        Note.create(title="Hello", plain_content="world")
        assert Note.search("xyzzy123") == []


# ===========================================================================
# Note — aggregates
# ===========================================================================

class TestNoteAggregates:

    def test_count_by_category_empty(self, db):
        assert Note.count_by_category() == {}

    def test_count_by_category_with_notes(self, db, sample_category):
        Note.create(category_id=sample_category.id)
        Note.create(category_id=sample_category.id)
        Note.create(category_id=sample_category.id)
        Note.create()  # uncategorized

        counts = Note.count_by_category()
        assert counts[sample_category.id] == 3
        assert counts["uncategorized"] == 1

    def test_count_by_tag_empty(self, db):
        assert Note.count_by_tag() == {}

    def test_count_by_tag_with_notes(self, db, sample_tag):
        n1 = Note.create(title="N1")
        n2 = Note.create(title="N2")
        Note.get_by_id(n1.id).add_tag("important")
        Note.get_by_id(n2.id).add_tag("important")

        counts = Note.count_by_tag()
        assert counts[sample_tag.id] == 2


# ===========================================================================
# Note — serialization
# ===========================================================================

class TestNoteToDict:

    def test_to_dict_has_expected_keys(self, db, sample_note):
        fetched = Note.get_by_id(sample_note.id)
        d = fetched.to_dict()
        expected_keys = {
            "id", "title", "content", "created_date", "modified_date",
            "color", "is_pinned", "category_id",
        }
        assert expected_keys.issubset(d.keys())

    def test_to_dict_dates_are_iso_strings(self, db, sample_note):
        fetched = Note.get_by_id(sample_note.id)
        d = fetched.to_dict()
        assert "T" in d["created_date"]
        datetime.datetime.fromisoformat(d["created_date"])  # must not raise

    def test_to_dict_includes_tags_when_loaded(self, db):
        note = Note.create(title="WithTags", tags=["mytag"])
        fetched = Note.get_by_id(note.id, include_tags=True)
        d = fetched.to_dict()
        assert "tags" in d
        assert d["tags"][0]["name"] == "mytag"

    def test_to_dict_includes_category_when_loaded(self, db, sample_category):
        note = Note.create(title="WithCat", category_id=sample_category.id)
        fetched = Note.get_by_id(note.id, include_category=True)
        d = fetched.to_dict()
        assert "category" in d
        assert d["category"]["name"] == "Work"

    def test_to_dict_none_dates_handled(self, db):
        note = Note()
        note.id = "test-id"
        note.title = "Manual"
        note.created_date = None
        note.modified_date = None
        note.color = None
        note.is_pinned = False
        note.category_id = None
        note.content = None
        d = note.to_dict()
        assert d["created_date"] is None
        assert d["modified_date"] is None
