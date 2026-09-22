---
name: controlled-progress-verification-git
description: "Use when working on the L.E.A.D. project and a task needs small logical increments, explicit verification, technical traceability, checkpoint reports, reproducible artifacts, or Git-ready progress without automatic commits."
argument-hint: "Describe the L.E.A.D. task and the immediate checkpoint to implement."
user-invocable: true
disable-model-invocation: false
---

# Controlled Progress, Verification & Git Workflow

## Purpose

Apply a controlled, traceable workflow to L.E.A.D. work. This is a workspace-scoped skill and its rules apply consistently across the project. Break large tasks into small, independently reviewable increments. After each meaningful increment, report the result and stop for human confirmation before starting the next block.

## When to Use

Use this skill for changes involving L.E.A.D. code, data, notebooks, models, tests, outputs, documentation, configuration, or pipelines, especially when the work affects methodology, generated artifacts, or repository state.

## Core Cycle

For each checkpoint:

1. Analyze the immediate request and identify the owning files, dependencies, inputs, outputs, and behavior to preserve.
2. Plan one small, concrete change.
3. Implement only that change. Do not combine unrelated refactoring, methodology, interface, model, cleanup, or documentation work.
4. Verify it with the cheapest meaningful executable or structural check available.
5. Update the existing traceability Markdown in `data/outputs/` or the relevant documentation when the project change is significant. Keep one cumulative log; do not create redundant tracking files.
6. Review Git status when relevant, including modified, new, deleted, and relevant ignored files.
7. Report the checkpoint using the format below.
8. Propose one Conventional Commit message for exactly that checkpoint.
9. Stop and wait for confirmation before continuing.

Never report success based only on having written code. If verification was impossible, say so explicitly.

## Before Editing

Identify:

- files involved and nearby existing implementations;
- dependencies and current behavior to preserve;
- input and output files;
- whether the change affects methodology or business assumptions.

Label decisions explicitly:

- `[REQUIERE DECISIÓN METODOLÓGICA]` for methodological alternatives that need approval;
- `[REQUIERE VALIDACIÓN CON EL NEGOCIO]` for business or domain validation;
- `[REFACTORIZACIÓN TÉCNICA]` for structure-only improvements;
- `[CAMBIO DE COMPORTAMIENTO DETECTADO]` when behavior changes.

Do not improve unrelated code opportunistically. If an additional task appears, record it as pending and keep it outside the current checkpoint.

## Verification

Prefer checks that directly exercise the changed behavior, in this order when practical:

- execute the affected code or pipeline;
- run focused tests;
- validate imports, routes, and paths;
- inspect generated files and their existence;
- verify record counts, columns, sizes, expected values, and comparisons with prior behavior.

For notebooks, preserve valid JSON structure and required cell metadata. Refer to notebook cells by their visible number in reports, never by cell IDs.

## Checkpoint Report

Use exactly this structure, replacing placeholders with concrete details:

```markdown
## Checkpoint N — [nombre del avance]

### Objetivo
[Qué se buscaba realizar]

### Archivos modificados
- [ruta o "Ninguno"]

### Archivos creados
- [ruta o "Ninguno"]

### Archivos eliminados
- [ruta o "Ninguno"]

### Código implementado
[Funciones, clases, módulos, parámetros, dependencias y lógica principal, según corresponda]

### Artefactos generados
Producto:
Ruta:
Tipo:
Descripción:
Origen:
Método utilizado:
Validación:

### Verificación realizada
[Comandos, tests, conteos, columnas, archivos y resultados concretos]

### Cambios de comportamiento
[Sin cambios de comportamiento | descripción exacta]

### Decisiones pendientes
[Ninguna | decisión etiquetada con una de las marcas requeridas]

### Estado
[COMPLETADO Y VERIFICADO | COMPLETADO CON OBSERVACIONES | PENDIENTE DE VALIDACIÓN | BLOQUEADO]

### Conventional Commit propuesto
`<type>(<scope>): <description>`
```

Use only these commit types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`, and `ci`. Never commit automatically.

## Traceability Log

When the checkpoint changes the project materially, locate and append an entry to the existing Markdown traceability file in `data/outputs/` or the documentation location already used by the project. Keep the log generic and cumulative across checkpoints. Do not assume that a product-specific output such as `productos_AX.md` is the traceability log unless the project has explicitly designated it as such. Do not create redundant tracking files. Use this structure:

```markdown
## Checkpoint N — [nombre]

**Fecha:** YYYY-MM-DD

### Objetivo
...

### Cambios realizados
...

### Archivos modificados
- `ruta/archivo.py`

### Archivos creados
- `ruta/archivo.csv`

### Código / implementación
...

### Resultados
...

### Verificación
...

### Decisiones pendientes
...

### Estado
COMPLETADO Y VERIFICADO
```

Register every concrete product, result, model, report, notebook, configuration, log, or generated dataset with its route, purpose, origin, method, and validation. Keep private data, credentials, and datasets that should remain outside version control ignored and out of commits.

## Methodology and Scope Boundaries

Keep technical implementation separate from methodological decisions. When a possible methodological improvement is discovered, document the problem and alternative, mark it `[REQUIERE DECISIÓN METODOLÓGICA]`, and do not implement it automatically. This applies especially to product selection, Pareto, ABC-XYZ, demand definitions, stockouts, imputation, forecasting, temporal validation, metrics, prediction intervals, and safety stock.

Do not mix checkpoints. A checkpoint may cover one tightly related increment, such as one module, function refactor, route correction, output generation, test addition, configuration change, documentation update, or pipeline validation.

## Completion Rule

A checkpoint is complete only after the change, verification, traceability update when needed, Git review, report, and commit proposal are finished. Then stop. The next module, file, model, cleanup, or stage requires a new checkpoint and human confirmation.
