# Paper2Result — Architecture

> **Paper → Claim → Method → Code → Sandbox Run → Result → Graph Update**

This document describes the hackathon architecture for [Paper2Result](https://github.com/ali-amjad52114/Paper2Result). Optimized for a **4-person team**, **one demo loop**, and **sponsor clarity**.

---

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph User["👤 User / Judge"]
        Browser["Browser"]
    end

    subgraph Frontend["Frontend — Person A"]
        UI["React App (4 screens)"]
        Home["Home / Paper Selection"]
        Graph["Graph View"]
        Method["Method Detail Panel"]
        RunUI["Run Result Panel"]
    end

    subgraph API["API Layer — Person B"]
        FastAPI["FastAPI"]
        Routes["/papers · /build-graph · /graph<br/>/methods/:id/generate-and-run"]
    end

    subgraph Data["Data & Graph — Person B"]
        Seed["data/papers.json<br/>(preloaded)"]
        Neo4j[("Neo4j Aura<br/>Knowledge Graph")]
        BB[("Butterbase<br/>papers · runs · artifacts")]
    end

    subgraph Execution["Execution — Person C"]
        Orch["Orchestration"]
        Codegen["Codegen<br/>template / LLM"]
        Runner["runExperiment()"]
        Daytona["Daytona Sandbox"]
        RR["RocketRide Pipeline<br/>(optional wrapper)"]
    end

    subgraph Product["Product — Ali"]
        Demo["Demo Script · README · Submit"]
    end

    Browser --> UI
    UI --> Home & Graph & Method & RunUI
    UI -->|REST| FastAPI
    FastAPI --> Routes
    Routes --> Seed
    Routes --> Neo4j
    Routes --> BB
    Routes --> Orch
    Orch --> RR
    Orch --> Codegen
    Orch --> Runner
    Runner --> Daytona
    Codegen --> Runner
    Runner -->|stdout · metric| Routes
    Routes -->|attach run + result| Neo4j
    Demo -.->|scope · pitch| UI
```

---

## 2. Winning Demo Loop (Sequence)

The **one feature that must work**:

```mermaid
sequenceDiagram
    actor Judge
    participant UI as Frontend
    participant API as FastAPI
    participant Gen as Codegen
    participant Day as Daytona
    participant N4j as Neo4j

    Judge->>UI: Click "Generate + Run Experiment"
    UI->>API: POST /methods/method_1/generate-and-run

    API->>Gen: Load method_1 plan
    Gen-->>API: CodeArtifact (experiment_method_1.py)

    API->>Day: runExperiment(code)
    Note over Day: Isolated sandbox<br/>stdout · stderr · runtime
    Day-->>API: status=success, F1=0.81

    API->>N4j: MERGE ExperimentRun + Result nodes
    API->>N4j: SUPPORTS_OR_WEAKENS → Claim

    API-->>UI: { artifact, run, result, graph_delta }
    UI->>Judge: Show code + logs + metric
    UI->>Judge: Graph highlights new Run + Result nodes

    Note over Judge,UI: "The graph now knows not only<br/>what the paper claimed,<br/>but what actually ran."
```

---

## 3. Four Screens → API → Backends

```mermaid
flowchart LR
    subgraph S1["Screen 1: Home"]
        P1["List 3 papers"]
        B1["Build Research Graph"]
    end

    subgraph S2["Screen 2: Graph"]
        G1["Force graph viz"]
        G2["Click Method node"]
    end

    subgraph S3["Screen 3: Method Panel"]
        M1["Claim + plan"]
        M2["Generate + Run"]
    end

    subgraph S4["Screen 4: Run Result"]
        R1["Code file"]
        R2["Sandbox logs"]
        R3["Metric + graph update"]
    end

    B1 -->|POST /build-graph| Neo4j[("Neo4j")]
    G1 -->|GET /graph| Neo4j
    M2 -->|POST /generate-and-run| Pipeline
    R3 -->|graph_delta| Neo4j

    subgraph Pipeline["Execution Pipeline"]
        Pipeline --> Codegen2["Template codegen"]
        Codegen2 --> Daytona2["Daytona"]
        Daytona2 --> Attach["Attach to graph"]
    end
```

---

## 4. Knowledge Graph Model (Neo4j)

```mermaid
flowchart TB
    P1["Paper<br/>paper_1"]
    P2["Paper<br/>paper_2"]
    C1["Claim<br/>claim_1"]
    M1["Method<br/>method_1"]
    D1["Dataset<br/>dataset_1"]
    CA["CodeArtifact<br/>artifact_1"]
    ER["ExperimentRun<br/>run_1"]
    RES["Result<br/>result_1"]

    P1 -->|MAKES_CLAIM| C1
    P1 -->|USES_METHOD| M1
    M1 -->|EVALUATED_ON| D1
    P1 -->|CITES| P2
    M1 -->|GENERATES_CODE| CA
    CA -->|EXECUTED_AS| ER
    ER -->|PRODUCED| RES
    RES -->|SUPPORTS_OR_WEAKENS| C1

    style ER fill:#4ade80,stroke:#166534
    style RES fill:#4ade80,stroke:#166534
    style CA fill:#fbbf24,stroke:#92400e
```

**Green nodes** appear **after** the demo run. **Yellow** = generated at run time.

---

## 5. Sponsor / Tool Mapping

```mermaid
flowchart TB
    subgraph Sponsors["HackwithBay Partners"]
        N4j["Neo4j<br/>Graph storage"]
        Day["Daytona<br/>Sandbox execution"]
        BB["Butterbase<br/>App + persistence"]
        RR["RocketRide<br/>Pipeline orchestration"]
        OAI["OpenAI / LLM<br/>Optional codegen"]
    end

    subgraph Roles["Team Ownership"]
        PB["Person B<br/>Neo4j + API"]
        PC["Person C<br/>Daytona + RocketRide"]
        PA["Person A<br/>Frontend"]
        Ali["Ali<br/>Butterbase submit + pitch"]
    end

    N4j --- PB
    Day --- PC
    RR --- PC
    BB --- Ali
    BB --- PB
    OAI --- PC
    PA --- PA

    subgraph Proof["Judge sees"]
        Proof1["Graph with Run nodes"]
        Proof2["Live sandbox logs"]
        Proof3["Deployed app URL"]
        Proof4["Multi-step pipeline"]
    end

    N4j --> Proof1
    Day --> Proof2
    BB --> Proof3
    RR --> Proof4
```

| Sponsor | Role in Paper2Result | Owner | Demo proof |
|---------|----------------------|-------|------------|
| **Neo4j** | Papers, claims, methods, runs, results | Person B | Graph updates after run |
| **Daytona** | Isolated code execution | Person C | Real stdout + runtime |
| **RocketRide** | generate → run → graph update | Person C | Observable pipeline waves |
| **Butterbase** | Deployed UI, run history, submission | Ali / B | Live URL + `app_id` |
| **OpenAI** | Optional LLM codegen | Person C | Template-first for reliability |

---

## 6. Deployment Architecture

```mermaid
flowchart TB
    Judge["Judge (incognito browser)"]

    subgraph Public["Public URLs"]
        FE["Frontend<br/>Butterbase deploy<br/>or Vercel/Netlify"]
        API_URL["API<br/>Railway / Render / Fly"]
        RRCloud["RocketRide Cloud<br/>(optional)"]
    end

    subgraph Private["Managed services"]
        N4jAura[("Neo4j Aura")]
        DayCloud["Daytona API"]
        BBAPI["Butterbase API"]
    end

    Judge --> FE
    FE --> API_URL
    API_URL --> N4jAura
    API_URL --> DayCloud
    API_URL --> BBAPI
    FE -.->|optional| RRCloud
    RRCloud -.-> API_URL
```

**Minimum for submission:** Frontend URL + GitHub repo. API can be same origin or separate HTTPS endpoint.

---

## 7. Fallback / Abstraction Layers

```mermaid
flowchart TB
    API["POST /methods/:id/generate-and-run"]

    API --> OrchAbs["orchestration.py"]
    OrchAbs -->|ROCKETRIDE_PIPELINE_URL set| RR["RocketRide Cloud"]
    OrchAbs -->|fallback| Local["local_pipeline()"]

    Local --> GenAbs["codegen.py"]
    GenAbs -->|template| Tmpl["method_1.py.j2"]
    GenAbs -->|OPENAI_API_KEY + toggle| LLM["gpt-4o-mini"]

    Local --> RunAbs["execution.py"]
    RunAbs -->|DAYTONA_API_KEY set| Day["Daytona SDK"]
    RunAbs -->|fallback| Sub["local subprocess"]

  style Day fill:#4ade80,stroke:#166534
  style Tmpl fill:#4ade80,stroke:#166534
  style RR fill:#fbbf24,stroke:#92400e
  style LLM fill:#fbbf24,stroke:#92400e
```

| Layer | Primary | Fallback | Label in demo |
|-------|---------|----------|---------------|
| Orchestration | RocketRide pipeline | FastAPI sequential | Document in README |
| Codegen | Jinja2 template | LLM | "Template-generated" |
| Execution | Daytona | Local subprocess | Badge if simulated |

---

## 8. Team Integration Contract

All four people integrate through **one endpoint**:

```
POST /api/methods/method_1/generate-and-run
```

**Response shape (freeze at hour 1):**

```json
{
  "artifact": {
    "id": "artifact_1",
    "filename": "experiment_method_1.py",
    "content": "..."
  },
  "run": {
    "id": "run_1",
    "status": "success",
    "stdout": "F1 score: 0.81",
    "stderr": "",
    "runtime_seconds": 4.2,
    "sandbox_provider": "daytona"
  },
  "result": {
    "metric_name": "F1 Score",
    "metric_value": 0.81,
    "summary": "Generated implementation ran successfully on toy data."
  },
  "graph_delta": {
    "nodes": [...],
    "edges": [...]
  }
}
```

```mermaid
flowchart LR
    A["Person A<br/>Frontend"] -->|calls| Contract["generate-and-run"]
    B["Person B<br/>Neo4j + API"] -->|implements| Contract
    C["Person C<br/>Daytona + RR"] -->|runs code| Contract
    Ali["Ali<br/>Demo"] -->|guards scope| Contract
```

---

## 9. What We Are NOT Building

```mermaid
flowchart TB
    subgraph Build["✅ Build"]
        B1["1 method runnable"]
        B2["3 papers preloaded"]
        B3["4 screens"]
        B4["Real Daytona run"]
        B5["Real graph update"]
    end

    subgraph Skip["❌ Skip"]
        S1["PDF parser"]
        S2["Paper chatbot"]
        S3["Multi-method synthesis"]
        S4["Benchmark suite"]
        S5["Giant graph explorer"]
    end
```

---

## Related docs

- [Execution Plan](./EXECUTION_PLAN.md) — full hackathon plan, task board, risks
- [README](../README.md) — project overview
