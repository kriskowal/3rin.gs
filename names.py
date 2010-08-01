
import csv

def names():
    entires = {}
    for line in csv.DictReader(open("names.csv")):
        entry = entires.setdefault(line["Canonical"], [])
        entry.append(dict(
            (key.decode("UTF-8"), value.decode("UTF-8"))
            for key, value in line.items()
            if value
        ))
    return entires
    
