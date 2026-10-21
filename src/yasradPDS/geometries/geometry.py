# geometry objects are a tool for system objects to produce geometry-specific outputs,
# they are only imported in system files, where they allow shared code to be used 
# irrespecitve of shape

from typing import Protocol, Any, Dict, Type

# interface
class Geometry(Protocol):


# factory
def new_geometry(system_type: str):
    