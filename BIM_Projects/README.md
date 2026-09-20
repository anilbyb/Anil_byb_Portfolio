# BIM and Computational Modelling Projects

Selected workflows connecting drawing data, computational geometry and Revit modelling. This index describes the material currently present in the repository and provides direct entry points into each collection.

## 1. Architectural wall modelling from drawing data

[Open the workflow](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/)

The project README describes a staged process: extract wall data in Rhino/Grasshopper, derive heights from structural references, create walls through the Revit API, and process wall/beam intersections with Dynamo.

Included material:

- [Rhino input model](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step1-Walls-0100-R1.3dm)
- Grasshopper definitions for [curve extraction](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step1a-GH_Wall_GetData-1.gh), [type matching](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step1b-GH_Wall-findtype.gh), [type organisation](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step1c-GH_Wall-organizetypes.gh) and [height data](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step2-GH_Wall-getheights.gh)
- [Step1_WallData.xlsx](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step1_WallData.xlsx) and [Step2_WallData.xlsx](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step2_WallData.xlsx)
- [Revit wall creation script](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step3-RVT-PythonShell-ModelWalls.py)
- [Dynamo wall/beam graph](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step4-CutBeamsFromWalls.dyn) and [clash dataset](Automated_Architectural_RevitModeling/Model_Walls_From_DWG/Step4-Wall_Beam_Clashes.csv)

**Scope:** The Python script reads CSV rows and uses named wall types and levels to create Revit walls. Structural FBX references and a complete Revit model/template are not included.

## 2. MEP modelling and coordination workflows

[Open the collection](Automated_MEP_Coordination/)

The project README describes underground infrastructure and hospital workflows. The repository includes data-extraction definitions, CSV datasets and scripts for Revit element creation and positioning.

Code entry points:

- [Fire pipe creation](Automated_MEP_Coordination/Codes/01-CreateFirePipes-v2.py)
- [Ventilation duct creation](Automated_MEP_Coordination/Codes/02-CreateVentDucts-v3.py)
- [Domestic water pipe creation](Automated_MEP_Coordination/Codes/04-CreateDOWPipes.py)
- [Pipe positioning relative to ceilings](Automated_MEP_Coordination/Codes/_PutAboveCeiling-Pipes.py)
- [Grasshopper definitions and datasets](Automated_MEP_Coordination/Codes/)
- [Project images](Automated_MEP_Coordination/Images/)



## 3. Parametric facade modelling

[Open the collection](Facade_Parametric_Modeling/)

The project README describes two workflows: detailing panels for a twisted tower facade, and generating facade data for a curved-floorplan Revit workflow.

Included definitions:

- [P1_PanelsModeler-v4.gh](Facade_Parametric_Modeling/Codes/P1_PanelsModeler-v4.gh)
- [P2-create-EXCEL-data-T1.gh](Facade_Parametric_Modeling/Codes/P2-create-EXCEL-data-T1.gh)
- [P2_Create_Face_Families.dyn](Facade_Parametric_Modeling/Codes/P2_Create_Face_Families.dyn)
- [Images and workflow screenshots](Facade_Parametric_Modeling/Images/)
- [External Rhino model reference](Facade_Parametric_Modeling/Models/README.md)

**Scope:** The `Models` directory contains a README linking to external Rhino files, rather than the model files themselves.

## Using these examples

These are project-specific workflow materials. Before adapting them, review the
input formats, file paths, Revit types and parameters they expect. Some MEP
scripts include deletion steps as part of rebuilding elements; read the execution
section and work on a copy of the model.


[Back to the portfolio](../README.md) · [Website](https://anilis.me/) · [LinkedIn](https://www.linkedin.com/in/anilbayburt)
