# system objects hold knowns and unknowns
# they define what the variables are, and keep them all in 
# one place so that exports and analyses can be performed by
# passing just a single system object

from typing import Protocol, Any, Dict, Type

# interface
class System(Protocol):

    
# factory
def new_system(system_type: str):
