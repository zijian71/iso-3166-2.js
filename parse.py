import csv
import json
import re


# countries and their subdivisions.
with open("data.csv", "r", encoding="utf-8") as csv_file:
    countries = {}
    reader = csv.reader(csv_file)
    for row in reader:
        country_name = row[0]
        subdivision_code = row[1]
        subdivision_name = re.sub(r"\[.*\]", "", row[2])
        type = row[3]
        country_code = row[4]
        if country_code not in countries:
            countries[country_code] = {"name": country_name.strip(), "sub": {}}
        countries[country_code]["sub"][subdivision_code] = {
            "name": subdivision_name.strip(),
            "type": type.strip()
        }
    subdivisions = sum(len(countries[cc]["sub"]) for cc in countries)

    print("Countries: %d, Subdivisions: %d" % (
        len(countries.keys()), subdivisions
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

    print("Country codes: %d" % len(codes.keys()))

    with open("data.js", "a", encoding="utf-8") as json_file:
        print("Dumping codes to data.js")
        json_file.write("var codes = ")
        json.dump(codes, json_file, ensure_ascii=False, separators=(",", ":"))
        json_file.write(";")
