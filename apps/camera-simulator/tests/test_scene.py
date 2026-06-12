from camera_simulator.scene import IncidentKind, Scene, SceneConfig


def test_initial_population_matches_target_density() -> None:
    scene = Scene(SceneConfig(lanes=3, vehicles_per_lane=4, density=1.0, seed=1))
    assert scene.target_count == 12
    assert len(scene.vehicles) == 12


def test_density_scales_vehicle_count() -> None:
    light = Scene(SceneConfig(lanes=3, density=0.5, seed=1))
    heavy = Scene(SceneConfig(lanes=3, density=2.0, seed=1))
    assert len(heavy.vehicles) > len(light.vehicles)


def test_step_is_deterministic_under_seed() -> None:
    a = Scene(SceneConfig(lanes=3, density=1.0, seed=42))
    b = Scene(SceneConfig(lanes=3, density=1.0, seed=42))
    for _ in range(30):
        a.step()
        b.step()
    assert [(v.id, round(v.position, 6)) for v in a.vehicles] == [
        (v.id, round(v.position, 6)) for v in b.vehicles
    ]


def test_density_maintained_after_recycling() -> None:
    scene = Scene(SceneConfig(lanes=3, density=1.0, seed=7))
    target = scene.target_count
    for _ in range(200):
        scene.step()
    assert len(scene.vehicles) == target


def test_vehicles_stay_in_bounds_when_no_incident() -> None:
    scene = Scene(SceneConfig(lanes=3, density=1.0, seed=7))
    for _ in range(200):
        scene.step()
        for vehicle in scene.vehicles:
            assert -0.001 <= vehicle.position <= 1.001


def test_stopped_vehicle_incident_holds_position() -> None:
    scene = Scene(SceneConfig(lanes=3, density=1.0, seed=3))
    vid = scene.inject_incident(IncidentKind.STOPPED_VEHICLE)
    stopped = next(v for v in scene.vehicles if v.id == vid)
    start = stopped.position
    for _ in range(50):
        scene.step()
    assert stopped.position == start
    assert vid in scene.active_incidents


def test_wrong_way_vehicle_travels_backwards() -> None:
    scene = Scene(SceneConfig(lanes=3, density=1.0, seed=3))
    vid = scene.inject_incident(IncidentKind.WRONG_WAY)
    vehicle = next(v for v in scene.vehicles if v.id == vid)
    start = vehicle.position
    scene.step()
    assert vehicle.position < start
