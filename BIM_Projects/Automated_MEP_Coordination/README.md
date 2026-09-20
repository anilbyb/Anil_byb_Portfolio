# MEP Modelling and Coordination Workflows

## Problem

**Project 1, port development.** Every underground MEP system on a 1,500,000 m²
port site had to fit inside a [N] m vertical corridor set by soil and elevation
conditions. [N] disciplines arrived as 2D AutoCAD layouts and had to be
coordinated into one clash-free model across 17 buildings.

**Project 2, hospital complex.** The same problem turned vertical: ventilation,
grey and fresh water, sprinklers, electrical trays, smoke extraction and medical
gases had to be routed through tight shafts while holding each system's
coordination rules.

## Approach

- Grasshopper reads locations, systems, diameters and materials from the drawing
  layouts and builds 3D constraint volumes defining where each system may run.
- Pipes, ducts and trays are repositioned automatically to avoid clashes;
  manholes and transitions follow each discipline's rules.
- Each system is written out as a structured CSV file, which acts as the contract
  between the geometry environment and the BIM environment.
- Python scripts inside Revit read those files and create every element with its
  system, type and material data.

The framework was built for the port project and reused on the hospital and
several other MEP-heavy projects.

## What is in this folder

## Technical examples

| File | Inputs visible in source | Intended output / current state |
| --- | --- | --- |
| [01-CreateFirePipes-v2.py](Codes/01-CreateFirePipes-v2.py) | `L05-Curves.csv`, `L05-Tags.csv`, `L05-risers.csv`; existing sprinklers; named Revit systems/types and custom parameters | Fire pipe creation and positioning routines. The execution section also invokes deletion and cleanup operations. "Reads exported curve, tag and riser data; sample CSV files are not published.". |
| [02-CreateVentDucts-v3.py](Codes/02-CreateVentDucts-v3.py) | CSV files including `CUR-RECTS.csv`, `CUR-ROUNDS.csv` and `CUR-DOWNRECTS.csv`; model types, parameters and ceiling references | Contains duct creation, fitting, insulation and height routines."Creates rectangular and round ducts from CSV geometry, then adds insulation and adjusts heights against linked ceilings." |
| [04-CreateDOWPipes.py](Codes/04-CreateDOWPipes.py) | `L06-DOWCurves.csv`; selected level/zone configuration; pipe types, system names, custom parameters and linked ceilings | Domestic water pipe creation, insulation and elevation updates. "Rebuilds domestic water pipes for a selected level: existing runs are cleared first, then created with insulation and elevation data." |
| [_PutAboveCeiling-Pipes.py](Codes/_PutAboveCeiling-Pipes.py) | Selected model elements, linked ceilings and custom height parameters | Adjusts selected pipe elevations using ceiling-related information; requires appropriate pipe selection and model setup. |

See [Codes](Codes/README.md) for data and definition entry points, and [Images](Images/) for the supplied visual material.

## Environment

- Rhino and Grasshopper for the supplied `.gh` definitions.
- AutoCAD for the supplied AutoLISP helper.
- Revit with a Python host exposing `__revit__` for the Python scripts.
- Project-specific Revit element types, system names, parameters and linked models.

## Limitations

The scripts expect project-specific Revit types, system names, parameters and
linked models, and they operate on level- or zone-based selections. Read the
execution section of each script before running it, and work on a copy.

[Back to BIM projects](../README.md) · [Main portfolio](../../README.md) · [LinkedIn](https://www.linkedin.com/in/anilbayburt)
