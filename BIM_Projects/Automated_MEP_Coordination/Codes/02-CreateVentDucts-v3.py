import csv


from Autodesk.Revit.DB import XYZ, Line, Transaction, BuiltInCategory, ElementId
from Autodesk.Revit.DB import Curve, Line, XYZ, IntersectionResultArray, SetComparisonResult
from Autodesk.Revit.DB.Plumbing import Pipe
from Autodesk.Revit.DB.Plumbing import PipeType
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


# Find the level named "xxx"
level_id = None
for level in levels:
    if level.Name == "L01":
        level_id = level.Id
        break


csv_rectDucts = r"E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\10-SMOKE\cur-smoke-rectDucts.csv"
csv_elbows = r"E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\10-SMOKE\cur-smoke-elbows.csv"
csv_transitions = r"E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\10-SMOKE\cur-smoke-transitions.csv"
csv_risers = r"E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\10-SMOKE\cur-smoke-ductrisers.csv"
csv_sizeBlocks = r"E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\10-SMOKE\cur-smoke-sizeBlocks.csv"



# Get the system type, pipe type, and level for the duct
system_type_id_Exhaust = ElementId(132469)  
system_type_id_Return = ElementId(132468)  
system_type_id_Supply = ElementId(132467)


def delete_existing_ducts_and_fittings():
    ductfittings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctFitting).WhereElementIsNotElementType().ToElements()
    ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
    for duct in ducts:
        completed = duct.LookupParameter('CMS_Completed').AsInteger()
        if completed == 0:
            doc.Delete(duct.Id)   
    for fitting in ductfittings:
        completed = fitting.LookupParameter('CMS_Completed').AsInteger()
        if completed == 0:
            doc.Delete(fitting.Id)

#create a function; inputs are a point and a duct, get all the ducts in document, find the closest connector of ducts to the point except the duct itself, return the owner duct of the connector
def get_closest_duct_to_point(point, duct):
    ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
    #select the ducts with "CMS_Completed" parameter as 0
    ducts = [d for d in ducts if d.LookupParameter('CMS_Completed').AsInteger() == 0]    



    min_distance = 500/304.8
    closest_duct = None
    for d in ducts:
        duct_shape = d.LookupParameter('CMS_DuctShape').AsString()
        if duct_shape == "round":
            width = d.LookupParameter('Diameter').AsDouble()
        elif duct_shape == "rectangular":
            width = d.LookupParameter('Width').AsDouble()

        if d.Id != duct.Id and width < 280 / 304.8:
            connectors = d.ConnectorManager.Connectors
            for connector in connectors:
                distance = XYZ(connector.Origin.X, connector.Origin.Y, 0).DistanceTo(XYZ(point.X, point.Y, 0))
                if distance < min_distance:
                    min_distance = distance
                    #print(f"Min distance: {min_distance}")
                    closest_duct = d
    return closest_duct


def create_rect_ducts_from_csv():

    # Read the CSV line files and create simple pipes
    with open(r'E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\07-VEN\CUR-RECTS.csv', 'r') as ducts_file:
        ducts_reader = csv.DictReader(ducts_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation + 4250 / 304.8

        # Create the pipes
        for row in ducts_reader:       
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation)
            end = XYZ(float(row['EndX']) / 304.8, float(row['EndY']) / 304.8, elevation)
            duct_width = float(row['KesitX']) / 304.8
            duct_height = float(row['KesitY']) / 304.8
            #get length from distance from start to end
            length = start.DistanceTo(end)
            min_length = 150 / 304.8         
            system_name = row['SystemName']
            global_system_name = system_name
            duct_type_id = get_duct_type_id("rectangular")               
                

            
            if length > min_length:
                if "HVAC-S" in system_name:
                    system_id = system_type_id_Supply
                elif "HVAC-R" in system_name:
                    system_id = system_type_id_Return
                elif "HVAC-E" in system_name:
                    system_id = system_type_id_Exhaust
                elif "HVAC-F" in system_name:
                    system_id = system_type_id_Exhaust
                else:
                    #here raise an exception for type not found"
                    raise Exception(f"System type not found: {system_name}")
                duct = Duct.Create(doc, system_id, duct_type_id, level_id, start, end)
                duct.LookupParameter('Comments').Set(system_name)
                duct.LookupParameter('Width').Set(duct_width)
                duct.LookupParameter('Height').Set(duct_height)
                duct.LookupParameter('CMS_DuctShape').Set("rectangular") 


def create_round_ducts_from_csv():

    # Read the CSV line files and create simple pipes
    with open(r'E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\07-VEN\CUR-ROUNDS.csv', 'r') as ducts_file:
        ducts_reader = csv.DictReader(ducts_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation + 4250 / 304.8

        # Create the pipes
        for row in ducts_reader:     
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation)
            end = XYZ(float(row['EndX']) / 304.8, float(row['EndY']) / 304.8, elevation)
            diameter = float(row['Diameter']) / 304.8
            #get length from distance from start to end
            length = start.DistanceTo(end)
            min_length = 250 / 304.8         
            system_name = row['SystemName']
            duct_type_id = get_duct_type_id("round")


            
            if length > min_length:
                if "HVAC-S" in system_name:
                    system_id = system_type_id_Supply
                elif "HVAC-R" in system_name:
                    system_id = system_type_id_Return
                elif "HVAC-E" in system_name:
                    system_id = system_type_id_Exhaust
                elif "HVAC-F" in system_name:
                    system_id = system_type_id_Exhaust
                else:
                    #here raise an exception for type not found"
                    raise Exception(f"System type not found: {system_name}")
                duct = Duct.Create(doc, system_id, duct_type_id, level_id, start, end)
                duct.LookupParameter('Comments').Set(system_name)
                duct.LookupParameter('Diameter').Set(diameter)
                duct.LookupParameter('CMS_DuctShape').Set("round")

def create_rect_vertducts_from_csv():

    # Read the CSV line files and create simple pipes
    with open(r'E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\07-VEN\CUR-DOWNRECTS.csv', 'r') as ducts_file:
        ducts_reader = csv.DictReader(ducts_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation
        ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
        #select the ducts with "CMS_Completed" parameter as 0
        ducts = [d for d in ducts if d.LookupParameter('CMS_Completed').AsInteger() == 0]
        branch_height = 800/304.8
        # Create the pipes
        for row in ducts_reader:     
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation)               
            system_name = row['SystemName']
            duct_type_id = get_duct_type_id("rectangular")
            duct_width = 200/304.8
            duct_height = 200/304.8
            for duct in ducts:
                duct_level = doc.GetElement(duct.LevelId)
                if duct_level.Id == level_id:
                    if is_point_inside_duct(duct, start):
                        
                        elevation = duct.LookupParameter('Middle Elevation').AsDouble()
                        break

            


            print(f"ele: {elevation*304.8}")
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation - abs(level.Elevation))
            low_point = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation-branch_height- abs(level.Elevation))



            if "HVAC-S" in system_name:
                system_id = system_type_id_Supply
            elif "HVAC-R" in system_name:
                system_id = system_type_id_Return
            elif "HVAC-E" in system_name:
                system_id = system_type_id_Exhaust
            elif "HVAC-F" in system_name:
                system_id = system_type_id_Exhaust
            else:
                #here raise an exception for type not found"
                raise Exception(f"System type not found: {system_name}")
            duct = Duct.Create(doc, system_id, duct_type_id, level_id, start, low_point)
            duct.LookupParameter('Comments').Set(system_name)
            duct.LookupParameter('Width').Set(duct_width)
            duct.LookupParameter('Height').Set(duct_height)
            duct.LookupParameter('CMS_DuctShape').Set("rectangular")
        
            branch_duct = get_closest_duct_to_point(low_point, duct)
            if branch_duct:
                #print(f"Branch duct found: {branch_duct.Id}")
                #make the duct's width and height same with the branch duct
                
                duct.LookupParameter('Width').Set(branch_duct.LookupParameter('Height').AsDouble())
                duct.LookupParameter('Height').Set(branch_duct.LookupParameter('Width').AsDouble())
                #set the elevation of branch duct lower as branch height from its current elevation
                
                current_elevation = branch_duct.LookupParameter('Middle Elevation').AsDouble()
                branch_duct.LookupParameter('Middle Elevation').Set(current_elevation - branch_height)
                
                #get connectors of the duct and branch duct find the closest connectors and connect them with elbow
                duct_connectors = duct.ConnectorManager.Connectors
                branch_duct_connectors = branch_duct.ConnectorManager.Connectors
                min_distance = 500/304.8
                closest_duct_connector = None
                closest_branch_duct_connector = None
                for duct_connector in duct_connectors:
                    for branch_duct_connector in branch_duct_connectors:
                        distance = duct_connector.Origin.DistanceTo(branch_duct_connector.Origin)
                        if distance < min_distance:
                            min_distance = distance
                            closest_duct_connector = duct_connector
                            closest_branch_duct_connector = branch_duct_connector
                if closest_duct_connector and closest_branch_duct_connector and min_distance<200/304.8:
                    elbow = doc.Create.NewElbowFitting(closest_duct_connector, closest_branch_duct_connector)
                    branch_duct_system = branch_duct.LookupParameter('Comments').AsString()
                    elbow.LookupParameter('Comments').Set(branch_duct_system)
                
            else:
                #print("Branch duct not found")
                continue

def get_duct_type_id(duct_type_name):
    """
    Get the ID of a pipe type based on its name.

    Parameters:
    - doc: The Revit document.
    - pipe_type_name: The name of the pipe type.

    Returns:
    - The ID of the pipe type if found, None otherwise.
    """
    if duct_type_name == "round":
        duct_type_name = "Taps / Short Radius"
    elif duct_type_name == "rectangular":
        duct_type_name = "Radius Elbows / Taps"

    duct_type_id = None
    duct_types = FilteredElementCollector(doc).OfClass(DuctType).ToElements()
    for duct_type in duct_types:
        if duct_type.Name == duct_type_name:
            duct_type_id = duct_type.Id
            break
    return duct_type_id

def add_duct_insulations():
    ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
    #select the ducts with "CMS_Completed" parameter as 0
    ducts = [d for d in ducts if d.LookupParameter('CMS_Completed').AsInteger() == 0]
    ductinsulation_type_id = None
    ductinsulation_types = FilteredElementCollector(doc).OfClass(DuctInsulationType).ToElements()
    for ductinsulation_type in ductinsulation_types:
        if ductinsulation_type.Name == "Duct Wrap":
            ductinsulation_type_id = ductinsulation_type.Id
            break
    for duct in ducts:
        duct_level = doc.GetElement(duct.LevelId)
        duct_system = duct.LookupParameter('Comments').AsString()    
        
        if duct_level.Id == level_id and "HVAC-E" in duct_system:
            duct_insulation = DuctInsulation.Create(doc, duct.Id, ductinsulation_type_id, 50/304.8)
        elif duct_level.Id == level_id and "HVAC-R" in duct_system:
            duct_insulation = DuctInsulation.Create(doc, duct.Id, ductinsulation_type_id, 25/304.8)
        elif duct_level.Id == level_id and "HVAC-S" in duct_system:
            duct_insulation = DuctInsulation.Create(doc, duct.Id, ductinsulation_type_id, 25/304.8)
        elif duct_level.Id == level_id and "HVAC-F" in duct_system:
            duct_insulation = DuctInsulation.Create(doc, duct.Id, ductinsulation_type_id, 25/304.8)
            
def get_related_ceiling_height():
    ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
    #select the ducts with "CMS_Completed" parameter as 0
    ducts = [d for d in ducts if d.LookupParameter('CMS_Completed').AsInteger() == 0]
    for duct in ducts:
        start = duct.Location.Curve.GetEndPoint(0)
        end = duct.Location.Curve.GetEndPoint(1)
        start_top = XYZ(start.X, start.Y, start.Z + 5000/304.8)
        end_top = XYZ(end.X, end.Y, end.Z + 5000/304.8)
         

        line1 = Line.CreateBound(start, start_top)
        line2 = Line.CreateBound(end, end_top)     
        
        get_ceiling_from_link(doc, line1, duct)
        
    for duct in ducts:
        heightfound = duct.LookupParameter('CMS_HeightFound').AsInteger()
        start = duct.Location.Curve.GetEndPoint(0)
        end = duct.Location.Curve.GetEndPoint(1)
        start_top = XYZ(start.X, start.Y, start.Z + 5000/304.8)
        end_top = XYZ(end.X, end.Y, end.Z + 5000/304.8)
         

        line1 = Line.CreateBound(start, start_top)
        line2 = Line.CreateBound(end, end_top)   


        if heightfound != 1:
            get_ceiling_from_link(doc, line2, duct)
        else:
            continue                

    for duct in ducts:
        heightfound = duct.LookupParameter('CMS_HeightFound').AsInteger()
        if heightfound != 1:
            duct.LookupParameter('RelatedCeilingHeight').Set(2670)
            duct.LookupParameter('CMS_HeightFound').Set(True)
        else:
            continue
          
def organize_ducts_heights():
    ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
    #select the ducts with "CMS_Completed" parameter as 0
    ducts = [d for d in ducts if d.LookupParameter('CMS_Completed').AsInteger() == 0]
    bottom_duct_bottom_height = 800/304.8
    top_duct_bottom_height = 1350/304.8
    downbranch_duct_middle_height = 475/304.8
    for duct in ducts:
        related_ceiling_height = duct.LookupParameter('RelatedCeilingHeight').AsDouble()/304.8
        duct_shape = duct.LookupParameter('CMS_DuctShape').AsString()
        if duct_shape == "round":
            duct_height = duct.LookupParameter('Diameter').AsDouble()
        else:
            duct_height = duct.LookupParameter('Height').AsDouble()        
        #get the insulation thickness of the duct
        duct_ins_thickness = duct.LookupParameter('Insulation Thickness').AsDouble()       
        duct.LookupParameter('Middle Elevation').Set(related_ceiling_height + duct_height/2 + duct_ins_thickness + bottom_duct_bottom_height)


#create a function to get if a point is inside the bounding box of a duct
def is_point_inside_duct(duct, point):
    # Check if the duct is valid
    if duct is None:
        return False
    
    # Get the duct's bounding box
    duct_bb = duct.get_BoundingBox(None)
    
    # Check if the bounding box exists
    if duct_bb is None:
        return False
    else:    
        # Check if the point is inside the bounding box
        min_point = duct_bb.Min
        max_point = duct_bb.Max
        #modify the point'z to be middle of max and min
        point = XYZ(point.X, point.Y, (max_point.Z + min_point.Z)/2)
        return (min_point.X <= point.X <= max_point.X and
                min_point.Y <= point.Y <= max_point.Y and
                min_point.Z <= point.Z <= max_point.Z)

from Autodesk.Revit.DB import FilteredElementCollector, Transaction, BuiltInCategory # Adjusted import


def create_round_vertducts_from_csv():

    # Read the CSV line files and create simple pipes
    with open(r'E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\_MEP\07-VEN\CUR-ROUNDS.csv', 'r') as ducts_file:
        ducts_reader = csv.DictReader(ducts_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation
        ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
        branch_height = 800/304.8
        # Create the pipes
        for row in ducts_reader:     
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation)               
            system_name = row['SystemName']
            duct_type_id = get_duct_type_id("round")
            duct_diameter = row['Diameter']
            duct_diameter = float(duct_diameter)  / 304.8
            
            for duct in ducts:
                duct_level = doc.GetElement(duct.LevelId)
                if duct_level.Id == level_id:
                    if is_point_inside_duct(duct, start):
                        
                        elevation = duct.LookupParameter('Middle Elevation').AsDouble()
                        break

            



            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation - abs(level.Elevation))
            low_point = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation-branch_height- abs(level.Elevation))



            if "HVAC-S" in system_name:
                system_id = system_type_id_Supply
            elif "HVAC-R" in system_name:
                system_id = system_type_id_Return
            elif "HVAC-E" in system_name:
                system_id = system_type_id_Exhaust
            elif "HVAC-F" in system_name:
                system_id = system_type_id_Exhaust
            else:
                #here raise an exception for type not found"
                raise Exception(f"System type not found: {system_name}")
            duct = Duct.Create(doc, system_id, duct_type_id, level_id, start, low_point)
            duct.LookupParameter('Comments').Set(system_name)
            duct.LookupParameter('Diameter').Set(duct_diameter)
            duct.LookupParameter('CMS_DuctShape').Set("round")
            
            branch_duct = get_closest_duct_to_point(low_point, duct)
            if branch_duct:
                #print(f"Branch duct found: {branch_duct.Id}")
                #check if branch duct is round
                branch_duct_shape = branch_duct.LookupParameter('CMS_DuctShape').AsString()
                if branch_duct_shape == "round":
                    current_elevation = branch_duct.LookupParameter('Middle Elevation').AsDouble()
                    branch_duct.LookupParameter('Middle Elevation').Set(current_elevation - branch_height)
                    
                    #get connectors of the duct and branch duct find the closest connectors and connect them with elbow
                    duct_connectors = duct.ConnectorManager.Connectors
                    branch_duct_connectors = branch_duct.ConnectorManager.Connectors
                    min_distance = 500/304.8
                    closest_duct_connector = None
                    closest_branch_duct_connector = None
                    for duct_connector in duct_connectors:
                        for branch_duct_connector in branch_duct_connectors:
                            distance = duct_connector.Origin.DistanceTo(branch_duct_connector.Origin)
                            if distance < min_distance:
                                min_distance = distance
                                closest_duct_connector = duct_connector
                                closest_branch_duct_connector = branch_duct_connector
                    if closest_duct_connector and closest_branch_duct_connector:
                        if min_distance < 50/304.8:
                            #print(f"Closest duct connector: {closest_duct_connector.Id}")
                            elbow = doc.Create.NewElbowFitting(closest_duct_connector, closest_branch_duct_connector)
                            branch_duct_system = branch_duct.LookupParameter('Comments').AsString()
                            elbow.LookupParameter('Comments').Set(branch_duct_system)
                
            else:
                #print("Branch duct not found")
                continue
            
def add_transition_fittings():
    # Start a transaction (assuming `doc` is the current document)
    t = Transaction(doc, "Add Fittings")
    t.Start()
    
    try:
        duct_collector = FilteredElementCollector(doc).OfClass(Duct)
        #select the ducts with "CMS_Completed" parameter as 0
        ducts = [d for d in duct_collector if d.LookupParameter('CMS_Completed').AsInteger() == 0]
        ducts = list(duct_collector)
        
        for i in range(len(ducts)):
            for j in range(i+1, len(ducts)):
                duct1 = ducts[i]
                duct2 = ducts[j]
                min_distance = 1000/304.8  # Minimum distance between ducts for a fitting
                # Ensure ducts and connectors are valid before proceeding
                if not duct1 or not duct2 or not duct1.ConnectorManager or not duct2.ConnectorManager:
                    continue
                
                connectors1 = duct1.ConnectorManager.Connectors
                connectors2 = duct2.ConnectorManager.Connectors
                
                for connector1 in connectors1:
                    for connector2 in connectors2:
                        # Validate connectors before use
                        if not connector1 or not connector2:
                            continue
                        
                        # Check distance and connection status
                        if connector1.Origin.DistanceTo(connector2.Origin) < min_distance and not connector1.IsConnected and not connector2.IsConnected and (connector1.Origin.X == connector2.Origin.X or connector1.Origin.Y == connector2.Origin.Y):
                            # Check for compatibility before attempting to create a fitting
                            if duct1.DuctType.Id.IntegerValue == duct2.DuctType.Id.IntegerValue:
                                # Attempt to create fitting and handle exceptions
                                try:
                                    #doc.Create.NewElbowFitting(connector1, connector2)
                                    fitting = doc.Create.NewTransitionFitting(connector1, connector2)
                                    systemname = duct1.LookupParameter('Comments').AsString()
                                    fitting.LookupParameter('Comments').Set(systemname)
                                except Exception as e:  # Using a more general exception
                                    print(f"Failed to create fitting between ducts {duct1.Id} and {duct2.Id}: {str(e)}")
        print("Fittings added successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Commit or roll back the transaction as appropriate
        t.Commit()


def add_elbow_fittings():
    # Start a transaction (assuming `doc` is the current document)
    t = Transaction(doc, "Add Fittings")
    t.Start()
    
    try:
        duct_collector = FilteredElementCollector(doc).OfClass(Duct)
        #select the ducts with "CMS_Completed" parameter as 0
        ducts = [d for d in duct_collector if d.LookupParameter('CMS_Completed').AsInteger() == 0]
        ducts = list(duct_collector)
        
        for i in range(len(ducts)):
            for j in range(i+1, len(ducts)):
                duct1 = ducts[i]
                duct2 = ducts[j]
                min_distance = 1500/304.8  # Minimum distance between ducts for a fitting
                # Ensure ducts and connectors are valid before proceeding
                if not duct1 or not duct2 or not duct1.ConnectorManager or not duct2.ConnectorManager:
                    continue
                
                connectors1 = duct1.ConnectorManager.Connectors
                connectors2 = duct2.ConnectorManager.Connectors
                
                for connector1 in connectors1:
                    for connector2 in connectors2:
                        # Validate connectors before use
                        if not connector1 or not connector2:
                            continue
                        
                        # Check distance and connection status
                        if connector1.Origin.DistanceTo(connector2.Origin) < min_distance and not connector1.IsConnected and not connector2.IsConnected:
                            # Check for compatibility before attempting to create a fitting
                            if duct1.DuctType.Id.IntegerValue == duct2.DuctType.Id.IntegerValue:
                                # Check if ducts are rectangular and have the same width and height
                                if duct1.LookupParameter('CMS_DuctShape').AsString() == "rectangular" and duct2.LookupParameter('CMS_DuctShape').AsString() == "rectangular":
                                    if duct1.LookupParameter('Width').AsDouble() == duct2.LookupParameter('Width').AsDouble() and duct1.LookupParameter('Height').AsDouble() == duct2.LookupParameter('Height').AsDouble():
                                        # Check if connector positions are different
                                        treshold = 300/304.8  # Minimum distance between ducts for a fitting
                                        if connector1.Origin.DistanceTo(connector2.Origin) < treshold and not connector1.IsConnected and not connector2.IsConnected:
                                            # Attempt to create fitting and handle exceptions
                                            try:
                                                fitting = doc.Create.NewElbowFitting(connector1, connector2)
                                                systemname = duct1.LookupParameter('Comments').AsString()
                                                fitting.LookupParameter('Comments').Set(systemname)
                                            except Exception as e:  # Using a more general exception
                                                print(f"Failed to create elbow fitting between ducts {duct1.Id} and {duct2.Id}: {str(e)}")
        print("Fittings added successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Commit or roll back the transaction as appropriate
        t.Commit()

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


def Connect_same_ducts():
    # Start a transaction (assuming `doc` is the current document)
    t = Transaction(doc, "Connect Ducts")
    t.Start()
    
    try:
        duct_collector = FilteredElementCollector(doc).OfClass(Duct)
        #select the ducts with "CMS_Completed" parameter as 0
        ducts = [d for d in duct_collector if d.LookupParameter('CMS_Completed').AsInteger() == 0]
        ducts = list(duct_collector)
        
        for i in range(len(ducts)):
            for j in range(i+1, len(ducts)):
                duct1 = ducts[i]
                duct2 = ducts[j]
                min_distance = 350/304.8  # Minimum distance between ducts for a connection
                # Ensure ducts and connectors are valid before proceeding
                if not duct1 or not duct2 or not duct1.ConnectorManager or not duct2.ConnectorManager:
                    continue
                
                connectors1 = duct1.ConnectorManager.Connectors
                connectors2 = duct2.ConnectorManager.Connectors
                
                for connector1 in connectors1:
                    for connector2 in connectors2:
                        # Validate connectors before use
                        if not connector1 or not connector2:
                            continue
                        
                        # Check distance and connection status
                        if connector1.Origin.DistanceTo(connector2.Origin) < min_distance and not connector1.IsConnected and not connector2.IsConnected and (connector1.Origin.X == connector2.Origin.X or connector1.Origin.Y == connector2.Origin.Y):
                            # Check if ducts have the same duct shape
                            if duct1.LookupParameter('CMS_DuctShape').AsString() == "rectangular" and duct2.LookupParameter('CMS_DuctShape').AsString() == "rectangular":
                                # Check if ducts have the same width and height
                                threshold = 100  # Adjust the threshold value as needed

                                if abs(duct1.LookupParameter('Width').AsDouble() - duct2.LookupParameter('Width').AsDouble()) < threshold and abs(duct1.LookupParameter('Height').AsDouble() - duct2.LookupParameter('Height').AsDouble()) < threshold:
                                    # Check and adjust directions before connecting
                                    direction1 = connector1.CoordinateSystem.BasisZ
                                    direction2 = connector2.CoordinateSystem.BasisZ
                                    if direction1.IsAlmostEqualTo(direction2.Negate(), 0.01):
                                        # Reverse one of the ducts here. This step depends on the API's capabilities.
                                        # For example, you might set a parameter or call a method to reverse the duct.
                                        # This is a placeholder for the actual implementation.
                                        pass
                                    
                                    # Now connect the ducts
                                    connector1.ConnectTo(connector2)
                                    break
        print("Ducts connected successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Commit or roll back the transaction as appropriate
        t.Commit()

def tr_delete_duplicate_elements():
    # Start the transaction
    t = Transaction(doc, "delete duplicates")
    t.Start()

    # Create a dictionary to store elements
    elements_dict = {}

    # Create a list to store elements to be deleted
    elements_to_delete = []

    ducts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DuctCurves).WhereElementIsNotElementType().ToElements()
    # Iterate over the elements
    for elem in ducts:
        # Get the parameters
        parameters = (
            elem.Location.Curve.GetEndPoint(0).X,
            elem.Location.Curve.GetEndPoint(0).Y,            
            elem.Location.Curve.GetEndPoint(1).X,
            elem.Location.Curve.GetEndPoint(1).Y,
            elem.LookupParameter('Comments').AsDouble(),
                      
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



t = Transaction(doc, "Put ducts on the right level")
t.Start()

delete_existing_ducts_and_fittings()



#create_rect_ducts_from_csv()
#create_round_ducts_from_csv()

t.Commit()




t = Transaction(doc, "Connect Ducts")
t.Start()
#add_duct_insulations()
#get_related_ceiling_height()
#organize_ducts_heights()

t.Commit()


#tr_delete_duplicate_elements()


t = Transaction(doc, "Connect Ducts")

t.Start()

#create_rect_vertducts_from_csv()
#create_round_vertducts_from_csv()

t.Commit()

#Connect_same_ducts()
