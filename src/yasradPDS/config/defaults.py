# loads defaults.json and exposes default values. 
# unlike constants.py, this should be used for constants which might change based on
# our source (material properites, safety factors, drag coefficients, etc.).



POINTS_PER_METER = 1181
# target density of points along a gore outline, in points per metre of curve length.
# 800-2000 is the goal (roughly 20-50 per inch); 1181 is about 30 per inch.




SEMI_ELIPSOID_CD0 = 1.55
# the baseline unvented drag coefficient CD0 is chosen as the median of industry-standard semi-ellipsoidal 
# parachute profiles, which empirically demonstrate steady-state drag coefficients between 1.5 and 1.6
# relative to projected inflated area (e.g., Fruity Chutes Classic Elliptical, Cd = 1.6; 
# Nakka Aerodynamic Studies, Cd = 1.5.