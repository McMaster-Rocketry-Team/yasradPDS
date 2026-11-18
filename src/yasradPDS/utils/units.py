# unit conversion helpers so inputs and outputs can move between SI and imperial
def convert_ft_m(measurement_num: float, desired_unit: str) -> float:
    FT_M_RATIO = 0.3048
    if desired_unit == "m":
        return measurement_num * FT_M_RATIO
    elif desired_unit == "ft":
        return measurement_num * (1/FT_M_RATIO)
    else:
        raise Exception("Desired unit should be m or ft")
