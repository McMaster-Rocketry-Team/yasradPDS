# loads defaults.json and exposes default values. 
# unlike constants.py, this should be used for constants which might change based on
# our source (material properites, safety factors, drag coefficients, etc.).



POINTS_PER_METER = 1181
# target density of points along a gore outline, in points per metre of curve length.
# 800-2000 is the goal (roughly 20-50 per inch); 1181 is about 30 per inch.




SEMI_ELIPSOID_CD = 1.6
#industry standard for semi-ellipsoid drag coefficient, used for drogue and main parachutes.

FILE_PATH : str = ""