# MEP Modelling and Coordination Workflows

## Purpose and project context

This collection documents drawing-data extraction and project-specific Revit modelling and positioning logic.

The original project documentation describes two contexts:

- **Project 1: underground MEP coordination for a port development**, using drawing-derived system information and spatial constraints.
- **Project 2: hospital MEP modelling**, adapting drawing-data preparation and Revit automation to building services.

Images use `P1_` and `P2_` prefixes. Code files use system and task names instead. A definitive project-to-code mapping has not yet been documented, so the files below are organised by function.

## Technical examples

| File | Inputs visible in source | Intended output / current state |
| --- | --- | --- |
| [01-CreateFirePipes-v2.py](Codes/01-CreateFirePipes-v2.py) | `L05-Curves.csv`, `L05-Tags.csv`, `L05-risers.csv`; existing sprinklers; named Revit systems/types and custom parameters | Fire pipe creation and positioning routines. The execution section also invokes deletion and cleanup operations. The three named CSV inputs are not present in this repository. |
| [02-CreateVentDucts-v3.py](Codes/02-CreateVentDucts-v3.py) | CSV files including `CUR-RECTS.csv`, `CUR-ROUNDS.csv` and `CUR-DOWNRECTS.csv`; model types, parameters and ceiling references | Contains duct creation, fitting, insulation and height routines. **In the committed execution section, creation and adjustment calls are commented out while a deletion call is active. It is not an end-to-end duct creation run as saved.** |
| [04-CreateDOWPipes.py](Codes/04-CreateDOWPipes.py) | `L06-DOWCurves.csv`; selected level/zone configuration; pipe types, system names, custom parameters and linked ceilings | Domestic water pipe creation, insulation and elevation updates. The execution section first deletes existing pipes/fittings selected by its level logic. |
| [_PutAboveCeiling-Pipes.py](Codes/_PutAboveCeiling-Pipes.py) | Selected model elements, linked ceilings and custom height parameters | Adjusts selected pipe elevations using ceiling-related information; requires appropriate pipe selection and model setup. |

See [Codes](Codes/README.md) for data and definition entry points, and [Images](Images/) for the supplied visual material.

## Environment

- Rhino and Grasshopper for the supplied `.gh` definitions.
- AutoCAD for the supplied AutoLISP helper.
- Revit with a Python host exposing `__revit__` for the Python scripts.
- Project-specific Revit element types, system names, parameters and linked models.

Exact working software versions and Python-host configuration are not established by the reviewed source. Earlier version labels are not presented here as verified requirements.

## Known limitations

The source includes hard-coded paths, level/zone choices and parameter names. Some routines operate on model-wide collections or level-based selections; their scope must be inspected before use. Several scripts also rely on API names or host-provided imports that are not fully self-contained.

The repository does not establish a complete automatic routing solver, full clash resolution or regulatory compliance. No measured time savings or success rates are asserted. The supplied scripts and definitions were not run in their host applications during this review; evaluate them only after reviewing dependencies and execution sections, using a copy of the model.

[Back to BIM projects](../README.md) · [Main portfolio](../../README.md) · [LinkedIn](https://www.linkedin.com/in/anilbayburt)
