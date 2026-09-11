# Parametric Facade Modelling

## Purpose

Two project workflows explore facade geometry, panel detailing and Revit family placement. The original project descriptions identify a twisted tower facade and a curved-floorplan facade. The supplied code filenames distinguish these as `P1_` and `P2_`.

## Project 1: twisted tower panel detailing

The documented aim is to generate profiles, substructure and connection geometry for facade panels with varying geometry.

- **Input:** Base facade surfaces in Rhino; externally referenced model filenames are listed in [Models](Models/README.md).
- **Definition:** [P1_PanelsModeler-v4.gh](Codes/P1_PanelsModeler-v4.gh).
- **Intended output:** Rhino geometry for panel detailing.
- **Supporting material:** [Images](Images/) contains `P1_` images and a Grasshopper screenshot.

The definition has not been executed or fully inspected internally in this review. Fabrication readiness and geometric tolerances have not been independently verified.

## Project 2: curved-floorplan facade modelling

The original description associates this workflow with spline-based facade geometry and Revit delivery. Two implementation files are included:

| File | Evidence and intended role |
| --- | --- |
| [P2-create-EXCEL-data-T1.gh](Codes/P2-create-EXCEL-data-T1.gh) | Grasshopper definition identified by its filename as a data-preparation step. Its exact export schema and handoff to Revit remain undocumented. |
| [P2_Create_Face_Families.dyn](Codes/P2_Create_Face_Families.dyn) | The saved graph uses selected Revit element geometry, surface/curve processing, family types, `FamilyInstance.ByPoint`, parameter updates and rotation. Intended output is configured Revit family instances. |

The Dynamo graph sets parameters including `Start_X`, `Start_Y`, `End_X`, `End_Y`, `h1`, `h2`, `Sweep Radius` and `Width`. Required families and the complete Revit model are not included.

The reviewed graph does not contain the CSV import step described in the earlier README. It uses point-based family instance nodes; an adaptive-component placement workflow is not established by this file. The relationship between the Grasshopper export and selected Revit geometry needs clarification.

## Environment and limitations

- Rhino/Grasshopper are required for the `.gh` definitions.
- The Dynamo graph requires a Revit context and project-specific family types and geometry.
- The graph records Dynamo **2.13.1.3887**. This is saved metadata, not confirmation of a working Revit/Dynamo version combination.
- The [Models directory](Models/README.md) contains an external download reference, not local `.3dm` files. External availability has not been checked.
- No definition or graph was run in Rhino, Grasshopper, Revit or Dynamo during this review. Output quality, dependencies and compatibility remain unverified.

Project and client names are omitted here, as in the original documentation.

[Back to BIM projects](../README.md) · [Main portfolio](../../README.md) · [LinkedIn](https://www.linkedin.com/in/anilbayburt)
