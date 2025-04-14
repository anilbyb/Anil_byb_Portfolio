import csv


from Autodesk.Revit.DB import XYZ, Line, Transaction, BuiltInCategory, ElementId
from Autodesk.Revit.DB import Curve, Line, XYZ, IntersectionResultArray, SetComparisonResult
from Autodesk.Revit.DB.Plumbing import Pipe
from Autodesk.Revit.DB.Plumbing import PipeType, PipeInsulation, PipeInsulationType, PipingSystem, PipingSystemType
from Autodesk.Revit.DB.Mechanical import Duct, DuctType, DuctInsulation, DuctInsulationType
import System
from System import Array

clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')


from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


from Autodesk.Revit.DB import Transaction, MEPSystem, BuiltInCategory, FilteredElementCollector
from Autodesk.Revit.Exceptions import InvalidOperationException


# Get the current document
doc = __revit__.ActiveUIDocument.Document


# Get all levels in the document
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

zone_name = "ZON-5"
# Find the level named "xxx"
level_id = None
for level in levels:
    if level.Name == "L06":
        level_id = level.Id
        break

# Get the system type, pipe type, and level for the duct



#find the system type id by name
def get_system_type_id(system_name):
    system_type_id = None
    system_types = FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements()
    for system_type in system_types:
        print(system_type.Name)
        if system_type.Name == system_name:
            system_type_id = system_type.Id
            break
    return system_type_id


def delete_existing_pipes_and_fittings():
    pipe_fittings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeFitting).WhereElementIsNotElementType().ToElements()
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    for pipe in pipes:
        pipe_level = doc.GetElement(pipe.LevelId)
        if pipe_level.Id == level_id:
            doc.Delete(pipe.Id)   
    for fitting in pipe_fittings:
        fitting_level = doc.GetElement(fitting.LevelId)
        if fitting_level.Id == level_id:
            doc.Delete(fitting.Id)




def create_HPipes_from_csv():

    # Read the CSV line files and create simple pipes
    with open(r'E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\02-DOW\L06-DOWCurves.csv', 'r') as HPipes_file:
        HPipes_reader = csv.DictReader(HPipes_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation
        i = 2
        # Create the pipes
        for row in HPipes_reader:
            zone = row['ZONE']          
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation)
            end = XYZ(float(row['EndX']) / 304.8, float(row['EndY']) / 304.8, elevation)
            distance = (start - end).GetLength()*304.8
            if distance > 10 / 304.8:
                PSize = float(row['PSize']) / 304.8         
                system_name = row['SystemName']
                system_type = row['SystemType']
                position = row['Position']
                pipe_type_id = get_pipe_type_id(system_type)
                Critical = row['Critical']
                if zone == zone_name:
                    if "B1" in system_type:
                        system_id = get_system_type_id("Domestic Cold Water")
                    elif "T3" in system_type:
                        system_id = get_system_type_id("Domestic Hot Water")
                    elif "T4" in system_type:
                        system_id = get_system_type_id("Domestic Hot Water Circ")
                    else:                    
                        raise Exception(f"System type not found: {system_name}")
                    pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, start, end)
                    pipe.LookupParameter('Comments').Set(system_name)
                    pipe.LookupParameter('CMS_Position').Set(position)
                    pipe.LookupParameter('isCritical').Set(Critical)
                    if Critical == "critical":
                        pipe.LookupParameter('RNS_Critical Arae Information').Set(True)
                    else:
                        pipe.LookupParameter('RNS_Critical Arae Information').Set(False)
                    if PSize == 0:
                        pipe.LookupParameter('Diameter').Set(32 / 304.8)
                        pipe.LookupParameter('CMS_SizeNote').Set("Need To Check") 
                    else:
                        pipe.LookupParameter('Diameter').Set(PSize)
                i += 1
            else:
                print(f"Distance is too short for pipe {i}")
                i += 1


def get_pipe_type_id(systemtype):
    """
    Get the ID of a pipe type based on its name.

    Parameters:
    - doc: The Revit document.
    - pipe_type_name: The name of the pipe type.

    Returns:
    - The ID of the pipe type if found, None otherwise.
    """
    if systemtype:
        pipe_type_name = "PVC - DWV"
    

    pipe_type_id = None
    pipe_types = FilteredElementCollector(doc).OfClass(PipeType).ToElements()
    for pipe_type in pipe_types:
        if pipe_type.Name == pipe_type_name:
            pipe_type_id = pipe_type.Id
            break
    return pipe_type_id

def add_pipe_insulations():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    pipeinsulation_type_id = None
    pipeinsulation_types = FilteredElementCollector(doc).OfClass(PipeInsulationType).ToElements()
    for pipeinsulation_type in pipeinsulation_types:
        if pipeinsulation_type.Name == "Fiberglass":
            pipeinsulation_type_id = pipeinsulation_type.Id
            break
    for pipe in pipes:
        pipe_level = doc.GetElement(pipe.LevelId)     
        
        if pipe_level.Id == level_id:
            pipe_insulation = PipeInsulation.Create(doc, pipe.Id, pipeinsulation_type_id, 25/304.8)
                
def get_related_ceiling_height():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    for pipe in pipes:
        start = pipe.Location.Curve.GetEndPoint(0)
        end = pipe.Location.Curve.GetEndPoint(1)
        start_top = XYZ(start.X, start.Y, start.Z + 5000/304.8)
        end_top = XYZ(end.X, end.Y, end.Z + 5000/304.8)
         

        line1 = Line.CreateBound(start, start_top)
        line2 = Line.CreateBound(end, end_top)     
        
        get_ceiling_from_link(doc, line1, pipe)
        
    for pipe in pipes:
        heightfound = pipe.LookupParameter('CMS_HeightFound').AsInteger()
        start = pipe.Location.Curve.GetEndPoint(0)
        end = pipe.Location.Curve.GetEndPoint(1)
        start_top = XYZ(start.X, start.Y, start.Z + 5000/304.8)
        end_top = XYZ(end.X, end.Y, end.Z + 5000/304.8)
         

        line1 = Line.CreateBound(start, start_top)
        line2 = Line.CreateBound(end, end_top)   


        if heightfound != 1:
            get_ceiling_from_link(doc, line2, pipe)
        else:
            continue                

    for pipe in pipes:
        heightfound = pipe.LookupParameter('CMS_HeightFound').AsInteger()
        if heightfound != 1:
            pipe.LookupParameter('RelatedCeilingHeight').Set(2700)
            pipe.LookupParameter('CMS_HeightFound').Set(True)
        else:
            continue
          
def organize_pipes_heights():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    main_pipe_middle_height = 695/304.8
    branch_pipe_middle_height = 435/304.8
    for pipe in pipes:
        related_ceiling_height = pipe.LookupParameter('RelatedCeilingHeight').AsDouble()/304.8    
        position = pipe.LookupParameter('CMS_Position').AsString()
        if position == "main":
            pipe.LookupParameter('Middle Elevation').Set(related_ceiling_height + main_pipe_middle_height)
        elif position == "branch":
            pipe.LookupParameter('Middle Elevation').Set(related_ceiling_height + branch_pipe_middle_height)
        else:
            pipe.LookupParameter('Middle Elevation').Set(related_ceiling_height + main_pipe_middle_height)



def get_ceiling_from_link(doc, line, elem):
    link_instances = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
    for link_instance in link_instances:
        link_doc = link_instance.GetLinkDocument()
        if link_doc is not None:
            title = link_doc.Title
            if "A-GN-M3" in title:
                Ceiling_collector = FilteredElementCollector(link_doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType()
                for ceiling in Ceiling_collector:
                    if ceiling.LevelId == elem.LevelId:
                        geometry = ceiling.get_Geometry(Options())        
                        for geo in geometry:
                            if isinstance(geo, Solid):
                                for face in geo.Faces:
                                    result_array = clr.Reference[IntersectionResultArray]()
                                    result = face.Intersect(line, result_array)
                                    # Print the result of the Intersect method                    
                                    if result == SetComparisonResult.Overlap:                                                                             
                                        # Get the "Height Offset From Level" parameter of the ceiling
                                        height_offset = ceiling.LookupParameter('Height Offset From Level').AsDouble()
                                        # Set the "Elevation from Level" parameter of the air terminal to the height offset
                                        elem.LookupParameter('RelatedCeilingHeight').Set(height_offset*304.8)
                                        elem.LookupParameter('CMS_HeightFound').Set(True)
                                        break
                                        
                                    else:
                                        continue
    return None        




def tr_delete_duplicate_elements():
    # Start the transaction
    t = Transaction(doc, "delete duplicates")
    t.Start()

    # Create a dictionary to store elements
    elements_dict = {}

    # Create a list to store elements to be deleted
    elements_to_delete = []

    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    # Iterate over the elements
    for elem in pipes:
        # Get the parameters
        parameters = (
            elem.Location.Curve.GetEndPoint(0).X,
            elem.Location.Curve.GetEndPoint(0).Y,
            elem.Location.Curve.GetEndPoint(0).Z,
            elem.Location.Curve.GetEndPoint(1).X,
            elem.Location.Curve.GetEndPoint(1).Y,
            elem.Location.Curve.GetEndPoint(1).Z            
        )

        # Create a key from the parameters
        key = hash(parameters)

        # Check if the key already exists in the dictionary
        if key in elements_dict:
            # If it does, add the element to the list of elements to delete
            elements_to_delete.append(elem.Id)
        else:
            # If it doesn't, add the key and the element to the dictionary
            elements_dict[key] = elem

    # Delete the elements
    for elem_id in elements_to_delete:
        doc.Delete(elem_id)

    # Print out how many elements were deleted
    print(f"{len(elements_to_delete)} elements were deleted.")

    # Commit the transaction
    t.Commit()

t = Transaction(doc, "Put pipes on the right level")
t.Start()

delete_existing_pipes_and_fittings()

create_HPipes_from_csv()
add_pipe_insulations()
get_related_ceiling_height()
organize_pipes_heights()

t.Commit()