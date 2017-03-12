# This script uploads a mission to the interop server. First it prompts the user for configuration
# files explorted from mission planner and parses those files (only certain file formats work - ask
# Ethan if you are having trouble). Then it imports the django environment and creates a new
# instance of the MissionConfig model and any other models necessary. Note that this script 
# needs to be run from within the docker container.


import sys
import os


def main():

	# Print some info for the user
	print "\nMAKE SURE YOU ARE RUNNING THIS SCRIPT WITHIN THE INTEROP DOCKER CONTAINER\n"
	print "My job is to upload a mission to the interop server. You need to provide me with certain" \
		" files exported from Mission Planner for me to be able to do that. A .waypoints file" \
		" is required and any other files are optional."
	
	mission_waypoints = []   # Data parsed from .waypoints file will be appended here
	boundary_vertices = []   # Data parsed from .poly file will be appended here


	promptForFilesAndParse(mission_waypoints, boundary_vertices)

	uploadMission(mission_waypoints, boundary_vertices)

# Prompt the user for the configuration files exported from mission planner and parse them
def promptForFilesAndParse(mission_waypoints, boundary_vertices): 
	files_provided = [False, False]
	while True:
		# print directions
		print "\n-----------------------------------------------------------------------------\n"
		if files_provided[0] == False:
			print "To select a .waypoints file (required): type '0' and hit enter."
		if files_provided[1] == False:
			print "To select a .poly file (optional):      type '1' and hit enter."
		print "To continue to the upload:              type '8' and hit enter."
		print "To cancel:                              type '9' and hit enter."
	
		# read the user input and act upon it
		user_choice = raw_input("\nType your choice here: ")
		print ""
		if user_choice == '0':    # User wants to provide a .waypoints file
			if files_provided[0] == True:  # User already provided a .waypoints file
				sys.stderr.write("You've already provided a .waypoints file. You can't do it again.\n")
				continue
			parsed = askForAndParseWaypointsFile(mission_waypoints)
			if parsed == True:
				files_provided[0] = True
			continue
		elif user_choice == '1':  # User wants to provide a .poly file
			if files_provided[1] == True:  # User already provided a .poly file
				sys.stderr.write("You've already provided a .poly file. You can't do it again.\n")
				continue
			parsed = askForAndParsePolyFile(boundary_vertices)
			if parsed == True:
				files_provided[1] = True
			continue
		elif user_choice == '8':  # User wants to continue to upload
			if files_provided[0] == False:
				sys.stderr.write("Can't continue to upload until you provide a .waypoints file.\n")
				continue
			break
		elif user_choice == '9':  # User wants to cancel
			print "Cancelling and exiting program."
			sys.exit()	
		else:                     # User input is bad
			sys.stderr.write("I didn't understand your input, please try again.\n")


# Ask for .waypoints file, parse it, and append data to mission_waypoints
def askForAndParseWaypointsFile(mission_waypoints):

	lines = None   # file contents will later be extracted to this variable

	# Prompt user for a filename, keep prompting until file exists, has the correct extension, and has at least 3 lines
	filename_valid = False
	while filename_valid == False:
		input = raw_input("\nType .waypoints filepath here or type '9' to go back: ")
		if input == '9':    # User wants to go back
			return False
		filename = input
		if os.path.isfile(filename) == False:
			sys.stderr.write("The filename you inputted, " + filename + ", does not exist. Please try again.\n")
			continue
		extension = os.path.splitext(filename)[1]
		if extension != ".waypoints":
			sys.stderr.write("The filename you inputted, " + filename + ", does not have the .waypoints extension. Please try again.\n")
			continue
		f = open(filename, 'r')
		lines = f.read().splitlines() # extract file contents into an array
		f.close()
		if len(lines) < 3:
			sys.stderr.write("The file you provided, " + filename + ", does not have at least 3 lines. Please try again.\n")
			continue
		filename_valid = True

	# Attempt to parse the file contents
	print "\nAttempting to parse " + filename + "..."
	line_index = 2
	try:
		while line_index < len(lines): # Parse each line one-by-one, but skip the 1st 2 lines (because they store metadata, not data)
			line = lines[line_index]
			line_split = line.split("\t")
			if len(line_split) != 12:
				sys.stderr.write("\nError2 - Unable to parse line " + str(line_index+1) +". Please report this error to Ethan. Exiting...\n")
				sys.exit(1)
			long = float(line_split[8])
			lat = float(line_split[9])
			alt = float(line_split[10])
			mission_waypoints.append([long, lat, alt])
			line_index += 1
	except Exception:
		sys.stderr.write("\nError - Unable to parse line " + str(line_index+1) + ". Please report this error to Ethan. Exiting...\n")
		sys.exit(1)

	# Let the user know that the parsing was succesful and print the extracted data
	print "\nParsing Success"
	for i in range(len(mission_waypoints)):
		long, lat, alt = mission_waypoints[i]
		print "Waypoint " + str(i+1) + ": [long: " + str(long) + ", lat: " + str(lat) + ", alt: " + str(alt) + "]"
	return True



# Ask for .poly file, parse it, and append data to boundary_vertices
def askForAndParsePolyFile(boundary_vertices):
	
	lines = None   # file contents will later be extracted to this variable

	# Prompt user for a filename, keep prompting until file exists, has the correct extension, and has at least 2 lines
        filename_valid = False
        while filename_valid == False:
		input = raw_input("\nType .poly filepath here or type '9' to go back: ")
		if input == '9':    # User wants to go back
			return False
		filename = input
                if os.path.isfile(filename) == False:
                        sys.stderr.write("The filename you inputted, " + filename + ", does not exist. Please try again.\n")
                        continue
		extension = os.path.splitext(filename)[1]
                if extension != ".poly":
                        sys.stderr.write("The filename you inputted, " + filename + ", does not have the .poly extension. Please try again.\n")
                        continue
		f = open(filename, 'r')
		lines = f.read().splitlines() # extract file contents into an array
		f.close()
		if len(lines) < 2:
			sys.stderr.write("The file you provided, " + filename + ", does not have at least 2 lines. Please try again.\n")
			continue
                filename_valid = True

	# Attempt to parse the file contents
	print "\nAttempting to parse " + filename + "..."
	line_index = 1
	try:
		while line_index < len(lines): # Parse each line one-by-one, but skip the 1st line (because the 1st line is a comment le$
			line = lines[line_index]
			line_split = line.split(" ")
			if len(line_split) != 2:
				sys.stderr.write("\nError2 - Unable to parse line " + str(line_index+1) +". Please report this error to Ethan. Exiting...\n")
				sys.exit(1)
			long = float(line_split[0])
			lat = float(line_split[1])
			boundary_vertices.append([long, lat])
			line_index += 1
	except Exception:
		sys.stderr.write("\nError - Unable to parse line " + str(line_index+1) + ". Please report this error to Ethan. Exiting...\n")
		sys.exit(1)
	
	# Let the user know that the parsing was succesful and print the extracted data
	print "\nParsing Success"
	for i in range(len(boundary_vertices)):
		long, lat = boundary_vertices[i]
		print "Vertex " + str(i+1) + ": [long: " + str(long) + ", lat: " + str(lat) + "]"
	return True


def uploadMission(mission_waypoints, boundary_vertices):

	# Infiltrte django environment, need to be within docker container for these lines of code to work
	print "\nInfiltrating django environment, if this script fails here, you are running it wrong...\n"
	sys.path.append('/interop/server')
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
	from django.core.wsgi import get_wsgi_application
	application = get_wsgi_application()
	from auvsi_suas.models.gps_position import GpsPosition
	from auvsi_suas.models.aerial_position import AerialPosition
	from auvsi_suas.models.waypoint import Waypoint
	from auvsi_suas.models.fly_zone import FlyZone
	from auvsi_suas.models.mission_config import MissionConfig


	print "\nUploading mission...\n"

	# upload all the data from the mission_waypoints list
	mission_waypoint_objects = []
	for i in range(len(mission_waypoints)):
		long, lat, alt = mission_waypoints[i]
		gps_position = GpsPosition(longitude=long, latitude=lat)
		gps_position.save()
		aerial_position = AerialPosition(gps_position=gps_position, altitude_msl=alt)
		aerial_position.save()
		mission_waypoint_obj = Waypoint(position=aerial_position, order=i+1)
		mission_waypoint_obj.save()
		mission_waypoint_objects.append(mission_waypoint_obj)

	# upload all the data from the boundary_vertices list (note that the same models are used as for mission_waypoints, dont get confused) 
	boundary_waypoint_objects = []
	for i in range(len(boundary_vertices)):
		long, lat = boundary_vertices[i]
		gps_position = GpsPosition(longitude=long, latitude=lat)
		gps_position.save()
		alt = 425   # Setting the altitude to 425 for every boundary waypoint due to lack of better thing to do. Should be ok though, because according to rule book, plane should be between 100ft-750ft at all times.
		aerial_position = AerialPosition(gps_position=gps_position, altitude_msl=alt)
		aerial_position.save()
		boundary_waypoint_obj = Waypoint(position=aerial_position, order=i+1)
		boundary_waypoint_obj.save()
		boundary_waypoint_objects.append(boundary_waypoint_obj)


	# Use the boundary_waypoint_objects list to create a FlyZone instance
	alt_min = 100   # Based on the rulebook
	alt_max = 750   # Based on the rulebook
	fly_zone = FlyZone(altitude_msl_min=alt_min, altitude_msl_max=alt_max)
	fly_zone.save()
	for boundary_waypoint_object in boundary_waypoint_objects:
		fly_zone.boundary_pts.add(boundary_waypoint_object)



	# Finally, create a MissionConfig instance

	# Need to assign the following values because they are required in the MissionConfig constructor
	home_pos = mission_waypoint_objects[0].position.gps_position   # set the home position to the 1st waypoint (makes sense to do this)
	emergent_last_known_pos = mission_waypoint_objects[0].position.gps_position   # set this value to the 1st waypoint as a placeholder (doesn't really make sense to do this, need to change this in the future)
	off_axis_target_pos = mission_waypoint_objects[0].position.gps_position   # set this value to the 1st waypoint as a placeholder (doesn't make sense to do this, need to change in the future)
	air_drop_pos = mission_waypoint_objects[0].position.gps_position   # set this value to the 1st waypoint as a placeholder (doesn't make sense to do this, need to change in the future)
	
	mission = MissionConfig(is_active=True, 
                        home_pos=home_pos,
                        emergent_last_known_pos=emergent_last_known_pos,
                        off_axis_target_pos=off_axis_target_pos,
                        air_drop_pos=air_drop_pos)
	mission.save()
	# Add the fly zone instance to the mission instance
	mission.fly_zones.add(fly_zone)
	# Add the mission waypoints to the mission instance
	for mission_waypoint_object in mission_waypoint_objects:
		mission.mission_waypoints.add(mission_waypoint_object)
	# Use the boundary points as seach grid points as well and add them to the mission instance
	for boundary_waypoint_object in boundary_waypoint_objects:
		mission.search_grid_points.add(boundary_waypoint_object)

	
	# As of now, this script does not have the ability to add obstacles to the mission. This needs to change in the future.


	print "\nUpload Success! You should now visit http://127.0.0.1:8000/admin/auvsi_suas/ in your browser to make sure that everything got uploaded correctly.\n"
	
if __name__ == "__main__":
	main()
