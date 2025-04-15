# 🧱 Revit Wall Automation Workflow

This folder documents a multi-stage workflow designed to automate the creation of architectural walls in Revit using raw DWG drawings, structural FBX references, and scripting via Grasshopper, PythonShell, and Dynamo.

Each step produces structured outputs that are used in the next phase of the pipeline. The goal is to reduce manual wall modeling and achieve higher coordination accuracy between architectural and structural models.

---

## 📐 Step 1: Get Wall Data from DWG

**Input:**  
- `Step1-Walls-0100-R1.3dm`: Rhino model with architectural wall curves and embedded material data from DWG

**Tools:**  
- `Step1a-GH_Wall_GetData-1.gh`: Extracts raw wall curves  
- `Step1b-GH_Wall-findtype.gh`: Matches curves to wall type names  
- `Step1c-GH_Wall-organizetypes.gh`: Organizes and structures wall type data  

**Output:**  
- `Step01_WallData.xlsx`  
  _(Format: LEVEL, ZONE, TYPE, OPTIONAL, START X, START Y, END X, END Y)_

---

## 🏗️ Step 2: Get Wall Heights from Structural Model

**Input:**  
- `Step01_WallData.xlsx`: From Step 1  
- `FBX Structural Models` (not included due to restrictions)

**Tools:**  
- `Step2-GH_Wall-getheights.gh`: Samples height geometry from structural FBX and enriches wall data

**Output:**  
- `Step02_WallData.xlsx`: Includes additional height information

---

## 🧰 Step 3: Model Walls in Revit

**Input:**  
- `Step02_WallData.xlsx` (exported as `.csv` per zone)

**Tools:**  
- `Step3-RVT-PythonShell-ModelWalls.py`: Creates Revit wall elements based on type, coordinates, and height

**Output:**  
- Walls are placed in the Revit model at correct locations with defined wall types

---

## 🪚 Step 4: Subtract Beams from Walls

**Input:**  
- Revit architectural wall model  
- Revit structural model  
- `Step4-Wall_Beam_Clashes.csv`: Clash data between beams and walls (exported from clash check software)

**Tools:**  
- `Step4-CutBeamsFromWalls.dyn`: Uses clash data to subtract intersecting beams from walls in Dynamo

**Output:**  
- Coordinated and cleaned architectural model with beams properly cut from walls

---

## 📌 Notes

- This workflow was developed to handle a large number of DWG-based wall layouts with minimal manual input.
- The structural FBX files are excluded due to project confidentiality.
- Grasshopper files are written to handle naming inconsistencies and DWG data irregularities.
- Python and Dynamo scripts require Revit custom parameters to be pre-defined in the template.

---

👤 Author: Anıl Bayburtluoğlu  
Visit the [main portfolio](../README.md) for more workflows and automation scripts.

