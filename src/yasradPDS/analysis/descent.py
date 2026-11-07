# rocketpy assisted descent calculations (altitude/velocity-time sims) 
# and real opening shocks

import rocketpy as rp
from ..config import defaults



#Opening Shock Analysis
"""
Need -> Source: 
Velocity relative to air at opening time -> Rocketpy launch simulation
Density of air at deployment time -> Rocketpy -> Simulation
Drag Coefficient -> Determined Experimentally / Approximated 
Nominal Surface Area -> Obtained Via System
"""