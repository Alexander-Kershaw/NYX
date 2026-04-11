from cloud.kinesis_producer import build_event_factory_cycle


def test_build_factory_cycle_expected_factories_number() -> None:
    factories = build_event_factory_cycle()

    assert len(factories) == 5


def test_build_factory_cycle_factories_return_events() -> None:
    factories = build_event_factory_cycle()
    events = [factory() for factory in factories]

    assert all(event.event_id for event in events)
    assert all(event.satellite_id.startswith("NYX-SAT-") for event in events)