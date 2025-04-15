import csv
from Autodesk.Revit.DB import XYZ, FilteredElementCollector, BuiltInCategory
from Autodesk.Revit.DB import Line, Transaction, Wall


# Define the path to the CSV file
csv_file_path = r'E:\000_COMAS\55-KAZAKISTAN-RNS-HSTNE\01Wall-Automate\_Start20240220\Excel-CSV Files\Zon-5.csv'

# Get the current document
doc = __revit__.ActiveUIDocument.Document

# Get all wall types
wall_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()

# Get all levels
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

# Define a function to find a wall type by name
def find_wall_type(name, optional):
    if name == "GP":
        combined_name = f"GP-{optional}"
        for wall_type in wall_types:
            if wall_type.Name == combined_name:
                return wall_type
               
    elif name == "BGP":
        combined_name = f"BGP-{optional}"
        for wall_type in wall_types:
            if wall_type.Name == combined_name:
                return wall_type
                
    elif name == "ACX-BGP-":
        combined_name = f"ACX-BGP-{optional}"
        for wall_type in wall_types:
            if wall_type.Name == combined_name:
                return wall_type              
                
    elif name == "GPW1":
        combined_name = f"GPW1-{optional}"
        for wall_type in wall_types:
            if wall_type.Name == combined_name:
                return wall_type  
                
    elif name == "GPW2":
        combined_name = f"GPW2-{optional}"
        for wall_type in wall_types:
            if wall_type.Name == combined_name:
                return wall_type

    else:
        for wall_type in wall_types:
            if wall_type.Name == name:
                return wall_type               
                
    return None

# Define a function to find a level by name
def find_level(name):
    for level in levels:
        if level.Name == name:
            return level
    return None

# Create a list to store the wall data
walls_data = []

try:
    # Open the CSV file and create a csv.reader object
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        # Skip the header row
        next(reader)
        
        
        # Define the function to get the wall type width
        def get_wall_type_width(wall_type):
            return wall_type.Width
        
        # Loop through the rows in the CSV file
        for row in reader:
            if len(row) == 10:
                # Get the data from the row
                floor, zone, type, optional, start_x, start_y, end_x, end_y, height, offset = row
                # Find the wall type and level
                wall_type = find_wall_type(type, optional)
                level = find_level(floor)
                # Create the start and end points
                start = XYZ(float(start_x)/304.8, float(start_y)/304.8, 0)
                end = XYZ(float(end_x)/304.8, float(end_y)/304.8, 0)
                W_height = float(height)/304.8
                W_offset = float(offset)/304.8
                # Store the wall data in the list
                walls_data.append({
                    'wall_type': wall_type,
                    'level': level,
                    'start': start,
                    'end': end,
                    'height': W_height,
                    'offset': W_offset
                })
            else:
                print(f"Row has incorrect number of columns: {row}")
	
     

except FileNotFoundError:
    print(f"The file {csv_file_path} does not exist.")
except PermissionError:
    print(f"Permission denied when trying to open the file {csv_file_path}.")
    

# Start a new transaction
t = Transaction(doc, "Create Walls")
t.Start()

# Loop through the wall data
for wall_data in walls_data:
	# Print properties
    print(wall_data['wall_type'], wall_data['start'], wall_data['end'], wall_data['height'], wall_data['offset'])
	# Create a line from the start and end points
    start = wall_data['start']
    end = wall_data['end']
    geomLine = Line.CreateBound(start, end)

    # Determine the other parameters
    height = wall_data['height']
    offset = wall_data['offset']
    
    wall_type = wall_data['wall_type']
     
    if height<0 or height>3000:
    	height=2500
    
    # Create the wall
    wall = Wall.Create(doc, geomLine, wall_type.Id, wall_data['level'].Id, height, offset, True, True)

# Commit the transaction
t.Commit()


