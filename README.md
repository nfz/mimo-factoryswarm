<p align="center">
  <h1 align="center">MiMo FactorySwarm</h1>
  <p align="center">
    <strong>A 1000-Agent Digital Twin for Manufacturing Line Simulation</strong>
  </p>
  <p align="center">
    <a href="#architecture">Architecture</a> •
    <a href="#agent-roles">Agent Roles</a> •
    <a href="#simulation-logic">Simulation Logic</a> •
    <a href="#development-roadmap">Roadmap</a> •
    <a href="#getting-started">Getting Started</a>
  </p>
</p>

---

## What is FactorySwarm?

FactorySwarm is a **multi-agent digital twin system** that simulates an entire manufacturing assembly line as a collaborative network of lightweight AI agents.

Instead of treating a factory as a monolithic optimization problem, we model every physical entity — workstations, conveyor belts, quality inspectors, warehouse workers, AGV vehicles, maintenance crews, production planners — as an independent agent with its own state, role, and decision-making capability. These agents communicate through a unified event bus and coordinate in real time, just like a real factory floor.

The system is designed to answer questions that traditional simulations cannot:

- **What happens when a key workstation breaks down mid-shift?** How does the failure propagate through the production line, and how do maintenance, logistics, and scheduling agents respond?
- **What is the actual impact of an urgent order insertion?** Can the current production plan absorb it, or does it trigger a cascade of rescheduling decisions?
- **Where is the real bottleneck?** Not just "which workstation is slowest", but why — is it material shortage, quality issues, logistics delays, or uneven workload distribution?
- **How do different agent collaboration strategies affect overall KPIs?** Compare centralized vs. distributed decision-making across throughput, yield rate, OEE, and order fulfillment.

## Why 1000 Agents?

A real factory is not controlled by a single brain. It operates through thousands of independent entities, each making local decisions within their role boundaries. FactorySwarm replicates this architecture:

| Agent Category | Count | Role |
|---|---|---|
| Station Worker Agents | ~700 | Individual workstations performing specific operations |
| Quality Control Agents | ~80 | Inspection, defect detection, rework decisions |
| Logistics / AGV Agents | ~80 | Material transport and delivery routing |
| Maintenance Agents | ~50 | Fault diagnosis, repair dispatch, spare parts management |
| Warehouse Agents | ~30 | Inventory tracking, replenishment triggers |
| Line Management Agents | ~20 | Per-line supervision, bottleneck reporting |
| Planning & Optimization | ~20 | Production scheduling, order coordination, capacity optimization |
| Safety & Environment | ~20 | Energy monitoring, anomaly alerts, safety compliance |
| **Total** | **~1000** | |

These are not 1000 independent processes competing for resources. The system uses **event-driven scheduling with lightweight role-based execution** — agents wake up in response to relevant events, make role-appropriate decisions, and publish their actions back to the event bus. This architecture naturally scales from a 20-agent MVP to a 1000-agent full simulation.

## Architecture

```
                        ┌─────────────────────┐
                        │   Factory Manager    │
                        │   (Macro Control)    │
                        └──────────┬──────────┘
                                   │
                        ┌──────────┴──────────┐
                        │   Production Planner  │
                        │   (Scheduling Brain)  │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
     ┌────────┴────────┐ ┌───────┴────────┐ ┌────────┴────────┐
     │  Line A (10~80   │ │  Line B (10~80  │ │  Line C (10~80  │
     │  Station Agents) │ │  Station Agents) │ │  Station Agents) │
     │  + Line Leader   │ │  + Line Leader   │ │  + Line Leader   │
     └────────┬────────┘ └───────┬────────┘ └────────┬────────┘
              │                  │                    │
              └──────────────────┼────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │      Event Bus          │
                    │  (Unified Communication) │
                    └──┬─────┬─────┬─────┬───┘
                       │     │     │     │
                  ┌────┴┐ ┌──┴──┐ ┌┴───┐ ┌┴────┐
                  │ QC  │ │ AGV │ │ WH │ │Maint│
                  │Team │ │Fleet│ │    │ │Team │
                  └─────┘ └─────┘ └────┘ └─────┘
```

### Core Layers

**1. Simulation Engine (Time & Events)**

The foundation of the entire system. A discrete Tick-based virtual clock drives all agents forward in lockstep. Every agent action, state change, and decision is timestamped and recorded as a structured event on the global event bus. This ensures that the simulation is not just producing results — it is producing an **auditable, replayable, explainable** factory operation narrative.

**2. Agent Runtime (Role & Behavior)**

Every agent follows a unified lifecycle — observe relevant events, think (LLM reasoning or rule-based logic), act (update state or publish new events) — but each role has distinct responsibilities, output styles, and decision boundaries. A maintenance agent will never override a planner's scheduling decision; a warehouse agent will never attempt quality inspection. This role separation is what makes the simulation feel like a real factory rather than a single model wearing different name tags.

**3. Physical Twin Layer (Hard Constraints)**

Factory physics are enforced as immutable rules, not LLM suggestions. A broken workstation cannot resume production until maintenance completes. A QC-failed product cannot proceed to the next station. Inventory cannot go below zero. This layer prevents AI hallucination from corrupting the simulation's physical integrity.

## Agent Roles

### Management Layer

- **Factory Manager Agent** — Monitors overall OEE, capacity targets, and cross-line coordination. Escalates critical issues to the planner.
- **Production Planner Agent** — The primary reasoning engine. Ingests full factory state to generate scheduling plans, handle urgent order insertions, and redistribute workload across lines. This is the most token-intensive role in the system.

### Shop Floor Layer

- **Line Supervisor Agent** — One per production line. Observes all station events within its line, identifies bottlenecks (e.g., "Station B has 10 work-in-progress items while Station C is idle"), and reports to the factory manager.
- **Station Agent** — The fundamental production unit. Each agent represents a physical workstation performing a specific operation (soldering, assembly, screw fastening, labeling, etc.). Progresses through work orders tick-by-tick, requests materials when needed, and broadcasts failures immediately.

### Support Layer

- **Quality Control Agent** — Inspects completed work items against configurable yield rates. Flags defects, triggers rework loops, and feeds quality metrics back to the planner.
- **Warehouse Agent** — Maintains global inventory levels. Responds to material requests, monitors stock thresholds, and triggers procurement warnings.
- **Logistics Agent (AGV)** — Physical material transport. Has location, route, and speed attributes. Delivery takes real simulation time — cannot teleport. Becomes a real logistics constraint.
- **Maintenance Agent** — Responds to machine failure events. Travels to the fault location (consuming ticks), performs repairs (consuming MTTR), and restores the workstation to operational status.

## Simulation Logic

### What Gets Simulated

The system models real factory dynamics that affect production outcomes:

| Dimension | Behavior |
|---|---|
| **Production Rhythm** | Each workstation has different processing times, creating natural beat differences and queue buildup |
| **Queue & Bottleneck** | Slow stations accumulate work-in-progress; fast stations idle waiting for input |
| **Material Shortage** | Warehouse depletion triggers stockout events, causing downstream station stalls |
| **Equipment Failure** | Random breakdowns with realistic MTBF/MTTR distributions |
| **Quality Failures** | Probabilistic defect detection with rework routing back to responsible stations |
| **Dynamic Rescheduling** | Urgent order insertion forces planner to rebalance across all lines |
| **Logistics Delay** | AGV delivery time is a physical constraint — distance and speed matter |
| **KPI Tracking** | Throughput, yield rate, OEE, average cycle time, downtime rate, order fulfillment rate |

### Event-Driven Communication

All agent interactions go through the event bus. No agent can directly call another agent's methods. This ensures:

- **Loose coupling** — agents can be added, removed, or reconfigured without breaking others
- **Full traceability** — every decision and state change is recorded with a timestamp
- **Scalable observation** — system-level analytics aggregate events across all agents

### Example Event Flow

```
Tick 120: Station B3 emits MaterialRequest (screws, qty: 200)
Tick 120: Warehouse Agent receives request, checks stock → sufficient
Tick 121: Warehouse Agent emits MaterialDispatch (target: B3, item: screws)
Tick 121: AGV Agent receives dispatch, calculates route → 8 ticks travel time
Tick 129: AGV Agent emits MaterialDelivered (target: B3)
Tick 129: Station B3 resumes processing
```

Every step is timestamped, traceable, and explainable.

## Demo Scenario: Smartphone Assembly Line

**Input:**
- Daily orders: 1,000 units
- 3 production lines, each with 10~30 workstations
- One material shipment delayed by 2 hours
- One critical workstation fails at Tick 500

**Output:**
- Real-time factory dashboard showing station states (working / idle / waiting / broken / maintenance)
- Live event trace showing failure propagation and response
- Bottleneck identification with root cause analysis
- KPI comparison: with vs. without dynamic rescheduling
- Maintenance response timeline and production impact assessment

## Development Roadmap

- [x] System architecture design and module decomposition
- [x] Product-level module definitions with delivery criteria
- [x] 10-track development plan for parallel Agent collaboration
- [x] Error-driven dynamic evolution workflow design
- [ ] Core simulation engine (virtual clock + event bus)
- [ ] Agent runtime (LLM client + base agent class)
- [ ] Physical twin layer (state machines + hard constraints)
- [ ] Production line agents (stations + line supervisors)
- [ ] Support agents (warehouse, logistics, QC, maintenance)
- [ ] Planning agents (factory manager + production planner)
- [ ] Metrics collection and analytics pipeline
- [ ] Scenario configuration system (JSON-based factory setups)
- [ ] CLI dashboard with real-time visualization (Rich/Typer)
- [ ] 20-Agent MVP demo (single production line)
- [ ] 100-Agent benchmark (multi-line simulation)
- [ ] 1000-Agent full factory simulation

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Agent Framework | Custom lightweight runtime (no heavy framework dependency) |
| LLM Integration | OpenAI-compatible API (MiMo-V2.5-Pro) |
| Data Validation | Pydantic v2 |
| CLI & Dashboard | Rich + Typer |
| Async Runtime | asyncio |
| Testing | pytest |

## Project Structure

```
mimo-factoryswarm/
├── src/                    # Core simulation engine
│   ├── simulator.py        # Virtual clock & main loop
│   ├── event_bus.py        # Global event bus (Pub/Sub)
│   ├── events.py           # Pydantic event schemas
│   ├── agent.py            # Base agent class
│   ├── factory.py          # Factory environment singleton
│   ├── station.py          # Workstation data structure & state machine
│   ├── order.py            # BOM & routing definitions
│   ├── metrics.py          # KPI calculation & data export
│   └── main.py             # System entry point & UI
├── agents/                 # Agent implementations
│   ├── station_agent.py    # Workstation agent
│   ├── line_supervisor_agent.py
│   ├── warehouse_agent.py
│   ├── logistics_agent.py
│   ├── qc_agent.py
│   ├── maintenance_agent.py
│   ├── planner_agent.py
│   └── manager_agent.py
├── utils/                  # Shared utilities
│   └── llm_client.py       # LLM API client with retry & rate limiting
├── scenarios/              # Simulation configurations
│   ├── baseline_factory.json
│   ├── shortage_case.json
│   └── machine_failure_case.json
├── prompts/                # LLM prompt templates per role
├── docs/                   # Architecture & design documents
│   ├── task_allocation.md  # 10-track module definitions
│   └── multi_agent_workflow.md  # Error-driven dev workflow
├── .gitignore
├── package.json
└── requirements.txt
```

## Getting Started

> **Note:** This project is currently in active development. The core simulation engine and agent implementations are being built following the 10-track parallel development plan documented in [docs/task_allocation.md](docs/task_allocation.md).

### Prerequisites

- Python 3.11+
- Access to an OpenAI-compatible LLM API endpoint

### Installation

```bash
git clone https://github.com/nfz/mimo-factoryswarm.git
cd mimo-factoryswarm
pip install -r requirements.txt
```

### Configuration

Set your LLM API endpoint and credentials:

```bash
export LLM_API_BASE="https://your-api-endpoint/v1"
export LLM_API_KEY="your-api-key"
export LLM_MODEL="your-model-name"
```

### Run Simulation (Coming Soon)

```bash
python src/main.py --scenario scenarios/baseline_factory.json
```

## Why MiMo

This project is designed from the ground up to leverage high-volume LLM inference:

- **Multi-agent decision making** — each agent makes role-specific judgments every simulation tick
- **Long-context state synthesis** — the planner agent ingests full factory state for scheduling decisions
- **Event summarization** — agents compress event streams into actionable intelligence
- **Anomaly analysis** — complex failures require multi-step reasoning chains
- **Dynamic rescheduling** — urgent order insertion triggers full factory state evaluation
- **Benchmark iterations** — comparing strategies across scenarios requires repeated full simulations

A single 100-agent benchmark run may involve 150+ model calls. Scaling to 1000 agents with multi-scenario optimization testing can generate 1000+ calls per simulation round.

## License

This project is open source under the MIT License.

---

<p align="center">
  Built for exploring how large-scale lightweight AI agents can collaborate<br/>
  to simulate complex real-world factory operations.
</p>
