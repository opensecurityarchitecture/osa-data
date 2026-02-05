# Vision: Graph-Based Security Architecture

A future direction for OSA - representing security architectures as graphs that can be dynamically generated, analysed, and annotated with controls.

## Core Concept

Security architecture as graph theory:

```
Nodes = Things you need to secure (assets, components, zones)
Edges = Transitive relationships (data flows, attack paths, trust boundaries)
Controls = Applied to nodes AND edges to manage threats
```

## Node Model

Nodes represent securable entities with metadata:

```json
{
  "id": "web-server-01",
  "type": "server",
  "classification": "confidential",
  "zone": "dmz",
  "metadata": {
    "os": "linux",
    "exposure": "internet-facing",
    "data_types": ["pii", "session_tokens"]
  },
  "controls": ["AC-01", "SC-07", "SI-04"]
}
```

Node types might include:
- Servers, clients, devices
- Data stores, databases
- Users, actors, roles
- Security zones, network segments
- External systems, APIs
- Data assets

## Edge Model

Edges represent relationships with security implications:

```json
{
  "from": "web-server-01",
  "to": "database-01",
  "type": "data_flow",
  "metadata": {
    "protocol": "tcp/5432",
    "encryption": "tls_1.3",
    "data_classification": "confidential",
    "direction": "bidirectional"
  },
  "threats": ["interception", "injection", "privilege_escalation"],
  "controls": ["SC-08", "SC-13", "AC-04"]
}
```

Edge types might include:
- Data flows (what data moves where)
- Attack paths (how threats propagate)
- Trust relationships (authentication/authorisation flows)
- Network connectivity (physical/logical)
- Dependencies (component relationships)

## Dynamic Pattern Generation

Given:
1. **System description** - nodes and edges
2. **Data classification** - what's being processed
3. **Threat context** - threat actors, attack vectors
4. **Compliance requirements** - which frameworks apply

Generate:
1. **Applicable controls** - from NIST 800-53 or other catalogues
2. **Visual pattern** - SVG diagram with OSA iconography
3. **Gap analysis** - missing controls for compliance
4. **Attack surface** - graph analysis of exposure

## Example Workflow

```
User: "I have a web application that processes credit card data,
       hosted on AWS, with a PostgreSQL database"

System:
1. Creates nodes: [web_app, database, users, aws_vpc, internet]
2. Creates edges: [user→web_app, web_app→database, internet→web_app]
3. Identifies: PCI-DSS scope, internet exposure, data classification
4. Applies: Relevant controls from catalogue
5. Generates: Pattern diagram with control annotations
6. Highlights: Gaps, risks, recommendations
```

## Technical Approach

### Data Format
- JSON or YAML for portability
- JSON Schema for validation
- Could align with STIX/TAXII for threat data interop

### Graph Storage Options
- **Simple**: JSON adjacency list (good for small architectures)
- **Scalable**: Neo4j or similar graph database
- **Embedded**: SQLite with graph extensions

### Visualisation
- Generate SVG dynamically from graph data
- Use OSA icon set for consistent visual language
- Support multiple layout algorithms (hierarchical, force-directed)
- Export to common formats (PNG, PDF, Visio?)

### API Design
```
POST /api/v1/architecture
  → Create/update an architecture graph

GET /api/v1/architecture/{id}/controls
  → Get applicable controls for an architecture

GET /api/v1/architecture/{id}/diagram
  → Generate visual pattern (SVG/PNG)

POST /api/v1/architecture/{id}/analyse
  → Run threat analysis, identify gaps

POST /api/v1/chat
  → Conversational interface for building architectures
```

## AI Integration

Embed AI into the site for conversational architecture modelling:

1. **Natural language input** - describe your system in plain English
2. **Iterative refinement** - AI asks clarifying questions
3. **Threat brainstorming** - "what threats should I consider for X?"
4. **Control recommendations** - "which controls address Y?"
5. **Compliance mapping** - "show me the ISO 27001 gaps"

Could use Claude API with function calling to:
- Build/modify the graph
- Query the control catalogue
- Generate diagrams
- Explain control requirements

## Icon Set Modernisation

For dynamic diagram generation, we need a modern icon set:

### Validation First
- Check analytics for old icon page traffic
- Survey community on demand
- Research competitor offerings (Lucidchart, Draw.io security shapes)

### If Valuable
- Modernise to clean SVG on consistent grid (24px/48px)
- Match OSA palette
- Categorise: actors, infrastructure, security controls, zones, data
- Offer as downloadable pack + API access
- Use in dynamic pattern generation

## Questions to Explore

1. **Schema design** - What's the minimum viable graph schema?
2. **Existing standards** - Can we align with NIST/MITRE formats?
3. **Complexity balance** - How detailed before it's unusable?
4. **Hosting** - API on old web servers, static site on Cloudflare?
5. **Monetisation** - Free core, paid features? Enterprise API?

## Next Steps

1. Sketch out minimal graph schema (nodes, edges, controls)
2. Build prototype with 2-3 simple architectures
3. Test dynamic SVG generation
4. Experiment with Claude API for conversational modelling
5. Validate icon set demand before investing

---

*Created: 2026-02-05*
*Status: Vision / Brainstorm*
*Phase: 3 (AI Integration)*
