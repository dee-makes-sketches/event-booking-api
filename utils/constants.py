from models.event import EventStatus
from utils.exceptions import InvalidEventStatusTransition

ALLOWED_TRANSITIONS = {
    EventStatus.DRAFT: {
        EventStatus.PUBLISHED,
        EventStatus.CANCELLED,
    },

    EventStatus.PUBLISHED: {
        EventStatus.COMPLETED,
        EventStatus.CANCELLED,
    },

    EventStatus.CANCELLED: set(),

    EventStatus.COMPLETED: set(),
}

def validate_status_transition(current_status:EventStatus, new_status:EventStatus):
    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise InvalidEventStatusTransition()