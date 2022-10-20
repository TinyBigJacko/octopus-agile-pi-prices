from inky.auto import auto

##  -- Detect display type automatically
try:
    inky_display = auto(ask_user=False, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")


if (inky_display.WIDTH == 212):
    print ("low-res")
else:
    print("high-res")