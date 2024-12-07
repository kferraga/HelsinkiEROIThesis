# Court and Fizaine' EROI constants. See sec X.X in thesis for a more detailed explanation.
# b = base, l = low, h = high, sf = scaling factor, in = initial normalized EROI with immature technology
# tl = technological learning rate, me = exploitation ratio for maximum growth rate/inflection point
# rd = resource degradation rate, URR = ultimately recoverable resources
# CITATION: Court, V., & Fizaine, F., 2017. Long-term estimates of the energy-return-on-investment (EROI) of coal, oil, and gas global productions. Ecological Economics, 138, pp. 145–159.

## Court and Fizaine General Information
valid_resources = ["coal", "oil", "gas"]
valid_prediction_types = ["l", "b", "h"]
base_year = 1800

## Court and Fizaine EROI Coal Constants
coal = {
    "delta": {"b": 0.022, "l": 0.024, "h": 0.021},
    "tlag": {"b": 333, "l": 323, "h": 343},
    "sf": 166.2530,
    "in": 0.0733,
    "tl": 70.4688,
    "me": 0.0471,
    "rd": 5.1135,
    "URR": 10500
}

## Court and Fizaine EROI Oil Constants
oil = {
    "delta": {"b": 0.03, "l": 0.04, "h": 0.024},
    "tlag": {"b": 250, "l": 240, "h": 260},
    "sf": 43.7869,
    "in": 0,
    "tl": 726.9201977,
    "me": 0.0004,
    "rd": 3.7793,
    "URR": 31000
}

## Court and Fizaine EROI Gas Constants
gas = {
    "delta": {"b": 0.037, "l": 0.058, "h": 0.027},
    "tlag": {"b": 238, "l": 228, "h": 248},
    "sf": 145.2906,
    "in": 0.1095,
    "tl": 805.8096137,
    "me": 0.0025,
    "rd": 4.9787,
    "URR": 27000
}
