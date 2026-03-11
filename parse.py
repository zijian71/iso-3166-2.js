import csv
import glob
import json
import os
import re


# countries and their subdivisions — read from country/*.csv files
countries = {}
deprecated_codes = set()

# Read deprecated codes first
for dep_file in sorted(glob.glob("country/*.deprecated.csv")):
    with open(dep_file, "r", encoding="utf-8") as f:
        for line in f:
            code = line.strip()
            if code:
                deprecated_codes.add(code)

# Read all country CSV files (skip *.deprecated.csv)
for csv_file in sorted(glob.glob("country/*.csv")):
    if csv_file.endswith(".deprecated.csv"):
        continue
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            country_name = row[0].strip()
            subdivision_code = row[1].strip()
            subdivision_name = re.sub(r"\[.*\]", "", row[2]).strip()
            subdivision_type = row[3].strip()
            country_code = row[4].strip()

            if country_code not in countries:
                countries[country_code] = {"name": country_name, "sub": {}}

            entry = {
                "name": subdivision_name,
                "type": subdivision_type
            }

            if subdivision_code in deprecated_codes:
                entry["isDeprecated"] = True

            countries[country_code]["sub"][subdivision_code] = entry

subdivisions = sum(len(countries[cc]["sub"]) for cc in countries)
deprecated_count = sum(
    1
    for cc in countries
    for code in countries[cc]["sub"]
    if countries[cc]["sub"][code].get("isDeprecated")
)

print("Countries: %d, Subdivisions: %d (deprecated: %d)" % (
    len(countries), subdivisions, deprecated_count
))

with open("data.js", "w", encoding="utf-8") as json_file:
    print("Dumping subdivisions to data.js")
    json_file.write("var data = ")
    json.dump(countries, json_file, ensure_ascii=False, separators=(",", ":"))
    json_file.write(";")


# alpha-3 to alpha-2 country code conversions
with open("codes.csv", "r", encoding="utf-8") as csv_file:
    codes = {}
    reader = csv.reader(csv_file)
    for row in reader:
        alpha2 = row[0]
        alpha3 = row[1]
        codes[alpha3] = alpha2

    print("Country codes: %d" % len(codes))

    with open("data.js", "a", encoding="utf-8") as json_file:
        print("Dumping codes to data.js")
        json_file.write("var codes = ")
        json.dump(codes, json_file, ensure_ascii=False, separators=(",", ":"))
        json_file.write(";")
