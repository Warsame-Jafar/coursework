import math, random, re, time, sys, os
from collections import Counter
alphabet = list("abcdefghijklmnopqrstuvwxyz")


def polybius_standardize(message):
    message = message.replace(" ", "")
    coords, coord = [], ""
    for i, k in enumerate(message):
        if i % 2 == 0 and coord:
            coords.append(coord)
            coord = ""
        coord += k
    if coord:
        coords.append(coord)
    unique_coords = list(set(coords))   
    standardized = ""
    for i in coords:
        standardized += alphabet[unique_coords.index(i)]
    return standardized.upper()
