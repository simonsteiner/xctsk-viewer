# XCTSK Viewer

A viewer for paragliding competition tasks in the XCTrack task format, with an optional airspace overlay on the task map.

## Tasks

**Task**:
The route a pilot must fly in one competition round: an ordered list of turnpoints plus start, end-of-speed-section and goal rules.
_Avoid_: Route, course

**XCTSK file**:
A task in XCTrack's JSON task format, stored as a `.xctsk` file.
_Avoid_: Task file, xctask

**Task code**:
The short code under which xcontest's task-sharing service publishes a task.
_Avoid_: Task ID, task key

**Task type**:
Whether a task is a classic task flown through ordered turnpoints (`CLASSIC`) or a waypoints-only task (`W`).

**Turnpoint**:
A cylinder of a given radius around a waypoint that the pilot must reach, in order.
_Avoid_: Waypoint (a waypoint is only the named location a turnpoint is centred on)

**Takeoff**:
The first turnpoint, where the takeoff window opens and closes.

**SSS (start of speed section)**:
The turnpoint where timing starts, either as a race to goal (`RACE`) or elapsed-time (`ELAPSED-TIME`), opened by its start gates.
_Avoid_: Start

**ESS (end of speed section)**:
The turnpoint where timing stops.

**Goal**:
The last turnpoint, either a cylinder or a line; a task without an explicit goal has a cylinder goal.

**Center distance**:
Task length measured through the centres of all turnpoints.

**Optimized distance**:
The shortest flyable task length, touching each turnpoint cylinder at its nearest edge.
_Avoid_: Shortest distance

**Earth model**:
The model distances are computed on: `WGS84` ellipsoid or `FAI_SPHERE`.

## Airspace

**Airspace**:
A named volume of controlled or restricted airspace with a class, lower and upper limits and a lateral boundary.

**Airspace class**:
The category of an airspace (A–E, CTR, Restricted, Danger, Prohibited, …) that determines its colour on the map.

**OpenAir**:
The plain-text format airspace files are written in.

**Airspace dataset**:
The single set of airspaces currently shown on the overlay, from the default Swiss file, an uploaded OpenAir file or the COMP CH layer.
_Avoid_: Airspace file, layer

**COMP CH**:
xcontest's Swiss competition airspace layer, fetched live.
