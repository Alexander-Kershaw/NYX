from simulator.contracts import EventType
from simulator.run_simulator import create_event_factories

def test_factories_generate_events_with_expected_types() -> None:
    event_factories = create_event_factories()
    events = [factory() for factory in event_factories]

    event_types = [event.event_type for event in events]

    assert event_types == [
        EventType.COMMS,
        EventType.HEARTBEAT,
        EventType.NAVIGATION,
        EventType.POWER,
        EventType.THERMAL
    ]

