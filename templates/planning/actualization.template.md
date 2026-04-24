# Actualization map

Feature: `features/<feature-slug>/feature.md`  
Quarter: `<YYYY-QN>`  
Baseline: `commander-plan`

## Правила
- `virtual` означает, что story ещё сама является текущей execution-единицей.
- `materialized` означает, что story полностью раскрыта в реальные implementation tasks.
- `mixed` означает, что часть story уже заменена real tasks, а остаток ещё виден как virtual residual.
- `Replaced By` заполняется явным указанием пользователя или выводом LLM по смыслу.
- `Residual Virtual Tasks` заполняется только для `mixed`.
- `Depends On` используем, если story без замещения должна в actual-progress стартовать после завершения другой story по логике commander-plan.

## Mapping

| Story ID | Summary | Baseline Start | Baseline Duration (дн) | Actualization State | Mapping Mode | Replaced By | Residual Virtual Tasks | Depends On |
|---|---|---|---:|---|---|---|---|---|
| STORY-XXX-001 | <summary> | <YYYY-MM-DD> | <N> | virtual | explicit |  |  |  |
