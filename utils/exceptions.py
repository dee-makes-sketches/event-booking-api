class VenueOwnershipError(Exception):
    pass

class EventTimeConflictError(Exception):
    pass

class EventOwnershipError(Exception):
    pass

class SeatCapacityExceededError(Exception):
    pass

class SeatNotAvailableError(Exception):
    pass

class SeatNotFoundError(Exception):
    pass

class EventHasActiveBookingsError(Exception):
    pass

class EventNotPublishedError(Exception):
    pass


class InvalidEventStatusTransition(Exception):
    pass

class BookingAlreadyCancelledError(Exception):
    pass







class ForcedBookingFailure(Exception):
    pass