# 🧱 Automated Facade Production Modeling

This project focuses on the creation of detailed production models for facade elements of a complex architectural structure.

---

## 🧩 Main Challenge

The architectural designs featured **non-repetitive, angular or curved facade geometry**, which made manual modeling of individual profiles and connections inefficient and error-prone.

# 🧱 Parametric Facade Projects

This folder contains two distinct facade modeling and automation projects developed using Rhino, Grasshopper, Revit, and Dynamo. Both projects were designed to solve geometry-related challenges arising from complex architectural designs and to support precise production or BIM delivery workflows.

Each project’s files are prefixed accordingly:
- `P1_`: Project 1 – Twisted Tower Panel Detailing
- `P2_`: Project 2 – Curved Floorplan Facade Parametrization

---

## 🏢 Project 1 – Twisted Tower Facade Panel Detailing

**📌 Problem:**  
A major bank’s headquarters, composed of two high-rise towers, features a twisted box architectural form. As a result, the facade includes triangular panels with varying angles and sizes. In order to connect these panels properly to both the building and to each other, high-precision connection details had to be modeled based on the chosen fabrication method.

**⚙️ Solution**  
To address this, I developed a **Grasshopper definition** that automates the generation of:
- 3D facade profiles  
- Substructure geometries  
- Connection details  

The algorithm works by **selecting a surface** from the base facade model. It then:
1. Analyzes surface orientation and curvature  
2. Aligns profile elements accordingly  
3. Creates parametric extrusion and connection logic  
4. Outputs geometry suitable for production and detailing in Rhino  

📂 _Files related to this project are prefixed with `P1_`._

---

## 🏦 Project 2 – Curved Floorplan Facade Parametrization

**📌 Problem:**  
The architectural design of another bank’s 10-story headquarters featured uniquely curved floor plans drawn using AutoCAD’s spline tool. The facade elements needed to be delivered as a detailed Revit model.

**⚙️ Solution**  
To address this, I developed a **multi-tool workflow** using Grasshopper, CSV, and Dynamo, which automates the generation of:
- Parametric facade panel types  
- Sliced spline-derived surfaces  
- Adaptive component placement in Revit  

The algorithm:
1. Reads spline curves from AutoCAD  
2. Slices them based on geometric rules  
3. Exports curvature parameters and panel types into a `.csv` file  
4. Dynamo then reads this file in Revit  
5. Uses the data to place and configure adaptive families with correct curvature and orientation  

📂 _Files related to this project are prefixed with `P2_`._

---

📌 *Project names and client details are omitted due to confidentiality agreements. Visuals and scripts represent the underlying logic and technical contribution.*


---

## 📁 Included Files

- `Images/`: Rendered images showing the final output on sample facade sections
- `Codes/`: Grasshopper definition files (`.gh`)
- `Models/`: Rhino 3D base facade model and sample outputs (`.3dm`)

---

## 🛠️ Tools Used

- Rhino 7
- Grasshopper (Visual Programming)
- Revit 2018
- Dynamo
- Architectural facade design references

---

## 📌 Notes

- Project name and building details are omitted due to confidentiality.
- Visuals included are generic representations of the solution logic and algorithm behavior.

---

## 👤 Author: Anıl Bayburtluoğlu  
For the full portfolio, visit the [main repository](../../README.md)  
Contact: [LinkedIn](https://www.linkedin.com/in/anilbaybur)


