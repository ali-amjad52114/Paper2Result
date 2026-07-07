# Paper-to-Results Graph — Hackathon Execution Plan

> **Team:** 4 (Ali + 3 teammates)  
> **Event:** HackwithBay 3.0 — *Thoughtful Agents for Productivity*  
> **Repo:** [github.com/ali-amjad52114/Paper2Result](https://github.com/ali-amjad52114/Paper2Result)  
> **Status:** Plan only — do not code until team aligns on Section 20

---

## 1. One-Sentence Product Definition

**Paper-to-Results Graph turns a research paper's method into a sandboxed experiment and records what actually ran—not just what was claimed—in a living knowledge graph.**

---

## 2. Demo Story (Exact Script)

**Duration:** 90–120 seconds. One judge laptop, incognito tab, live URL.

| Step | Who clicks | What happens on screen | What Ali says |
|------|------------|------------------------|---------------|
| 1 | Ali | **Home** — 3 papers on "Graph-Based Anomaly Detection" | "Most tools help you read papers. We help you test them." |
| 2 | Ali | Clicks **Build Research Graph** | "We've pre-extracted claims and methods into a graph." |
| 3 | Ali | **Graph View** — Papers, Claims, Methods, Datasets, citations | "This is Neo4j — structure, not chat history." |
| 4 | Ali | Clicks **Method** node: *Local Neighborhood Anomaly Score* | Method detail panel opens |
| 5 | Ali | Clicks **Generate + Run Experiment** | Loading states: Generating code → Starting sandbox → Running |
| 6 | All | **Run Result** panel — code filename, stdout, `F1 Score: 0.81`, runtime 4.2s | "Code generated, executed in Daytona — isolated sandbox." |
| 7 | Ali | Graph refreshes — new **ExperimentRun** + **Result** nodes appear; edge to Claim | **"The graph now knows not only what the paper claimed, but what actually ran."** |
| 8 | Ali | Points to `SUPPORTS_OR_WEAKENS` edge on claim | "Result linked back to the claim. That's the closed loop." |

**Backup line if run fails:** "Even failures are evidence — the graph records stderr and a failed run node. That's still more than a summary."

---

## 3. MVP Scope (Must-Have Only)

| # | Feature | Why |
|---|---------|-----|
| 1 | 3 preloaded papers as structured JSON | No PDF parser dependency |
| 2 | **Build Research Graph** → Neo4j populated | Graph is the product |
| 3 | Graph visualization with 8 node types | Judge sees structure |
| 4 | Click Method → detail panel | Selection UX |
| 5 | **Generate + Run Experiment** one button | Winning moment |
| 6 | Generated Python file (template or LLM) | Visible artifact |
| 7 | **Real Daytona run** with stdout/stderr/runtime | Proof of execution |
| 8 | Result metric captured (e.g. F1) | Quantified outcome |
| 9 | Graph update: ExperimentRun + Result nodes | Closed loop |
| 10 | Deployed live URL (Butterbase or Vercel) | Submission requirement |
| 11 | README + sponsor mapping | Judging + $200 Butterbase prize |

**Single method for demo:** `method_1` on `paper_1` only. Other papers exist for graph richness, not for running.

---

## 4. Non-Goals (Explicit)

- Arbitrary PDF upload + parse at demo time
- Multi-paper code synthesis
- Generic "chat with papers"
- Full graph explorer (search, filters, 3D, etc.)
- Automatic scientific validation / peer review
- Benchmark suite across methods
- User auth / multi-tenant
- More than 4 screens
- Perfect LLM codegen — template-first
- RocketRide Cloud deploy if it blocks the run loop (document integration point instead)

---

## 5. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (Vite + React) — Butterbase deploy or static host │
│  Screens: Home | Graph | Method Panel | Run Result          │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST
┌──────────────────────────▼──────────────────────────────────┐
│  API (FastAPI) — api/main.py                                │
│  /papers  /build-graph  /graph  /method/:id/generate|run    │
└──────┬─────────────┬──────────────┬─────────────────────────┘
       │             │              │
       ▼             ▼              ▼
┌──────────┐  ┌─────────────┐  ┌─────────────────────────────┐
│ Seed JSON│  │ Neo4j Aura  │  │ Butterbase (optional layer) │
│ data/    │  │ Graph store │  │ papers, runs, artifacts     │
└──────────┘  └─────────────┘  └─────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │  Execution Service       │
              │  runExperiment(code)     │
              │  → Daytona SDK (real)    │
              │  → local subprocess stub │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │  RocketRide (orchestration)│
              │  POST /pipeline/run      │
              │  waves: gen → run → graph  │
              │  FALLBACK: API calls steps │
              └─────────────────────────┘
```

### Component decisions

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Frontend | Vite + React + `react-force-graph-2d` or `vis-network` | Fast graph viz, teammate 1 knows React |
| API | FastAPI | Same language as Daytona; easy JSON |
| Graph DB | Neo4j Aura free | Sponsor requirement, Cypher demo |
| Persistence | JSON files + Neo4j; Butterbase if time | JSON works for hour 1–4 |
| Sandbox | Daytona SDK (`daytona` package) | Already verified in `main.py` |
| Orchestration | RocketRide pipeline **or** FastAPI sequential calls | RocketRide = thin wrapper calling same functions |
| LLM | OpenAI gpt-4o-mini for codegen **optional** | Template code for demo reliability |

### Fallback stubs

```python
# api/services/execution.py
async def runExperiment(code: str, method_id: str) -> RunResult:
    if os.getenv("DAYTONA_API_KEY"):
        return await run_daytona(code)      # REAL
    return run_local_subprocess(code)       # FALLBACK (same interface)
```

```python
# api/services/orchestration.py
async def execute_method_pipeline(method_id: str):
    if os.getenv("ROCKETRIDE_PIPELINE_URL"):
        return await call_rocketride(method_id)  # REAL
    return await local_pipeline(method_id)       # FALLBACK
```

---

## 6. Data Model

### TypeScript interfaces (frontend + shared types)

```typescript
export interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  claims: Claim[];
  methods: Method[];
  datasets: Dataset[];
  cites?: string[]; // paper ids
}

export interface Claim {
  id: string;
  text: string;
}

export interface Method {
  id: string;
  name: string;
  summary: string;
  implementation_plan: string[];
  dataset_id?: string;
  claim_ids?: string[];
}

export interface Dataset {
  id: string;
  name: string;
  description?: string;
}

export interface CodeArtifact {
  id: string;
  method_id: string;
  filename: string;
  content: string;
  generated_at: string;
  source: "template" | "llm";
}

export interface ExperimentRun {
  id: string;
  method_id: string;
  code_artifact_id: string;
  status: "pending" | "running" | "success" | "failed";
  runtime_seconds: number;
  stdout: string;
  stderr: string;
  sandbox_provider: "daytona" | "local";
  started_at: string;
  finished_at?: string;
}

export interface Result {
  id: string;
  run_id: string;
  metric_name: string;
  metric_value: number;
  summary: string;
  supports_claim_ids: string[];
  weakens_claim_ids: string[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: NodeType;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
}

export type NodeType =
  | "Paper" | "Claim" | "Method" | "Dataset"
  | "Citation" | "CodeArtifact" | "ExperimentRun" | "Result";

export type EdgeType =
  | "MAKES_CLAIM" | "USES_METHOD" | "EVALUATED_ON" | "CITES"
  | "GENERATES_CODE" | "EXECUTED_AS" | "PRODUCED"
  | "SUPPORTS_OR_WEAKENS";
```

---

## 7. Graph Schema (Neo4j)

### Node labels & key properties

| Label | Properties |
|-------|------------|
| `Paper` | `id`, `title`, `year` |
| `Claim` | `id`, `text` |
| `Method` | `id`, `name`, `summary` |
| `Dataset` | `id`, `name` |
| `CodeArtifact` | `id`, `filename`, `generated_at` |
| `ExperimentRun` | `id`, `status`, `runtime_seconds`, `stdout`, `stderr` |
| `Result` | `id`, `metric_name`, `metric_value`, `summary` |

### Relationships

| Relationship | From → To |
|--------------|-----------|
| `MAKES_CLAIM` | Paper → Claim |
| `USES_METHOD` | Paper → Method |
| `EVALUATED_ON` | Method → Dataset |
| `CITES` | Paper → Paper |
| `GENERATES_CODE` | Method → CodeArtifact |
| `EXECUTED_AS` | CodeArtifact → ExperimentRun |
| `PRODUCED` | ExperimentRun → Result |
| `SUPPORTS_OR_WEAKENS` | Result → Claim (`weight: float`, `direction: support\|weaken`) |

### Seed graph Cypher (run on build)

```cypher
// Papers
MERGE (p1:Paper {id: 'paper_1', title: 'Graph-Based Anomaly Detection for Sensor Streams', year: 2024})
MERGE (p2:Paper {id: 'paper_2', title: 'Streaming Graph Outlier Detection', year: 2023})
MERGE (p3:Paper {id: 'paper_3', title: 'Neighborhood-Based Sensor Fault Detection', year: 2022})

// Claims
MERGE (c1:Claim {id: 'claim_1', text: 'Local neighborhood scoring improves anomaly detection on sensor data.'})
MERGE (p1)-[:MAKES_CLAIM]->(c1)

// Methods
MERGE (m1:Method {id: 'method_1', name: 'Local Neighborhood Anomaly Score',
  summary: 'Builds a k-NN graph of sensor readings and scores local deviation.'})
MERGE (p1)-[:USES_METHOD]->(m1)

// Dataset
MERGE (d1:Dataset {id: 'dataset_1', name: 'Toy Sensor Anomaly Dataset'})
MERGE (m1)-[:EVALUATED_ON]->(d1)

// Citations
MERGE (p1)-[:CITES]->(p2)
MERGE (p1)-[:CITES]->(p3)
```

### Post-run Cypher (after experiment)

```cypher
MATCH (m:Method {id: $method_id})
MERGE (ca:CodeArtifact {id: $artifact_id, filename: $filename, generated_at: datetime()})
MERGE (m)-[:GENERATES_CODE]->(ca)
MERGE (run:ExperimentRun {id: $run_id, status: $status, runtime_seconds: $runtime,
  stdout: $stdout, stderr: $stderr})
MERGE (ca)-[:EXECUTED_AS]->(run)
MERGE (res:Result {id: $result_id, metric_name: $metric_name, metric_value: $metric_value,
  summary: $summary})
MERGE (run)-[:PRODUCED]->(res)
MATCH (c:Claim {id: $claim_id})
MERGE (res)-[:SUPPORTS_OR_WEAKENS {direction: 'support', weight: 0.81}]->(c)
RETURN run, res
```

### Graph API response shape

```json
{
  "nodes": [{"id": "paper_1", "label": "Graph-Based Anomaly...", "type": "Paper"}],
  "edges": [{"source": "paper_1", "target": "method_1", "type": "USES_METHOD"}]
}
```

---

## 8. File / Folder Plan

### Current repo

```
Paper2Result/
├── README.md              # Ali updates → Paper2Result branding
├── main.py                # Daytona smoke test (keep)
├── requirements.txt       # Expand for FastAPI, neo4j
├── .env.example
├── pipelines/.gitkeep     # RocketRide .pipe
└── docs/EXECUTION_PLAN.md # This file
```

### Target structure (create during hackathon)

```
Paper2Result/
├── README.md
├── docs/
│   ├── EXECUTION_PLAN.md
│   ├── DEMO_SCRIPT.md          # Ali — 1-page judge script
│   └── SPONSOR_MAPPING.md      # Ali — table for judges
├── data/
│   ├── papers.json             # Backend — 3 seed papers
│   └── templates/
│       └── method_1.py.j2      # Execution — codegen template
├── api/
│   ├── main.py                 # FastAPI app + routes
│   ├── requirements.txt
│   ├── services/
│   │   ├── graph.py            # Neo4j read/write
│   │   ├── codegen.py          # Template + optional LLM
│   │   ├── execution.py        # runExperiment() abstraction
│   │   ├── orchestration.py    # Pipeline entry (RR or local)
│   │   └── butterbase.py       # Optional persistence
│   └── models/
│       └── schemas.py          # Pydantic models
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── Home.tsx
│       │   ├── GraphView.tsx
│       │   ├── MethodPanel.tsx
│       │   └── RunResult.tsx
│       ├── components/
│       │   ├── PaperList.tsx
│       │   ├── ForceGraph.tsx
│       │   └── RunLog.tsx
│       └── api/client.ts
├── pipelines/
│   └── paper-to-results.pipe   # RocketRide — optional
├── scripts/
│   └── seed_neo4j.py           # One-time graph seed
└── main.py                     # Daytona smoke test (unchanged)
```

### Modify vs create

| File | Action | Owner |
|------|--------|-------|
| `README.md` | Rewrite for Paper-to-Results Graph | Ali |
| `requirements.txt` | Add fastapi, uvicorn, neo4j, jinja2 | Backend |
| `.env.example` | Add NEO4J_*, OPENAI_API_KEY, ROCKETRIDE_* | Backend |
| `data/papers.json` | **Create** | Backend |
| `api/*` | **Create** | Backend + Execution |
| `frontend/*` | **Create** | Frontend |
| `pipelines/paper-to-results.pipe` | **Create if time** | Execution |
| `main.py` | Keep as Daytona reference | Execution |

---

## 9. API Plan

Base URL: `/api`

| Method | Endpoint | Body | Response | Owner |
|--------|----------|------|----------|-------|
| `GET` | `/papers` | — | `Paper[]` | Backend |
| `POST` | `/build-graph` | — | `{ nodes: n, edges: m }` | Backend |
| `GET` | `/graph` | — | `{ nodes, edges }` | Backend |
| `GET` | `/methods/:id` | — | `Method` + paper context | Backend |
| `POST` | `/methods/:id/generate` | — | `CodeArtifact` | Execution |
| `POST` | `/methods/:id/run` | `{ use_llm?: bool }` | `ExperimentRun` (streaming status optional) | Execution |
| `GET` | `/runs/:id` | — | `ExperimentRun` + `Result?` | Backend |
| `POST` | `/runs/:id/attach-to-graph` | — | Updated graph snippet | Backend |

### Combined demo endpoint (shortcut)

If wiring separate steps is slow, add:

```
POST /methods/:id/generate-and-run
→ returns { artifact, run, result, graph_delta }
```

**Internal flow:**
1. `codegen.generate(method_id)` → template or LLM
2. `execution.runExperiment(code)` → Daytona
3. `graph.attach_run_result(...)` → Neo4j
4. Return full payload for UI

---

## 10. Sandbox Execution Plan

### Priority 1 — Real Daytona (verified)

Reuse pattern from `main.py`:

```python
def run_daytona(code: str) -> RunResult:
    sandbox = daytona.create()
    t0 = time.time()
    response = sandbox.process.code_run(code)
    return RunResult(
        status="success" if response.exit_code == 0 else "failed",
        stdout=response.result or "",
        stderr="" if response.exit_code == 0 else str(response.result),
        runtime_seconds=time.time() - t0,
    )
```

### Generated code requirements

- **Single file** `experiment_method_1.py`
- **No network** inside sandbox
- **Synthetic data inline** (numpy random or csv string)
- **Prints metric** in parseable format: `F1 score: 0.81`
- **Runs in < 30 seconds**

### Priority 2 — `runExperiment()` abstraction

Same interface, local `subprocess.run(["python", "-c", code])` with timeout.

### Priority 3 — Mock (labeled)

Only if Daytona down at demo time. UI shows badge: **"Simulated run — Daytona unavailable"**.

### Metric parsing

```python
import re
def parse_metric(stdout: str) -> tuple[str, float]:
    m = re.search(r"F1\s*score:\s*([\d.]+)", stdout, re.I)
    if m:
        return "F1 Score", float(m.group(1))
    return "Success", 1.0
```

---

## 11. RocketRide Plan

### Intended workflow

```
Webhook/HTTP trigger
  Wave 1: Load method from Butterbase/JSON
  Wave 2: LLM or template → generate code (tool_python)
  Wave 3: Call Daytona (tool_daytona) or HTTP to /run
  Wave 4: Parse result → write Neo4j (db_neo4j)
  Wave 5: Return graph delta
```

### Hackathon reality

| Time available | Approach |
|----------------|----------|
| **≥ 2 hours** | Deploy minimal `.pipe` to RocketRide Cloud; frontend calls pipeline URL |
| **< 2 hours** | FastAPI `orchestration.py` runs same steps; README shows `.pipe` diagram |

### Minimum viable RocketRide story

1. Copy `reference/rocketride-server/examples/agent-workflow.pipe`
2. Replace tools with: HTTP to your API OR inline `tool_daytona` + `db_neo4j`
3. Deploy one endpoint: `POST /run-method`
4. Ali mentions in pitch: *"RocketRide orchestrates extract → generate → run → graph update"*

### Placeholder file

`pipelines/paper-to-results.pipe` — even a JSON stub with node names is enough for README architecture diagram.

---

## 12. Butterbase Plan

### What to store (if integrated)

| Entity | Butterbase table | Fallback |
|--------|------------------|----------|
| Papers | `papers` | `data/papers.json` |
| Extractions | `extractions` | inline in papers.json |
| Code artifacts | `artifacts` + storage bucket | `api/storage/{id}.py` |
| Runs | `experiment_runs` | SQLite or JSON file |
| Logs | `run_logs` text column | same row |
| Graph metadata | `graph_builds` | Neo4j only |

### Hackathon path

| Phase | Butterbase |
|-------|------------|
| Hours 0–4 | Skip — JSON + Neo4j |
| Hours 4–6 | `init_app` + `papers` + `runs` tables if teammate 2 has MCP working |
| Hours 6–8 | Deploy frontend via Butterbase for **live URL** + submission `app_id` |

### Minimum for $200 prize

- Real Butterbase app with schema
- Deployed frontend URL
- Submit via `prep_and_submit_hackathon_entry` with `app_id`

Backend can stay on FastAPI elsewhere; Butterbase holds UI + run history.

---

## 13. OpenAI / LLM Plan

| Use case | Demo approach | LLM? |
|----------|---------------|------|
| Claim extraction | Pre-seeded JSON | ❌ Preloaded |
| Method summary | Pre-seeded JSON | ❌ Preloaded |
| Implementation plan | Pre-seeded JSON | ❌ Preloaded |
| Code generation | **Jinja2 template** `method_1.py.j2` | ⚠️ Optional enhancement |
| Result explanation | Template string from metric | ⚠️ Optional |

### Codegen strategy

```
1. Try template fill (method_id → template)     # 100% reliable
2. If OPENAI_API_KEY set AND user toggles LLM:  # nice-to-have
   prompt with implementation_plan → single .py file
3. Validate: file compiles (ast.parse)
4. If invalid → fall back to template
```

**Do not demo LLM codegen unless tested 3+ times before judging.**

---

## 14. Timeboxed Build Plan

Assume **8-hour hack** starting ~10:00 AM. Adjust if kickoff is later.

### Phase 1 — First 60 minutes (10:00–11:00)

| | |
|--|--|
| **Goal** | Align team, seed data frozen, repos + env working |
| **Ali** | Share this doc; lock demo topic; write DEMO_SCRIPT.md one-pager |
| **Frontend** | Vite scaffold, 4 empty routes, API client stub |
| **Backend** | `papers.json`, Pydantic models, `GET /papers` |
| **Execution** | Confirm Daytona runs `method_1` template script end-to-end |
| **Deliverable** | `papers.json` + Daytona prints F1 score |
| **Fallback** | Skip paper 2/3 content richness; 1 paper only |

### Phase 2 — Next 2 hours (11:00–1:00)

| | |
|--|--|
| **Goal** | API core + graph seed + basic UI |
| **Frontend** | Home + paper list + "Build Graph" button |
| **Backend** | Neo4j Aura provisioned, `POST /build-graph`, `GET /graph` |
| **Execution** | `runExperiment()` + `POST /methods/:id/run` (no UI yet) |
| **Deliverable** | Click Build Graph → JSON graph returns; run works via curl |
| **Fallback** | Graph from JSON in memory, not Neo4j (swap before demo) |

### Phase 3 — Next 4 hours (1:00–5:00)

| | |
|--|--|
| **Goal** | **Full loop working in ugly UI** |
| **Frontend** | Force graph, method click panel, run button, result panel |
| **Backend** | `generate-and-run` combined endpoint, attach to graph |
| **Execution** | Template codegen + metric parse + graph write after run |
| **Ali** | Deploy URL exists (even staging); sponsor table draft |
| **Deliverable** | **Click method → run → graph updates** (the must-have) |
| **Fallback** | Drop papers 2/3 from graph; single-page app |

### Phase 4 — Final 2 hours (5:00–7:00)

| | |
|--|--|
| **Goal** | Polish demo path + deploy + rehearse |
| **Frontend** | Loading states, run log animation, highlight new nodes |
| **Backend** | Butterbase tables OR confirm Neo4j persistence |
| **Execution** | RocketRide `.pipe` stub or Cloud deploy |
| **Ali** | README, pitch rehearsal, judge Q&A |
| **Deliverable** | 2 flawless demo runs in a row |
| **Fallback** | Pre-run once; demo "re-run" on cached graph |

### Phase 5 — Final 60 minutes (7:00–8:00)

| | |
|--|--|
| **Goal** | Submit + buffer |
| **All** | Fix deploy, GitHub push, Butterbase MCP submit |
| **Ali** | Lead demo dry-run, assign who drives laptop |
| **Deliverable** | `deployed_project_url` works in incognito |
| **Fallback** | Record 60s backup video link in submission |

---

## 15. Team Task Board

### Ali — Product / Demo / Pitch

| Task | Prio | Est. | Done when | Fallback |
|------|------|------|-----------|----------|
| Lock seed topic + paper JSON review | P0 | 30m | Team agrees on `method_1` | 1 paper only |
| Write DEMO_SCRIPT.md | P0 | 45m | Word-for-word 90s script | Index cards |
| Sponsor mapping table in README | P0 | 30m | 4 sponsors each essential | Verbal only |
| Real vs simulated table | P0 | 20m | In README | Slide |
| Scope guard — cut features | P0 | ongoing | No new features after 5 PM | Ali says no |
| README final pass | P1 | 45m | GitHub reflects demo | Minimal README |
| Pitch + Q&A rehearsal | P0 | 60m | 2 clean runs | Ali solo pitch |
| Butterbase submission | P0 | 30m | MCP submit with app_id | Manual fields |
| Deploy URL verification | P0 | 15m | Incognito works | Teammate hotspot |

### Teammate 1 — Frontend / Graph UI

| Task | Prio | Est. | Done when | Fallback |
|------|------|------|-----------|----------|
| Vite + React scaffold | P0 | 45m | `npm run dev` works | Single HTML page |
| Home / paper list | P0 | 60m | 3 papers + Build Graph btn | Static list |
| Graph visualization | P0 | 2h | Nodes colored by type | Simple SVG |
| Method detail panel | P0 | 90m | Shows plan + Run btn | Modal |
| Run result panel | P0 | 90m | stdout, metric, status | Text area |
| Highlight new nodes after run | P1 | 45m | Run/Result glow | Toast only |
| Loading states for run | P0 | 30m | 4-step progress | Spinner |
| Deploy frontend | P0 | 45m | Public URL | Netlify drop |

### Teammate 2 — Backend / Neo4j / Butterbase

| Task | Prio | Est. | Done when | Fallback |
|------|------|------|-----------|----------|
| `data/papers.json` (3 papers) | P0 | 90m | Valid schema, 1 runnable method | 1 paper |
| FastAPI scaffold + CORS | P0 | 45m | Frontend can call API | — |
| Neo4j Aura setup | P0 | 45m | Connection works | — |
| `POST /build-graph` | P0 | 90m | Seed Cypher runs | In-memory graph |
| `GET /graph` | P0 | 60m | Returns nodes/edges JSON | — |
| `attach-to-graph` after run | P0 | 90m | New nodes in Neo4j | Mock delta JSON |
| Butterbase `init_app` + schema | P1 | 2h | papers + runs tables | Skip |
| Deploy API (Railway/Render/BB) | P0 | 60m | HTTPS endpoint | ngrok for demo |

### Teammate 3 — Execution / Daytona / RocketRide

| Task | Prio | Est. | Done when | Fallback |
|------|------|------|-----------|----------|
| `method_1.py` template (toy k-NN anomaly) | P0 | 2h | Prints F1 ~0.8 on synthetic data | Hardcode stdout |
| `runExperiment()` abstraction | P0 | 60m | Daytona + local fallback | Local only |
| `codegen.py` template fill | P0 | 60m | Returns CodeArtifact | Static file |
| `POST /methods/:id/run` | P0 | 90m | Full run result JSON | — |
| Metric parser | P0 | 30m | Extracts F1 from stdout | Manual in result |
| `generate-and-run` combined | P0 | 60m | One-click backend | Two-step OK |
| RocketRide `.pipe` stub | P2 | 2h | File + diagram in README | FastAPI only |
| Test 3 consecutive runs | P0 | 45m | All succeed | Pre-record video |

---

## 16. Risk Register

| Risk | Likelihood | Impact | Mitigation | Fallback |
|------|------------|--------|------------|----------|
| PDF extraction too slow | High if attempted | High | **Don't parse PDFs** — JSON seed | N/A |
| Daytona slow/fails | Medium | Critical | Pre-warm sandbox; 30s timeout; test morning | `runExperiment` local + label |
| Graph viz too complex | Medium | Medium | `react-force-graph-2d` with 15 nodes max | Table + Mermaid |
| Neo4j write issues | Medium | High | `scripts/seed_neo4j.py` tested early | Return static graph_delta JSON |
| Codegen unreliable | High with LLM | High | **Template only** for demo | Pre-baked `.py` file |
| Demo hard to explain | Low if rehearsed | High | Ali script; one method only | Shorter 60s version |
| Sponsors feel forced | Medium | Medium | Each sponsor in one demo beat | Honest "stub" docs |
| Submission rushed | Medium | Medium | Submit by 7:30 PM | Ali owns checklist |
| CORS / deploy broken | Medium | Critical | Deploy by hour 4 | ngrok |
| Team parallel merge conflicts | Medium | Medium | Frontend/API contract frozen hour 1 | Single branch |

---

## 17. Real vs Simulated Plan

| Component | Real / Simulated | Demo explanation |
|-----------|------------------|------------------|
| Paper content (claims, methods) | **Preloaded JSON** | "Extraction is pre-done for reliability; pipeline supports PDF ingest next." |
| Knowledge graph structure | **Real Neo4j** | "Papers, claims, methods live in Neo4j — queryable, not a mock diagram." |
| Code generation | **Real template** (+ optional LLM) | "We generate a runnable Python module from the method plan." |
| Sandbox execution | **Real Daytona** | "Code runs in an isolated Daytona sandbox — not on our laptop." |
| stdout / stderr / runtime | **Real captured** | "These are actual execution logs." |
| Metric (F1) | **Real from code output** | "Parsed from experiment stdout." |
| Graph update after run | **Real Neo4j write** | "ExperimentRun and Result nodes created by API after run." |
| SUPPORTS_OR_WEAKENS edge | **Rule-based** | "We link result to claim; full validation is future work." |
| PDF upload button | **Simulated / disabled** | "Upload UI is placeholder; demo uses curated papers." |
| RocketRide orchestration | **Real or documented stub** | "Pipeline orchestrates steps; FastAPI mirrors same flow for hackathon speed." |
| Butterbase persistence | **Real if deployed** | "Run history stored in Butterbase; fallback JSON during dev." |
| Multi-paper comparison | **Simulated richness** | "Three papers seed citations; we run one method." |

**Golden rule:** Sandbox run + graph update must be **real**.

---

## 18. README Outline

Ali owns final README. Structure:

```markdown
# Paper-to-Results Graph

## Problem
Researchers read claims but rarely record what was actually executed.

## Solution
Paper → Method → Code → Sandbox Run → Result → Graph Update

## Demo
[90-second flow + screenshot/GIF]

## Architecture
[Diagram from Section 5]

## Sponsor Mapping
| Sponsor | How we use it |
| Neo4j | ... |
| Daytona | ... |
| Butterbase | ... |
| RocketRide | ... |

## What Is Real vs Simulated
[Table from Section 17]

## Quick Start
### Prerequisites
### Run API
### Run Frontend
### Run Daytona smoke test

## What We Built During the Hackathon
- [ ] bullet list of actual shipped features

## Team
## Future Work
- PDF ingestion
- LLM codegen with validation
- Multi-method benchmarks
- Claim validation scoring

## License
```

---

## 19. Judge Q&A

**Q: What does it do?**  
A: You pick a method from a research paper, we generate runnable code, execute it in a sandbox, and save the result back into a knowledge graph — so you see what ran, not just what was claimed.

**Q: How is this different from a research chatbot?**  
A: Chatbots summarize text. We produce **executable artifacts** and **record experiment outcomes** as graph nodes. The output is evidence, not prose.

**Q: Where is Neo4j used?**  
A: Neo4j stores papers, claims, methods, datasets, and after a run — CodeArtifact, ExperimentRun, and Result nodes with SUPPORTS_OR_WEAKENS edges to claims.

**Q: Where is Daytona used?**  
A: Generated Python runs inside a Daytona sandbox. We capture stdout, stderr, and runtime from real isolated execution.

**Q: Where is Butterbase used?**  
A: Butterbase hosts our demo app and stores paper metadata, run history, and artifacts — plus official hackathon submission.

**Q: Where is RocketRide used?**  
A: RocketRide orchestrates the pipeline: load method → generate code → execute → update graph. Each step is an observable agent wave.

**Q: What is real vs simulated?**  
A: Real: graph, sandbox run, logs, metric, graph update. Preloaded: paper extraction (JSON seed). Optional: LLM codegen.

**Q: What did you build during the hackathon?**  
A: A closed loop from method selection to sandbox execution to Neo4j graph update, with a 4-screen demo UI and deployed URL.

**Q: What would you build next?**  
A: PDF ingestion, multi-run comparison on the same claim, automated claim support/weaken scoring, and RocketRide Cloud production deploy.

**Q: Why should this win?**  
A: It's a **thoughtful agent** with a clear job at each step, uses the sponsor stack meaningfully, and proves understanding with **code execution** — not another literature chatbot.

---

## 20. Final Decision Check

### Is this build scope realistic?

**Yes, for a team of 4 in 8 hours — if you follow these rules:**

1. One runnable method (`method_1` on `paper_1`)
2. Template codegen, not LLM-first
3. JSON seed, not PDF parsing
4. Four screens, one happy path
5. Neo4j + Daytona are real; Butterbase/RocketRide can be thin

**No, if you add:** upload parsing, chat, multi-method runs, or LLM-only codegen.

### What to cut first if time is short

| Cut order | What |
|-----------|------|
| 1 | PDF upload UI |
| 2 | LLM codegen |
| 3 | Papers 2 & 3 (keep 1 paper) |
| 4 | RocketRide Cloud deploy (keep `.pipe` doc) |
| 5 | Butterbase DB (keep deploy URL only) |
| 6 | Fancy graph physics / animations |
| **Never cut** | Run loop + graph update |

### The one feature that must work

> **Click method → Generate + Run → capture stdout/metric → ExperimentRun + Result nodes appear in graph.**

If this works once, you have a demo. Everything else is presentation.

### Shortest path to a winning demo

```
Hour 0–1:   papers.json + method_1.py runs in Daytona (Teammate 3)
Hour 1–3:   POST /run + Neo4j seed (Teammate 2)
Hour 3–5:   UI: button → call /run → show logs (Teammate 1)
Hour 5–6:   Graph shows new nodes after run (Teammate 1 + 2)
Hour 6–8:   Deploy + Ali rehearsal + submit
```

**Parallel critical path:** Teammate 3 must deliver working `method_1.py` in Daytona by **hour 2**. Frontend can mock until hour 4.

---

## Appendix A — Recommended Demo Topic

**Topic:** Graph-Based Anomaly Detection for Sensor Streams

**Why:**
- Matches graph sponsor story (k-NN graph inside the algorithm)
- Runnable in ~40 lines Python with numpy/sklearn
- Clear metric (F1 score)
- Three papers can cite each other naturally

**Demo method:** Local Neighborhood Anomaly Score — k-NN graph on synthetic sensor readings, flag outliers, print F1.

---

## Appendix B — API Contract (Freeze at Hour 1)

Frontend and backend agree on these shapes before parallel work:

```typescript
// POST /api/methods/method_1/generate-and-run
type GenerateAndRunResponse = {
  artifact: { id: string; filename: string; content: string };
  run: { id: string; status: string; stdout: string; stderr: string; runtime_seconds: number };
  result: { metric_name: string; metric_value: number; summary: string };
  graph_delta: { nodes: GraphNode[]; edges: GraphEdge[] };
};
```

---

## Appendix C — First Team Sync Checklist (15 min)

- [ ] Repo cloned, `.env` filled (Daytona + Neo4j)
- [ ] Demo topic locked: sensor anomaly detection
- [ ] `method_1` is the only runnable method
- [ ] API contract frozen (Appendix B)
- [ ] Ali is scope enforcer — no features after 5 PM without trade-off
- [ ] Who presents? Who drives laptop?
- [ ] Deploy target chosen (Butterbase frontend + Render/Railway API)

---

*End of execution plan. Do not start feature work until team completes Appendix C.*
