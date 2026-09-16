# Facility Management Software Demo

This is a facility-management software demo prepared for a company. The workflow combined a Revit add-in for data export with a Unity application for model viewing, asset information and maintenance-related task handling.

## Workflow

1. A Revit add-in exported model geometry as FBX.
2. Revit parameter data was exported as CSV files.
3. A Unity application loaded the model and related asset information.
4. The viewer supported realistic and shaded model views.
5. Maintenance and warranty data were used to create colour-coded views with a legend.
6. Users could select elements from 3D, 2D or list views and inspect information such as type, brand, point of contact, room and building.
7. Users could create tasks linked to selected elements, including responsibility, location and the element to be maintained or replaced.

## Technical Scope

- **Source platform:** Revit add-in for export
- **Viewer platform:** Unity
- **Data flow:** FBX geometry plus CSV parameter data
- **Repository contents:** Documentation and demo notes only

## Demo Folder

See the [demo notes](DEMO/README.md) for the repository-level demo context.

## Notes

The full Revit add-in, Unity project source, exported client model data and build files are not included in this repository.
