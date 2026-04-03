# Components, Assemblies, Tooling, and Deliverables

## Component

A component is the lowest tracked part.

Two important categories exist:

- `custom component`
- `off-the-shelf component`

An off-the-shelf component is still treated as one digital component even if
the vendor item contains multiple internal physical parts.

## Assembly

An assembly is any object made from components and/or lower-level assemblies.

The top assembly follows the same behavioral rules as any other assembly. The
only difference is that it has nothing above it.

## Tooling

Tooling describes the production resources available to the project, such as:

- in-house FDM printing
- laser cutting
- CNC machining
- outsourced fabrication
- factory production
- hand-built processes

Tooling is a project decision, not a hard-coded platform assumption.

## Manufacturing Technique

Manufacturing technique describes how the output is intended to be produced,
for example:

- shell printing
- rib-and-spar construction
- folded paper construction
- stitched fabric layout
- molded composite layup
- sheet-metal forming

## Deliverables

Deliverables are node- and project-specific artifacts. They are not globally
fixed across all AeroForge projects.

Examples:

- `DXF`, `PNG`, or three-view sheets
- `STEP`, `STL`, or `3MF`
- crease patterns and fold instructions
- stitching plans and cut patterns
- mold tooling data
- procurement shortlist records
- BOM updates
- validation reports
