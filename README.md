# Interop
interoperability client programs

[Interop Docs](https://auvsi-suas-competition-interoperability-system.readthedocs.org/en/latest/integration/hints.html)


### Contains:
	- libinterop (library for utilizing interop clients)
	- Telemetry Interoperability client
	- SDA obstacles Interoperability client
	- Load Mission Interoperability client

###TO-DO list:
	- [ ] mission.py current fetches the mission details from the interop server in "Mission" object format (see libinterop/types.py-> Mission). However, Mission contains multiple "sub-object" fields that need to be parsed out and added to the current Mission (i.e. Mavproxy). Thus the mission.py needs to be edited to include dronekit and load the mission details into Mavproxy (mission_waypoints,search_area...). 

###About TO-DO list:
	please feel free to make any edits or solve any problems on the to-do lists. please first fork and make a Pull-request with the issue resolved.

