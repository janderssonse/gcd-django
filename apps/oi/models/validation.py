"""
Structural validators for the revision reflection layer (roadmap B0).

Field identity in the revision system is expressed as name strings resolved
against model attributes at runtime, so a rename can silently become a no-op.
These helpers walk every concrete Revision subclass and check the
hand-maintained name lists still resolve; they are exercised by
apps/oi/tests/test_revision_validation.py.

Extracted from the models package as the first step of the C1 split. Kept
free of import-time dependencies on the models module (Revision is imported
lazily) so it can never introduce a circular import.
"""

from django.core.exceptions import FieldDoesNotExist


def _walk_field_path(model_class, names):
    """
    Resolve a sequence of related field names, raising FieldDoesNotExist for
    any name that is not a field on the model reached so far.

    Unlike RelPath this tolerates a multi-valued intermediate step (the
    brand_emblem -> group special case), since we only care that the names
    exist, not that the path is traversable in a single query.
    """
    cls = model_class
    for name in names:
        field = cls._meta.get_field(name)
        if field.is_relation and field.related_model is not None:
            cls = field.related_model


def _concrete_revision_classes():
    """Every concrete production Revision subclass.

    Test doubles (the dummy revisions under apps/oi/tests/) register as
    Revision subclasses once another test imports them, so exclude anything
    defined in a test module -- the validators are about the real schema.
    """
    from apps.oi.models import Revision

    found = []

    def walk(cls):
        for sub in cls.__subclasses__():
            walk(sub)
            if not sub._meta.abstract and \
                    'tests' not in sub.__module__.split('.'):
                found.append(sub)

    walk(Revision)
    return found


def validate_revision_definitions():
    """
    Check that the count/stats field-name paths on every revision class still
    refer to real fields.

    These tuples (parent, major-flag and stats-category paths) are turned into
    RelPath lookups at commit time, so a stale name breaks count/stat
    propagation silently. Returns a list of human-readable error strings; an
    empty list means everything resolves.
    """
    errors = []
    for cls in _concrete_revision_classes():
        paths = set()
        paths |= set(cls._get_parent_field_tuples())
        paths |= set(cls._get_major_flag_field_tuples())
        paths |= set(cls._get_stats_category_field_tuples())
        for names in paths:
            try:
                _walk_field_path(cls, names)
            except FieldDoesNotExist as error:
                errors.append('%s: %s -> %s'
                              % (cls.__name__, tuple(names), error))
    return errors


def _revision_attr_exists(cls, name):
    """True if `name` is a model field on `cls` or a class attribute
    (property/descriptor) -- i.e. getattr(revision, name) can resolve it."""
    try:
        cls._meta.get_field(name)
        return True
    except FieldDoesNotExist:
        return hasattr(cls, name)


def validate_revision_field_lists():
    """
    Check that every name a revision lists in field_list() is a real field or
    attribute and has a _get_blank_values() entry.

    The compare/diff path does getattr(self, name) for each field_list name and
    looks it up in _get_blank_values() for added objects (see _changed_fields),
    so a stale name there crashes at compare time instead of degrading
    silently -- but only when that revision type is next edited. This turns it
    into a test failure.

    Returns (errors, skipped). A few revisions (IssueRevision) build their
    field_list from live changeset state and cannot be introspected from a
    bare instance; they are returned in `skipped` -- and covered by the
    add/compare flow tests -- rather than being silently ignored.
    """
    errors = []
    skipped = []
    for cls in _concrete_revision_classes():
        try:
            instance = cls()
            names = list(instance.field_list())
            blank_values = set(instance._get_blank_values())
        except Exception:
            skipped.append(cls.__name__)
            continue
        for name in names:
            if not _revision_attr_exists(cls, name):
                errors.append('%s.field_list: %r is not a field or attribute'
                              % (cls.__name__, name))
            elif name not in blank_values:
                errors.append('%s: field_list entry %r has no '
                              '_get_blank_values() entry' % (cls.__name__, name))
    return errors, skipped
