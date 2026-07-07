# PrismGraph AI 3.0

**Turn research papers into an executable knowledge graph.**

PrismGraph AI 3.0 is a research-to-code platform built for [HackwithBay 3.0](https://lu.ma) — *Thoughtful Agents for Productivity*. It goes beyond literature exploration: trace claims across papers, generate runnable implementations from selected methods, execute them in isolated sandboxes, and attach outputs back to the knowledge graph.

> **2.0 was a graph of papers. 3.0 closes the loop: evidence → code → execution → validated graph.**

---

## The problem

Researchers spend hours reading papers in isolation. Summaries help, but they don't answer:

- Do these papers **agree or contradict** on a specific claim?
- Can I **run** the method from Paper B without manually reimplementing it?
- What happened when we tried to reproduce it — and where does that result live?

PrismGraph AI connects literature, code, and experiment results in one graph.

---

## How it works

```
Upload papers → Extract claims, methods, citations
                    ↓
              Knowledge graph (Neo4j)
                    ↓
         Ask cross-paper questions (cited answers)
                    ↓
      Select a method → Generate runnable code (Paper2Code)
                    ↓
         Execute in Daytona sandbox → Capture logs & metrics
                    ↓
    Link Run node back to graph (VALIDATES / REFUTES claims)
```

### Agent roles

| Agent | Job |
|-------|-----|
| **Extractor** | Parse PDFs → claims, methods, datasets, citations |
| **Linker** | Connect papers, tasks, supporting/contradicting claims |
| **Planner** | Choose which method to implement |
| **Coder** | Paper2Code-style generation → minimal runnable module |
| **Runner** | Execute in Daytona, capture stdout/stderr/artifacts |
| **Curator** | Write run results back to graph + backend |

---

## Stack (HackwithBay partners)

| Partner | Role |
|---------|------|
| [**RocketRide**](https://github.com/rocketride-org/rocketride-server) | Multi-wave agent pipeline — extract → generate → execute → graph update |
| [**Neo4j**](https://neo4j.com) | Knowledge graph — papers, claims, methods, runs, conflicts |
| [**Daytona**](https://www.daytona.io) | Sandboxed code execution for generated implementations |
| [**Butterbase**](https://butterbase.ai) | Backend — papers, runs, artifacts, deployed demo UI |

---

## Graph model

**Nodes:** `Paper`, `Author`, `Claim`, `Method`, `Dataset`, `Task`, `Run`, `Artifact`

**Key relationships:**

- `(Author)-[:WROTE]->(Paper)`
- `(Paper)-[:CITES]->(Paper)`
- `(Claim)-[:FROM]->(Paper)`
- `(Method)-[:DESCRIBED_IN]->(Paper)`
- `(Claim)-[:SUPPORTS|CONTRADICTS]->(Claim)`
- `(Run)-[:IMPLEMENTS]->(Method)`
- `(Run)-[:VALIDATES|REFUTES]->(Claim)`

---

## Demo flow (2 minutes)

1. Select 2–3 papers on the same topic (pre-loaded).
2. Ask: *"Do these papers agree on [metric/approach]?"* → graph shows cited claims and conflicts.
3. Click a paper → **Implement method** → RocketRide agent generates code.
4. Run in Daytona sandbox → live execution log.
5. New `Run` node appears on the graph with results linked to the source claim.

---

## Project status

🚧 **Hackathon build in progress** — HackwithBay 3.0, July 7, 2026.

| Component | Status |
|-----------|--------|
| Daytona sandbox (SDK) | ✅ Verified |
| RocketRide pipeline | 🔲 In progress |
| Neo4j graph | 🔲 In progress |
| Butterbase backend + UI | 🔲 In progress |
| Paper2Code generation loop | 🔲 In progress |

---

## Local setup

### Prerequisites

- Python 3.11+
- [Daytona](https://www.daytona.io) API key
- RocketRide VS Code extension (for pipeline development)
- Neo4j Aura or local instance
- Butterbase account + MCP in Cursor

### Daytona quick test

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your DAYTONA_API_KEY to .env
python main.py
```

Expected output:

```
Hello World from code!
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `DAYTONA_API_KEY` | Daytona API key for sandbox execution |
| `NEO4J_URI` | Neo4j connection URI |
| `NEO4J_USER` | Neo4j username |
| `NEO4J_PASSWORD` | Neo4j password |

---

## Repository structure

```
.
├── README.md           # This file
├── main.py             # Daytona sandbox verification
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template (copy to .env)
└── pipelines/          # RocketRide .pipe files (coming soon)
```

---

## Team

Built for **HackwithBay 3.0** — AWS Builder Loft, San Francisco.

**Theme:** Thoughtful Agents for Productivity

---

## License

MIT
