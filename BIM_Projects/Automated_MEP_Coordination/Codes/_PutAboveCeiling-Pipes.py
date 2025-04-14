import csv

from Autodesk.Revit.DB import XYZ, Line, Transaction, BuiltInCategory, ElementId
from Autodesk.Revit.DB import Curve, Line, XYZ, IntersectionResultArray, SetComparisonResult
from Autodesk.Revit.DB.Plumbing import Pipe
from Autodesk.Revit.DB.Plumbing import PipeType
import System
from System import Array

import clr

clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


from Autodesk.Revit.DB import Transaction, MEPSystem, BuiltInCategory, FilteredElementCollector
from Autodesk.Revit.Exceptions import InvalidOperationException

from Autodesk.Revit.UI import TaskDialog



# Correct method to get the document based on your provided scripts
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# Get the selected elements
selection_ids = uidoc.Selection.GetElementIds()

# Global variable for the level name
level_name = "L01"
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
for level in levels:
    if level.Name == level_name:
        level_id = level.Id
        break



def put_ceilings_above():
    for pipe in pipes:
        #revise the pipe list to only pipes that have "2700" as 'RelatedCeilingHeight' parameter
        if pipe.LookupParameter('RelatedCeilingHeight').AsDouble() == 1600/304.8:
            get_related_ceiling_height(pipe)
            change_pipe_elevation(pipe)


def change_pipe_elevation(pipe):
    MiddleElev = pipe.LookupParameter('RelatedCeilingHeight').AsDouble() + 205/304.8
    pipe.LookupParameter('Middle Elevation').Set(MiddleElev)
    pipe.LookupParameter('CMS_HeightFound').Set(True)

def get_related_ceiling_height(pipe):
    start = pipe.Location.Curve.GetEndPoint(0)
    end = pipe.Location.Curve.GetEndPoint(1)
    start_bottom = XYZ(start.X, start.Y, start.Z - 1000 / 304.8)
    start_top = XYZ(start.X, start.Y, start.Z + 5000/304.8)
    end_top = XYZ(end.X, end.Y, end.Z + 5000/304.8)
    end_bottom = XYZ(end.X, end.Y, end.Z - 1000/304.8)
         

    line1 = Line.CreateBound(start_bottom, start_top)
    line2 = Line.CreateBound(end_bottom, end_top)     
        
    startceiling = get_ceiling_from_link(doc, line1, pipe)
    endceiling = get_ceiling_from_link(doc, line2, pipe)
    
    #select the heigher ceiling
    if startceiling is not None and endceiling is not None:
        if startceiling > endceiling:
            pipe.LookupParameter('RelatedCeilingHeight').Set(startceiling)
        else:
            pipe.LookupParameter('RelatedCeilingHeight').Set(endceiling)
    elif startceiling is not None:
        pipe.LookupParameter('RelatedCeilingHeight').Set(startceiling)
    elif endceiling is not None:
        pipe.LookupParameter('RelatedCeilingHeight').Set(endceiling)
    else:
        pipe.LookupParameter('CMS_HeightFound').Set(False)






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
                                        return height_offset
                                    else:
                                        continue
    return None




pipes = []

def create_pipes_list():
     if selection_ids.Count > 0:
        #create an empty list for pipes
        for selection_id in selection_ids:
            pipe = doc.GetElement(selection_id)
            pipes.append(pipe)
        

#create a function checking if only two pipes have common points in the pipe list, if yes, connect them with an elbow fitting

def align_pipesin_XY():
    pipeStartX = []
    pipeStartY = []
    pipeEndX = []
    pipeEndY = []
    for pipe in pipes:
        pipeCurve = pipe.Location.Curve
        pipeStart = pipeCurve.GetEndPoint(0)
        pipeEnd = pipeCurve.GetEndPoint(1)
        pipeStartX.append(pipeStart.X)
        pipeStartY.append(pipeStart.Y)
        pipeEndX.append(pipeEnd.X)
        pipeEndY.append(pipeEnd.Y)
    
    #get avarage of start and end points
    start_x = sum(pipeStartX) / len(pipeStartX)
    start_y = sum(pipeStartY) / len(pipeStartY)
    end_x = sum(pipeEndX) / len(pipeEndX)
    end_y = sum(pipeEndY) / len(pipeEndY)

    #modify pipe's start and end points to the avarage points
    for pipe in pipes:
        pipeCurve = pipe.Location.Curve
        pipeStart = pipeCurve.GetEndPoint(0)
        pipeEnd = pipeCurve.GetEndPoint(1)
        pipeStart = XYZ(start_x, start_y, pipeStart.Z)
        pipeEnd = XYZ(end_x, end_y, pipeEnd.Z)
        #move pipe connectors to the new points
        pipeCurve = Line.CreateBound(pipeStart, pipeEnd)
        pipe.Location.Curve = pipeCurve
        


t = Transaction(doc, "arrange  pipes")
t.Start()

create_pipes_list()
put_ceilings_above()

t.Commit()

