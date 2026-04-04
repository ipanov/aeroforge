# AeroForge Wiki

**AI-autonomous design framework for heavier-than-air aircraft.**

AeroForge runs inside any LLM agent (Claude Code, Codex, etc.) as an autonomous design assistant. The LLM drives the workflow; a deterministic engine enforces quality gates, step sequencing, and validation. The user gives design direction in natural language -- the system handles everything else.

Not limited to one aircraft class, manufacturing method, or deliverable type. Paper airplane to interceptor drone -- same framework, different providers.

---

## Architecture

```mermaid
flowchart TD
    subgraph UserLayer["User Layer"]
        U["👤 User\nnatural language"]
    end

    subgraph LLMLayer["LLM Agent Layer"]
        L["🤖 LLM Agent\nClaude Code / Codex"]
        SK["/aeroforge skill"]
        INIT["/aeroforge-init skill"]
    end

    subgraph Engine["Deterministic Engine"]
        WE["WorkflowEngine\nstate machine"]
        SM["StateManager\nhierarchical tree"]
        PM["ProjectManager\nmulti-project"]
    end

    subgraph Providers["Provider System"]
        CFD["CFD\nSU2 CUDA / CPU"]
        FEA["FEA\nFreeCAD + CalculiX"]
        AIR["Airfoil\nNeuralFoil"]
        MFG["Manufacturing\nFDM / Manual / CNC"]
        SLC["Slicer\nOrcaSlicer"]
    end

    subgraph Agents["Design Agents"]
        AE["🔵 Aerodynamicist"]
        SE["🟠 Structural Engineer"]
        WT["🟢 Wind-Tunnel Engineer"]
        SA["🟠 Structures Analyst"]
    end

    subgraph Quality["Quality Enforcement"]
        HK["13 Deterministic Hooks"]
        RAG["RAG Knowledge Base\nChromaDB"]
        N8N["n8n Monitoring"]
    end

    U --> L
    L --> SK
    L --> INIT
    SK --> WE
    WE --> SM
    WE --> PM
    WE --> AE
    WE --> SE
    WE --> WT
    WE --> SA
    WE --> CFD
    WE --> FEA
    WE --> AIR
    WE --> MFG
    WE --> SLC
    HK --> WE
    RAG --> AE
    RAG --> SE
    N8N --> WE

    style UserLayer fill:#2d6a4f,color:#fff
    style LLMLayer fill:#1b4332,color:#fff
    style Engine fill:#264653,color:#fff
    style Providers fill:#2a6f97,color:#fff
    style Agents fill:#6a4c93,color:#fff
    style Quality fill:#9d4edd,color:#fff
    style U fill:#40916c,color:#fff
    style L fill:#2d6a4f,color:#fff
    style SK fill:#2d6a4f,color:#fff
    style INIT fill:#2d6a4f,color:#fff
    style WE fill:#1d3557,color:#fff
    style SM fill:#1d3557,color:#fff
    style PM fill:#1d3557,color:#fff
    style CFD fill:#457b9d,color:#fff
    style FEA fill:#457b9d,color:#fff
    style AIR fill:#457b9d,color:#fff
    style MFG fill:#457b9d,color:#fff
    style SLC fill:#457b9d,color:#fff
    style AE fill:#4a90d9,color:#fff
    style SE fill:#e76f51,color:#fff
    style WT fill:#2a9d8f,color:#fff
    style SA fill:#e76f51,color:#fff
    style HK fill:#7b2cbf,color:#fff
    style RAG fill:#7b2cbf,color:#fff
    style N8N fill:#7b2cbf,color:#fff
```

---

## Quick Start

```
/aeroforge-init    Initialize a new project (interactive conversation)
/aeroforge         Drive the active project's design workflow
```

The LLM reads project state, spawns design agents, updates workflow steps, and shows you deliverables for approval. You give design direction in natural language. You never type commands or run scripts.

---

## Pages

| Page | Description |
|------|-------------|
| [AeroForge Overview](AeroForge-Overview) | System philosophy, what AeroForge is and is not |
| [Hierarchical Workflow](Hierarchical-Workflow) | Project phases, per-node design cycle, iteration model |
| [Initialization and Project Profile](Initialization-and-Project-Profile) | How `/aeroforge-init` works, project structure |
| [Components and Assemblies](Components-and-Assemblies) | Node types, CAD folder structure, off-shelf rules |
| [Provider System](Provider-System) | System vs project providers, auto-detection, hardware profile |
| [Agents](Agents) | All 4 design agents, parameterization, when they run |
| [Hooks and Enforcement](Hooks-and-Enforcement) | 13 deterministic hooks, what they block, LLM boundary |
| [Living BOM and Procurement](Living-BOM-and-Procurement) | BOM sync, supplier strategy |
| [RAG Knowledge Base](RAG-Knowledge-Base) | ChromaDB vector store, population, querying |
| [Example Project: AIR4](Example-Project-AIR4) | The F5J thermal sailplane reference project |
| [Reference and Research Index](Reference-and-Research-Index) | Catalogs, benchmarks, research archive |
