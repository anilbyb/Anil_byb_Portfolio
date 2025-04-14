# 🔧 Automated MEP Coordination

This folder contains two projects focused on automating the coordination and modeling of MEP (Mechanical, Electrical, and Plumbing) systems using **Grasshopper**, **Rhino**, **Python**, and **Revit**. Both workflows begin with 2D AutoCAD layouts and transform them into fully-coordinated, rule-compliant 3D MEP models, significantly reducing manual modeling time and clash risk.

Each project includes:
- Grasshopper definitions for extracting and coordinating MEP elements
- CSV outputs for systemized element data
- Python scripts for creating MEP elements directly in Revit

📂 _Project-related files are prefixed with `P1_` and `P2_` accordingly._

---

## ⚓ Project 1 – Large Port Area Underground MEP Coordination

**📌 Problem:**  
A massive 1,500,000 m² port area infrastructure project involving **11 MEP disciplines** and **17 buildings** required all underground MEP systems to fit within a constrained **7-meter vertical corridor**, due to challenging soil and elevation conditions.

**⚙️ Solution**  
To address this, I developed a **Grasshopper definition** that:
- Reads MEP layouts from AutoCAD (locations, systems, diameters, materials)
- Defines spatial constraints using 3D volumes
- Automatically repositions elements (pipes, ducts, trays) to avoid clashes
- Places manholes and transitions per discipline-specific rules
- Outputs structured CSVs for each system

In Revit, I wrote **Python scripts** that:
1. Read the CSV files
2. Create the MEP elements with accurate placement
3. Assign correct system and material data

📂 _Files related to this project are prefixed with `P1_`._

---

## 🏢 Project 2 – Twin Tower High-Rise MEP Coordination

**📌 Problem:**  
The incoming AutoCAD layouts for a twin-tower high-rise project included multiple MEP systems: ventilation, greywater, freshwater, sprinkler, and electrical trays. Manual modeling and coordination in Revit would be extremely time-consuming and error-prone.

**⚙️ Solution**  
I revised the previously developed Grasshopper + CSV workflow to adapt it to this vertical building typology. The process:
- Extracted required parameters from AutoCAD layouts
- Calculated optimal routing and offsets within tight shaft spaces
- Obeyed coordination rules per system (e.g., minimum spacing, duct heights)
- Generated CSVs used by a Python script in Revit to model all MEP systems accurately

📂 _Files related to this project are prefixed with `P2_`._

---

### 📌 Note

The core automation framework developed in these projects has since been adapted and reused in several other MEP-heavy projects, enabling rapid coordination and modeling while reducing manual workload and conflicts.

---

👤 Author: Anıl Bayburtluoğlu  
Visit the [main portfolio](../../README.md) for more projects or reach out via [LinkedIn](https://www.linkedin.com/in/anilbayburt) or mail: anilbayburt@gmail.com

