import csv

from Autodesk.Revit.DB import XYZ, Line, Transaction, BuiltInCategory, ElementId
from Autodesk.Revit.DB import Curve, Line, XYZ, IntersectionResultArray, SetComparisonResult
from Autodesk.Revit.DB.Plumbing import Pipe
from Autodesk.Revit.DB.Plumbing import PipeType
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

zone_name = "ZON-2"
# Find the level named 
level_id = None
for level in levels:
    if level.Name == "L05":
        level_id = level.Id
        break

# Get the system type, pipe type, and level for the pipe
system_type_id_FPwet = ElementId(132476)  # Fire Protection Wet
system_type_id_FPPreAction = ElementId(132478)  # Fire Protection Pre Action
system_type_id_FPDry = ElementId(132477)  # Fire Protection Dry
system_type_id_FPMain = ElementId(132479)  # Fire Protection Other / Main
system_type_id_Sanitary = ElementId(132473)  # Sanitary Drainage

def reset_organized_sprinklers():
    sprinklers = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sprinklers).WhereElementIsNotElementType().ToElements()
    for sprinkler in sprinklers:
        sprinkler.LookupParameter('isOrganized').Set(False)


def tr_delete_pipes_to_delete():
    # Start the transaction
    t = Transaction(doc, "delete splitted pipes")
    t.Start()    
    pipes_to_delete = []
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    for pipe in pipes:
        has_Sprinkler = pipe.LookupParameter('HasSprinkler').AsInteger()
        print(f"Pipe {pipe.Id} has sprinkler: {has_Sprinkler}")
        pipe_level = doc.GetElement(pipe.LevelId)
        if has_Sprinkler != 1 and pipe_level.Id == level_id:

            pipes_to_delete.append(pipe.Id)
        else:
            print(f"Pipe {pipe.Id} is not deleted.")
            pass


    for elem in pipes_to_delete:
        if doc.GetElement(elem):
            doc.Delete(elem)
            print(f"Pipe {elem} is deleted.")

    # Commit the transaction
    t.Commit()

extra_pipes_to_delete = []
def tr_delete_extra_pipes():
    # Start the transaction
    t = Transaction(doc, "delete splitted pipes")
    t.Start()    

    for elem in extra_pipes_to_delete:
        if doc.GetElement(elem):
            doc.Delete(elem)
            print(f"Pipe {elem} is deleted.")

    # Commit the transaction
    t.Commit()

def get_curve_intersection(curve1, curve2):
    # Create a reference to hold the IntersectionResultArray
    resultArray = clr.Reference[IntersectionResultArray]()
    
    # Perform the intersection
    result = curve1.Intersect(curve2, resultArray)
    
    # Check if the intersection result indicates an intersection
    if result == SetComparisonResult.Overlap and resultArray.Value and resultArray.Value.Size > 0:
        # Extract the intersection point(s)
        intersection_points = [resultItem.XYZPoint for resultItem in resultArray.Value]
        return intersection_points
    else:
        return None


def delete_existing_pipes_and_fittings():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    fittings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeFitting).WhereElementIsNotElementType().ToElements()
    sprinklers = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sprinklers).WhereElementIsNotElementType().ToElements()

    for sprinkler in sprinklers:
        sprinkler_level = doc.GetElement(sprinkler.LevelId)
        if sprinkler_level.Id == level_id and sprinkler.Name == 'Pendent Sprinkler':
            doc.Delete(sprinkler.Id)
        elif sprinkler_level.Id == level_id and sprinkler.Name == 'Upright Sprinkler':
            doc.Delete(sprinkler.Id)

    for pipe in pipes:
        pipe_level = doc.GetElement(pipe.LevelId)
        if pipe_level.Id == level_id:
            doc.Delete(pipe.Id)   
    for fitting in fittings:
        fitting_level = doc.GetElement(fitting.LevelId)
        if fitting_level.Id == level_id:
            doc.Delete(fitting.Id)

def get_pipe_type_id(pipe_type_name):
    """
    Get the ID of a pipe type based on its name.

    Parameters:
    - doc: The Revit document.
    - pipe_type_name: The name of the pipe type.

    Returns:
    - The ID of the pipe type if found, None otherwise.
    """
    pipe_type_id = None
    pipe_types = FilteredElementCollector(doc).OfClass(PipeType).ToElements()
    for pipe_type in pipe_types:
        if pipe_type.Name == pipe_type_name:
            pipe_type_id = pipe_type.Id
            break
    return pipe_type_id

def create_sprinkler_pipes_from_csv():

    # Read the CSV line files and create simple pipes
    with open(r'C:\ScriptCSV\FP\L05-Curves.csv', 'r') as lines_file:
        lines_reader = csv.DictReader(lines_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation

        # Create the pipes
        for row in lines_reader:            
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation)
            end = XYZ(float(row['EndX']) / 304.8, float(row['EndY']) / 304.8, elevation)
            pipe_length= start.DistanceTo(end)

            system_name = row['SystemName']
            zone = row['ZONE']
            critical = row['Critical']
            if zone == zone_name and pipe_length > 250/304.8:
                if "Discharge" in system_name:
                    pipe_type_id = get_pipe_type_id("Fire-Discharge")
                    system_id = system_type_id_Sanitary
                elif "Dry" in system_name:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPDry
                elif "Action" in system_name:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPPreAction
                elif "Main" in system_name:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPMain
                else:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPwet
                pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, start, end)
                pipe.LookupParameter('IsUpperPipe').Set(False)
                pipe.LookupParameter('IsHorizontal').Set(True)
                #set the Diameter parameter of the pipe as 25mm
                pipe.LookupParameter('Diameter').Set(25/304.8)
                #read SystemName row of the csv file and write it to comments of the pipe
                pipe.LookupParameter('Comments').Set(system_name)
                pipe.LookupParameter('isCritical').Set(critical)



def organize_sprinkler_pipes():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    sprinklers = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sprinklers).WhereElementIsNotElementType().ToElements()

    system_id = system_type_id_FPwet
    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")

    for sprinkler in sprinklers:
        #get the level of the sprinkler
        sprinkler_level = doc.GetElement(sprinkler.LevelId)
        #get the location of the sprinkler
        location = sprinkler.Location
        #get the location point of the sprinkler
        location_point = location.Point
        #get the location point x and y coordinates
        x = location_point.X
        y = location_point.Y
        z = sprinkler.LookupParameter('Elevation from Level').AsDouble()
        related_ceiling_height = z
        #create a new point variable named check_location only with X and Y, Z = 0 
        check_location = XYZ(x, y, 0)
        print(sprinkler.Id)
        
        for pipe in pipes:
            pipe_level = doc.GetElement(pipe.LevelId)
            pipe_comments = pipe.LookupParameter('Comments').AsString()
            isOrganized = sprinkler.LookupParameter('isOrganized').AsInteger()            
            if pipe_level.Id == level_id and 'Sprinkler' in pipe_comments:
                start = pipe.Location.Curve.GetEndPoint(0)
                end = pipe.Location.Curve.GetEndPoint(1)
                start = XYZ(start.X, start.Y, 0)
                end = XYZ(end.X, end.Y, 0)
                min_distance = 150/304.8
                if start.DistanceTo(check_location) < min_distance or end.DistanceTo(check_location) < min_distance:
                    #Upright and Pendent Sprinkler
                    if isOrganized == 0 and sprinkler_level.Id == level_id and sprinkler.Name == "SPRA006":      
                        #change the Middle Elevation of pipe as the Z coordinate of the sprinkler + 350mm in feet
                        pipe.LookupParameter('Middle Elevation').Set(z + 350/304.8)
                        copied = pipe.LookupParameter('CopiedPipe').AsInteger()
                        pipe.LookupParameter('HasSprinkler').Set(True)
                        pipe.LookupParameter('RelatedCeilingHeight').Set(related_ceiling_height)
                        pipe.LookupParameter('IsUpperPipe').Set(False)
                        sprinkler.LookupParameter('isOrganized').Set(True)
                        #pipe.LookupParameter('OrganizedPipe').Set(True)                   
                        
                        if copied != 1:
                            pipe.LookupParameter('CopiedPipe').Set(True)
                            #get the start and end points of the pipe
                            start = pipe.Location.Curve.GetEndPoint(0)
                            end = pipe.Location.Curve.GetEndPoint(1)
                            #create a new pipe with the same start and end points
                            pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                            system_id = system_type_id_FPwet
                            copied_pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, start, end)
                            #set the Diameter parameter of the copied pipe as 25mm
                            copied_pipe.LookupParameter('Diameter').Set(25/304.8)
                            #set the CopiedPipe parameter as true
                            copied_pipe.LookupParameter('CopiedPipe').Set(True)
                            #set the Comments parameter of the copied pipe as the same with the original pipe
                            copied_pipe.LookupParameter('Comments').Set(pipe_comments)
                            upper_pipe_z = pipe.LookupParameter('Middle Elevation').AsDouble()
                            upper_pipe_z  = upper_pipe_z + 1450/304.8
                            copied_pipe.LookupParameter('Middle Elevation').Set(upper_pipe_z)
                            copied_pipe.LookupParameter('HasSprinkler').Set(True)
                            copied_pipe.LookupParameter('RelatedCeilingHeight').Set(related_ceiling_height)
                            copied_pipe.LookupParameter('IsUpperPipe').Set(True)
                            #copied_pipe.LookupParameter('OrganizedPipe').Set(True)                          
                        else:
                            pass
                        #create new sprinkler in type "Pendent Sprinkler" on the same location
                        #symbol name of the new sprinkler is "Pendent Sprinkler"
                        symbols = [x for x in FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements() if x.Name == 'Pendent Sprinkler']
                        symbol = symbols[0] if symbols else None
                        #activate symbol if not
                        if not symbol.IsActive:
                            symbol.Activate()
                        
                        new_pendent_sprinkler = doc.Create.NewFamilyInstance(XYZ(x, y, z), symbol, level, Structure.StructuralType.NonStructural)
                        #create a new pipe from the new sprinkler to 100mm above the sprinkler
                        #get sprinkler's connector location
                        
                        connector_location =  new_pendent_sprinkler.Location.Point

                        vertical_pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, connector_location, XYZ(x,y,connector_location.Z + 350/304.8))
                        vertical_pipe.LookupParameter('Diameter').Set(25/304.8)
                        vertical_pipe.LookupParameter('Comments').Set(pipe_comments)
                        vertical_pipe.LookupParameter('HasSprinkler').Set(True)
                        vertical_pipe.LookupParameter('RelatedCeilingHeight').Set(related_ceiling_height)
                        vertical_pipe.LookupParameter('IsHorizontal').Set(False)
                        #create Upright Sprinklers                        
                        symbols = [x for x in FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements() if x.Name == 'Upright Sprinkler']
                        symbol = symbols[0] if symbols else None
                        z = z + 1900/304.8
                        if not symbol.IsActive:
                            symbol.Activate()
                        new_upright_sprinkler = doc.Create.NewFamilyInstance(XYZ(x, y, z), symbol, level, Structure.StructuralType.NonStructural)
                        
                        
                        connector_location =  new_upright_sprinkler.Location.Point

                        vertical_pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, connector_location, XYZ(x,y,connector_location.Z + 350/304.8))
                        vertical_pipe.LookupParameter('Diameter').Set(25/304.8)
                        vertical_pipe.LookupParameter('Comments').Set(pipe_comments)
                        vertical_pipe.LookupParameter('HasSprinkler').Set(True)
                        vertical_pipe.LookupParameter('RelatedCeilingHeight').Set(related_ceiling_height)
                        vertical_pipe.LookupParameter('IsHorizontal').Set(False)
                    elif isOrganized == 0 and sprinkler_level.Id == level_id and sprinkler.Name == "SPRA003":
                        #change the Middle Elevation of pipe as the Z coordinate of the sprinkler + 350mm in feet
                        pipe.LookupParameter('Middle Elevation').Set(z + 350/304.8)
                        copied = pipe.LookupParameter('CopiedPipe').AsInteger()
                        pipe.LookupParameter('HasSprinkler').Set(True)
                        pipe.LookupParameter('RelatedCeilingHeight').Set(related_ceiling_height)
                        pipe.LookupParameter('IsUpperPipe').Set(False)
                        sprinkler.LookupParameter('isOrganized').Set(True)
                        #pipe.LookupParameter('OrganizedPipe').Set(True)                   

                        #create new sprinkler in type "Pendent Sprinkler" on the same location
                        #symbol name of the new sprinkler is "Pendent Sprinkler"
                        symbols = [x for x in FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements() if x.Name == 'Pendent Sprinkler']
                        symbol = symbols[0] if symbols else None
                        if not symbol.IsActive:
                            symbol.Activate()
                            
                        new_pendent_sprinkler = doc.Create.NewFamilyInstance(XYZ(x, y, z), symbol, level, Structure.StructuralType.NonStructural)
                        
                        connector_location = new_pendent_sprinkler.Location.Point

                        vertical_pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, connector_location, XYZ(x,y,connector_location.Z + 350/304.8))
                        vertical_pipe.LookupParameter('Diameter').Set(25/304.8)
                        vertical_pipe.LookupParameter('Comments').Set(pipe_comments)
                        vertical_pipe.LookupParameter('HasSprinkler').Set(True)
                        vertical_pipe.LookupParameter('RelatedCeilingHeight').Set(related_ceiling_height)
                        vertical_pipe.LookupParameter('IsHorizontal').Set(False)
                    else:
                        if sprinkler.Name != "SPRA006" and sprinkler.Name != "SPRA003":
                            print(f"Sprinkler {sprinkler.Name} is not organized. Please check the sprinkler.")
                

def create_tagged_pipes_from_csv():

    # Read the CSV line files and create simple pipes
    with open(r'C:\ScriptCSV\FP\L05-Tags.csv', 'r') as lines_file:
        lines_reader = csv.DictReader(lines_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation

        # Create the pipes
        for row in lines_reader:            
            start = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, elevation)
            end = XYZ(float(row['EndX']) / 304.8, float(row['EndY']) / 304.8, elevation)
            start_check = XYZ(float(row['StartX']) / 304.8, float(row['StartY']) / 304.8, 0)
            end_check = XYZ(float(row['EndX']) / 304.8, float(row['EndY']) / 304.8, 0)
            
            system_name = row['SystemName']
            zone = row['ZONE']
            PipeSize = row['PipeSize']
            #remove the characters "DN" from the PipeSize
            PipeSize = PipeSize.replace("DN", "")
            #convert the PipeSize to integer
            PipeSize = int(PipeSize)
            critical = row['Critical']
            pipe_length= start.DistanceTo(end)
            if zone == zone_name and pipe_length > 250/304.8:
                if "Discharge" in system_name:
                    pipe_type_id = get_pipe_type_id("Fire-Discharge")
                    system_id = system_type_id_Sanitary
                elif "Dry" in system_name:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPDry
                elif "Action" in system_name:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPPreAction
                elif "Main" in system_name:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPMain
                else:
                    pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                    system_id = system_type_id_FPwet
                pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, start, end)
                pipe.LookupParameter('IsUpperPipe').Set(False)
                pipe.LookupParameter('IsHorizontal').Set(True)
                #set the Diameter parameter of the pipe as 25mm
                pipe.LookupParameter('Diameter').Set(PipeSize/304.8)
                #read SystemName row of the csv file and write it to comments of the pipe
                pipe.LookupParameter('Comments').Set(system_name)
                pipe.LookupParameter('isCritical').Set(critical)
                pipe.LookupParameter('HasSprinkler').Set(False)
                    
                sprinklers = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sprinklers).WhereElementIsNotElementType().ToElements()

                for sprinkler in sprinklers:
                    #get the level of the sprinkler
                    sprinkler_level = doc.GetElement(sprinkler.LevelId)
                    if sprinkler_level.Id == level_id and "SPRA" in sprinkler.Name:
                        #get the location of the sprinkler
                        location = sprinkler.Location
                        #get the location point of the sprinkler
                        location_point = location.Point
                        #get the location point x and y coordinates
                        x = location_point.X
                        y = location_point.Y
                        z = sprinkler.LookupParameter('Elevation from Level').AsDouble()
                        related_ceiling_height = z
                        #create a new point variable named check_location only with X and Y, Z = 0 
                        check_location = XYZ(x, y, 0)
                        min_distance = 150/304.8
                        if start_check.DistanceTo(check_location) < min_distance or end_check.DistanceTo(check_location) < min_distance:
                            extra_pipes_to_delete.append(pipe.Id)
                            continue

                            

def organize_sprinkler_line_pipes():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()

    # Check the pipe if its pipe system parameters has sprinkler and it has sprinkler parameters is not true
    for pipe in pipes:    
        pipe_level = doc.GetElement(pipe.LevelId)
        pipe_system = pipe.LookupParameter('Comments').AsString()
        has_sprinkler = pipe.LookupParameter('HasSprinkler').AsInteger()
            
        #check if pipe has "Sprinkler" in its pipe_system parameter and HasSprinkler parameter is not true
        if pipe_level.Id == level_id and 'Sprinkler' in pipe_system and has_sprinkler != 1:
            for branch_pipe in pipes:
                branch_pipe_level = doc.GetElement(branch_pipe.LevelId)
                branch_pipe_system = branch_pipe.LookupParameter('Comments').AsString()
                branch_pipe_has_sprinkler = branch_pipe.LookupParameter('HasSprinkler').AsInteger()
                branch_pipe_is_upper_pipe = branch_pipe.LookupParameter('IsUpperPipe').AsInteger()
                branch_pipe_is_horizontal = branch_pipe.LookupParameter('IsHorizontal').AsInteger()
                #check if branch_pipe is same level and its pipe_system parameter is the same with the pipe_system parameter
                if branch_pipe_level.Id == level_id and branch_pipe_system == pipe_system and branch_pipe_has_sprinkler == 1 and branch_pipe_is_upper_pipe != 1 and branch_pipe_is_horizontal == 1:
                    #set middle elevation of the pipe as 205mm above relatedceilingheight parameter of branch_pipe
                    Host_pipe_elev = branch_pipe.LookupParameter('RelatedCeilingHeight').AsDouble()+205/304.8
                    branch_pipe_elev = branch_pipe.LookupParameter('Middle Elevation').AsDouble()           
                    pipe.LookupParameter('Middle Elevation').Set(Host_pipe_elev)
                    #get the intersection point of the pipe and branch_pipe in X and Y only
                    start = pipe.Location.Curve.GetEndPoint(0)
                    end = pipe.Location.Curve.GetEndPoint(1)
                    branch_pipe_start = branch_pipe.Location.Curve.GetEndPoint(0)
                    branch_pipe_end = branch_pipe.Location.Curve.GetEndPoint(1)
                    #revise the start and end points of the pipe as their Z coordinates are 0
                    start = XYZ(start.X, start.Y, Host_pipe_elev)
                    end = XYZ(end.X, end.Y, Host_pipe_elev)
                    branch_pipe_start = XYZ(branch_pipe_start.X, branch_pipe_start.Y, Host_pipe_elev)
                    branch_pipe_end = XYZ(branch_pipe_end.X, branch_pipe_end.Y, Host_pipe_elev)
                    #create a new line with the start and end points of the pipe
                    pipe_line = Line.CreateBound(start, end)
                    branch_pipe_line = Line.CreateBound(branch_pipe_start, branch_pipe_end)
                    #get the intersection point of the pipe and branch_pipe

                    isIntersecting = pipe_line.Intersect(branch_pipe_line)                    
                    if isIntersecting == SetComparisonResult.Overlap:
                        intersection_points = get_curve_intersection(pipe_line, branch_pipe_line)
                        #create a new pipe from the intersection point to 1500mm above the intersection point
                        if intersection_points:
                            intersection_point = intersection_points[0]
                            #substitude the elevation of level from the Z coordinate of the intersection point
                            intersection_point = XYZ(intersection_point.X, intersection_point.Y, Host_pipe_elev)
                            #print intersection point as mm                       

                            pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
                            vertical_pipe = Pipe.Create(doc, system_type_id_FPwet, pipe_type_id, level_id, intersection_point, XYZ(intersection_point.X, intersection_point.Y, branch_pipe_elev))

                            vertical_pipe.LookupParameter('Diameter').Set(25/304.8)
                            vertical_pipe.LookupParameter('Comments').Set(pipe_system)
                            vertical_pipe.LookupParameter('HasSprinkler').Set(True)                        
                            vertical_pipe.LookupParameter('IsHorizontal').Set(False)

# Function to get ceiling element from linked models
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
                                        elem.LookupParameter('RelatedCeilingHeight').Set(height_offset)
                                        elem.LookupParameter('CMS_HeightFound').Set(True)
                                        break
                                        
                                    else:
                                        continue
    return None        



def get_related_ceiling_height(pipe):
    start = pipe.Location.Curve.GetEndPoint(0)
    end = pipe.Location.Curve.GetEndPoint(1)
    start_top = XYZ(start.X, start.Y, start.Z + 5000/304.8)
    end_top = XYZ(end.X, end.Y, end.Z + 5000/304.8)
         

    line1 = Line.CreateBound(start, start_top)
    line2 = Line.CreateBound(end, end_top)     
        
    get_ceiling_from_link(doc, line1, pipe)
    
    heightfound = pipe.LookupParameter('CMS_HeightFound').AsInteger()

    if heightfound != 1:
        get_ceiling_from_link(doc, line2, pipe)

    heightfound = pipe.LookupParameter('CMS_HeightFound').AsInteger()    
    if heightfound != 1:
        pipe.LookupParameter('RelatedCeilingHeight').Set(2700/304.8)
        pipe.LookupParameter('CMS_HeightFound').Set(True)


def organize_main_lines():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    for pipe in pipes:
        pipe_level = doc.GetElement(pipe.LevelId)
        pipe_system = pipe.LookupParameter('Comments').AsString()
        has_sprinkler = pipe.LookupParameter('HasSprinkler').AsInteger()
        if "Main" in pipe_system and pipe_level.Id == level_id and has_sprinkler != 1:
            start = pipe.Location.Curve.GetEndPoint(0)
            end = pipe.Location.Curve.GetEndPoint(1)
            pipe_line = Line.CreateBound(start, end)
            #get middle point of pipe line
            location = pipe_line.Evaluate(0.5, True)
            end_point = XYZ(location.X, location.Y, location.Z + 3500/304.8)# Create a line between the location point and the new point
            line = Line.CreateBound(location, end_point)
            get_related_ceiling_height(pipe)
            MiddleElev = pipe.LookupParameter('RelatedCeilingHeight').AsDouble() + 205/304.8
            pipe.LookupParameter('Middle Elevation').Set(MiddleElev)

        elif "Action" in pipe_system and pipe_level.Id == level_id and has_sprinkler != 1:
            start = pipe.Location.Curve.GetEndPoint(0)
            end = pipe.Location.Curve.GetEndPoint(1)
            pipe_line = Line.CreateBound(start, end)
            #get middle point of pipe line
            location = pipe_line.Evaluate(0.5, True)
            end_point = XYZ(location.X, location.Y, location.Z + 3500/304.8)# Create a line between the location point and the new point
            line = Line.CreateBound(location, end_point)
            get_related_ceiling_height(pipe)
            MiddleElev = pipe.LookupParameter('RelatedCeilingHeight').AsDouble() + 205/304.8
            pipe.LookupParameter('Middle Elevation').Set(MiddleElev)

        elif "Discharge" in pipe_system and pipe_level.Id == level_id and has_sprinkler != 1:
            start = pipe.Location.Curve.GetEndPoint(0)
            end = pipe.Location.Curve.GetEndPoint(1)
            pipe_line = Line.CreateBound(start, end)
            #get middle point of pipe line
            location = pipe_line.Evaluate(0.5, True)
            end_point = XYZ(location.X, location.Y, location.Z + 3500/304.8)# Create a line between the location point and the new point
            line = Line.CreateBound(location, end_point)
            get_related_ceiling_height(pipe)
            MiddleElev = pipe.LookupParameter('RelatedCeilingHeight').AsDouble() + 325/304.8
            pipe.LookupParameter('Middle Elevation').Set(MiddleElev)

        elif "Sprinkler" in pipe_system and pipe_level.Id == level_id and has_sprinkler != 1:
            start = pipe.Location.Curve.GetEndPoint(0)
            end = pipe.Location.Curve.GetEndPoint(1)
            pipe_line = Line.CreateBound(start, end)
            #get middle point of pipe line
            location = pipe_line.Evaluate(0.5, True)
            end_point = XYZ(location.X, location.Y, location.Z + 3500/304.8)# Create a line between the location point and the new point
            line = Line.CreateBound(location, end_point)
            get_related_ceiling_height(pipe)
            MiddleElev = pipe.LookupParameter('RelatedCeilingHeight').AsDouble() + 205/304.8
            pipe.LookupParameter('Middle Elevation').Set(MiddleElev)
        

def create_column_pipes_from_csv():
        # Read the CSV line files and create simple pipes
    with open(r'C:\ScriptCSV\FP\L05-risers.csv', 'r') as lines_file:
        lines_reader = csv.DictReader(lines_file)    
        #get elevation of the level
        level = doc.GetElement(level_id)
        elevation = level.Elevation

        # Create the pipes
        for row in lines_reader:            
            start = XYZ(float(row['pX']) / 304.8, float(row['pY']) / 304.8, elevation)
            end = XYZ(float(row['pX']) / 304.8, float(row['pY']) / 304.8, elevation+5000/304.8)            

            zone = row['ZONE']
            PipeSize = row['PSize']
            
            PipeSize = int(PipeSize)
       
            pipe_type_id = get_pipe_type_id("Pipe-Fire-Sprinkler")
            system_id = system_type_id_FPwet
            pipe = Pipe.Create(doc, system_id, pipe_type_id, level_id, start, end)
            pipe.LookupParameter('IsUpperPipe').Set(False)
            pipe.LookupParameter('IsHorizontal').Set(False)
                
            pipe.LookupParameter('Diameter').Set(PipeSize/304.8)
            pipe.LookupParameter('HasSprinkler').Set(False)
            pipe.LookupParameter('Comments').Set("Riser")
    





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



def check_horizontal():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    for pipe in pipes:        
        start = pipe.Location.Curve.GetEndPoint(0)
        end = pipe.Location.Curve.GetEndPoint(1)
        start = XYZ(start.X, start.Y, 0)
        end = XYZ(end.X, end.Y, 0)        
        if start.X == end.X and start.Y == end.Y:
            pipe.LookupParameter('IsHorizontal').Set(False)
        else:
            pipe.LookupParameter('IsHorizontal').Set(True)


#from concurrent.futures import ThreadPoolExecutor, as_completed
#import rtree

def get_pipelength_put_on_comments():
    pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().ToElements()
    for pipe in pipes:
        length = pipe.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
        pipe.LookupParameter('Comments').Set(f"Length: {length}")

t = Transaction(doc, "Delete existing pipes and fittings")
t.Start()
delete_existing_pipes_and_fittings()
t.Commit()

t = Transaction(doc, "Create sprinkler pipes from CSV")
t.Start()

reset_organized_sprinklers()
create_sprinkler_pipes_from_csv()
t.Commit()

tr_delete_duplicate_elements()


t = Transaction(doc, "ORGANİZE SPRİNKLER")
t.Start()

organize_sprinkler_pipes()
#organize_sprinkler_line_pipes()

t.Commit()

#tr_delete_pipes_to_delete()

"""
t = Transaction(doc, "Create Other Lines")
t.Start()

create_tagged_pipes_from_csv()
create_column_pipes_from_csv()
organize_main_lines()

t.Commit()

tr_delete_extra_pipes()
"""