import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_shared_models():
    from shared.models import Event, Topic, StationStatus, SimConfig
    event = Event(
        timestamp=1,
        source_id="test",
        topic=Topic.PRODUCTION,
        event_type="test_event",
    )
    assert event.event_id is not None
    assert event.timestamp == 1
    print("[PASS] shared models import and basic validation")


def test_track01_event_bus():
    from track_01_core_engine.src.event_bus import EventBus
    bus = EventBus()
    assert hasattr(bus, "publish")
    assert hasattr(bus, "subscribe")
    print("[PASS] Track 01 EventBus interface")


def test_track01_simulator():
    from track_01_core_engine.src.simulator import Simulator
    assert hasattr(Simulator, "run")
    assert hasattr(Simulator, "tick")
    print("[PASS] Track 01 Simulator interface")


def test_track02_base_agent():
    from track_02_agent_runtime.src.agent import BaseAgent
    assert hasattr(BaseAgent, "observe")
    assert hasattr(BaseAgent, "think")
    assert hasattr(BaseAgent, "act")
    assert hasattr(BaseAgent, "on_tick")
    print("[PASS] Track 02 BaseAgent interface")


def test_track02_llm_client():
    from track_02_agent_runtime.src.llm_client import LLMClient
    assert hasattr(LLMClient, "call")
    print("[PASS] Track 02 LLMClient interface")


def test_track03_station():
    from track_03_physical_twin.src.station import Station
    s = Station(station_id="S1", line_id="L1", station_type="assembly")
    assert s.status == StationStatus.IDLE
    print("[PASS] Track 03 Station default state")


def test_track03_state_machine():
    from track_03_physical_twin.src.station import Station
    from track_03_physical_twin.src.exceptions import StateTransitionError
    s = Station(station_id="S1", line_id="L1", station_type="assembly")
    s.start_work("O1", 10)
    assert s.status == StationStatus.WORKING
    try:
        s.transition_to(StationStatus.IDLE)
        assert False, "Should not allow WORKING -> IDLE directly"
    except StateTransitionError:
        pass
    print("[PASS] Track 03 State machine enforcement")


def test_track04_station_agent():
    from track_04_production.src.station_agent import StationAgent
    assert hasattr(StationAgent, "on_tick")
    print("[PASS] Track 04 StationAgent interface")


def test_track05_warehouse():
    from track_05_logistics.src.warehouse_agent import WarehouseAgent
    assert hasattr(WarehouseAgent, "on_tick")
    print("[PASS] Track 05 WarehouseAgent interface")


def test_track05_agv():
    from track_05_logistics.src.logistics_agent import LogisticsAgent
    assert hasattr(LogisticsAgent, "on_tick")
    print("[PASS] Track 05 LogisticsAgent interface")


def test_track06_qc():
    from track_06_quality_maintenance.src.qc_agent import QCAgent
    assert hasattr(QCAgent, "on_tick")
    print("[PASS] Track 06 QCAgent interface")


def test_track06_maintenance():
    from track_06_quality_maintenance.src.maintenance_agent import MaintenanceAgent
    assert hasattr(MaintenanceAgent, "on_tick")
    print("[PASS] Track 06 MaintenanceAgent interface")


def test_track07_planner():
    from track_07_planning.src.planner_agent import PlannerAgent
    assert hasattr(PlannerAgent, "on_tick")
    print("[PASS] Track 07 PlannerAgent interface")


def test_track08_metrics():
    from track_08_metrics.src.metrics import MetricsCollector
    assert hasattr(MetricsCollector, "throughput")
    assert hasattr(MetricsCollector, "yield_rate")
    assert hasattr(MetricsCollector, "oee")
    print("[PASS] Track 08 MetricsCollector interface")


def test_track09_loader():
    from track_09_scenarios.src.loader import ScenarioLoader
    assert hasattr(ScenarioLoader, "load")
    assert hasattr(ScenarioLoader, "validate")
    print("[PASS] Track 09 ScenarioLoader interface")


def test_track10_dashboard():
    from track_10_dashboard.src.dashboard import Dashboard
    assert hasattr(Dashboard, "render")
    print("[PASS] Track 10 Dashboard interface")


if __name__ == "__main__":
    tests = [
        test_shared_models,
        test_track01_event_bus,
        test_track01_simulator,
        test_track02_base_agent,
        test_track02_llm_client,
        test_track03_station,
        test_track03_state_machine,
        test_track04_station_agent,
        test_track05_warehouse,
        test_track05_agv,
        test_track06_qc,
        test_track06_maintenance,
        test_track07_planner,
        test_track08_metrics,
        test_track09_loader,
        test_track10_dashboard,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed > 0:
        sys.exit(1)
