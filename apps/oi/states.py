"""
Constants for the state of a Changeset in the indexing workflow.

The canonical definition is the ``ChangesetState`` enum; the module-level
names (``OPEN``, ``APPROVED`` ...), ``DISPLAY_NAME`` and the ``ACTIVE`` /
``CLOSED`` groupings are kept as thin aliases so existing call sites
(``states.OPEN``, ``states.DISPLAY_NAME`` ...) keep working unchanged.
"""
from django.db import models


class ChangesetState(models.IntegerChoices):
    # In the old_state field when a reservation is created.
    UNRESERVED = 99, 'Available'
    # Artificial reservation, replaced when the Log* tables are migrated.
    BASELINE = 0, 'Baseline'
    # Open and being worked on by the indexer.
    OPEN = 1, 'Editing'
    # Submitted for approval, but not being examined.
    PENDING = 2, 'Pending Review'
    # Being discussed between indexer, approver and others.
    DISCUSSED = 3, 'In Discussion'
    # Being examined for approval.
    REVIEWING = 4, 'Under Review'
    # Approval has been granted.
    APPROVED = 5, 'Approved'
    # Approval was refused, no further work will be done.
    DISCARDED = 6, 'Discarded'


UNRESERVED = ChangesetState.UNRESERVED
BASELINE = ChangesetState.BASELINE
OPEN = ChangesetState.OPEN
PENDING = ChangesetState.PENDING
DISCUSSED = ChangesetState.DISCUSSED
REVIEWING = ChangesetState.REVIEWING
APPROVED = ChangesetState.APPROVED
DISCARDED = ChangesetState.DISCARDED

DISPLAY_NAME = {state.value: state.label for state in ChangesetState}

ACTIVE = (OPEN, PENDING, DISCUSSED, REVIEWING)

CLOSED = (APPROVED, DISCARDED)
