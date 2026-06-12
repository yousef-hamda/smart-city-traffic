from simulator.network import load_network


def test_network_derivation_matches_spec_scale() -> None:
    network = load_network()
    assert 40 <= len(network.segments) <= 60
    assert len(network.sensors) == 3 * len(network.segments)
    assert 25 <= len(network.cameras) <= 35


def test_derivation_is_deterministic() -> None:
    first = load_network()
    second = load_network()
    assert [s.id for s in first.sensors] == [s.id for s in second.sensors]
    assert [c.id for c in first.cameras] == [c.id for c in second.cameras]


def test_sensors_lie_between_segment_endpoints() -> None:
    network = load_network()
    for sensor in network.sensors:
        segment = network.segment_by_id(sensor.segment_id)
        lat_lo, lat_hi = sorted((segment.start[0], segment.end[0]))
        lon_lo, lon_hi = sorted((segment.start[1], segment.end[1]))
        assert lat_lo <= sensor.lat <= lat_hi
        assert lon_lo <= sensor.lon <= lon_hi


def test_segment_names_are_trilingual() -> None:
    network = load_network()
    for segment in network.segments:
        assert segment.name_en and segment.name_he and segment.name_ar
