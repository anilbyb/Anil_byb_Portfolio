# Revit Wall Automation Workflow

## Problem

Hundreds of DWG layouts with inconsistent layer and type naming had to become
coordinated architectural walls in Revit, aligned to a structural model that was
still changing. Manual modelling and manual beam cutting were not realistic at
this scale: the published stage 2 dataset alone holds 5,256 wall segments.

## Purpose

A staged workflow for converting drawing-derived wall information into Revit elements and supporting coordination with structural geometry. 

## Files and workflow

| Stage | Inputs | Implementation | Intended output |
| --- | --- | --- | --- |
| 1. Prepare wall data | Drawing-derived curves in [Step1-Walls-0100-R1.3dm](Step1-Walls-0100-R1.3dm) | [Curve extraction](Step1a-GH_Wall_GetData-1.gh), [type matching](Step1b-GH_Wall-findtype.gh), [type organisation](Step1c-GH_Wall-organizetypes.gh) | Structured wall data; [Step1_WallData.xlsx](Step1_WallData.xlsx) is included |
| 2. Derive heights | Wall data and structural FBX references described in the original workflow | [Step2-GH_Wall-getheights.gh](Step2-GH_Wall-getheights.gh) | Height-enriched data; [Step2_WallData.xlsx](Step2_WallData.xlsx) is included |
| 3. Create Revit walls | CSV export, matching Revit wall types and levels | [Step3-RVT-PythonShell-ModelWalls.py](Step3-RVT-PythonShell-ModelWalls.py) | Wall elements created through the Revit API |
| 4. Process wall/beam intersections | Clash information, model elements and a void family | [Step4-CutBeamsFromWalls.dyn](Step4-CutBeamsFromWalls.dyn) | Placement and configuration of void families that performed the wall cuts |



## Python input and environment

The wall script accesses the active Revit document through `__revit__`, consistent with the PythonShell workflow described for this project. It is not a standalone Python application.

After skipping the header, it expects ten CSV columns in this order:

`floor, zone, type, optional, start_x, start_y, end_x, end_y, height, offset`

It resolves wall types and levels by name, converts coordinate/height/offset values using a millimetres-to-feet divisor of 304.8, and calls `Wall.Create` inside a transaction.

## Dynamo input and environment

The saved graph records Dynamo **2.13.1.3887** and references:

- Clockwork for Dynamo 2.x **2.6.0**
- Synthesize toolkit **24.4.1203**
- get documents **2021.0.0**



The graph uses an Excel import node for `beam-clashes-zone2-v2.xlsx`, sheet `Sheet1`, and a selected `Void_Family:Void_Family` type. Neither that workbook nor the family file is included. Clash data was prepared in Excel before use by the Dynamo graph. The supplied [Step4-Wall_Beam_Clashes.csv](Step4-Wall_Beam_Clashes.csv) is a clash dataset; the exact transformation into the graph's expected workbook is not included. The placed void family performed the cutting operation.

## Known limitations

- Structural FBX references, the complete Revit model/template and the zone CSV referenced by the Python script are not included.
- Local paths, wall-type naming rules and model element references require project-specific setup.
- The Python script does not guard against every missing wall type or level.
- The input workbook preparation and required void family are not included, so the complete cutting workflow cannot be reproduced from the supplied files alone.


[Back to architectural workflows](../README.md) · [BIM index](../../README.md) · [Main portfolio](../../../README.md)
