#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const UglifyJS = require("uglify-js");

// Simple CSV parser handling quoted fields
function parseCSVLine(line) {
  const row = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        field += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === "," && !inQuotes) {
      row.push(field);
      field = "";
    } else {
      field += ch;
    }
  }
  row.push(field);
  return row;
}

const countryDir = path.join(__dirname, "country");
const allFiles = fs.readdirSync(countryDir).sort();

// Read deprecated codes
const deprecatedCodes = new Set();
for (const file of allFiles) {
  if (!file.endsWith(".deprecated.csv")) continue;
  const lines = fs.readFileSync(path.join(countryDir, file), "utf8").split("\n");
  for (const line of lines) {
    const code = line.trim();
    if (code) deprecatedCodes.add(code);
  }
}

// Read country CSV files
const countries = {};
for (const file of allFiles) {
  if (!file.endsWith(".csv") || file.endsWith(".deprecated.csv")) continue;
  const lines = fs.readFileSync(path.join(countryDir, file), "utf8").split("\n");
  for (const line of lines) {
    if (!line.trim()) continue;
    const row = parseCSVLine(line);
    if (row.length < 5) continue;
    const countryName = row[0].trim();
    const subdivisionCode = row[1].trim();
    const subdivisionName = row[2].replace(/\[.*\]/g, "").trim();
    const subdivisionType = row[3].trim();
    const countryCode = row[4].trim();

    if (!countries[countryCode]) {
      countries[countryCode] = { name: countryName, sub: {} };
    }

    const entry = { name: subdivisionName, type: subdivisionType };
    if (deprecatedCodes.has(subdivisionCode)) {
      entry.isDeprecated = true;
    }
    countries[countryCode].sub[subdivisionCode] = entry;
  }
}

// Read codes.csv (alpha-2, alpha-3)
const codes = {};
const codesLines = fs.readFileSync(path.join(__dirname, "codes.csv"), "utf8").split("\n");
for (const line of codesLines) {
  if (!line.trim()) continue;
  const [alpha2, alpha3] = line.split(",");
  if (alpha2 && alpha3) codes[alpha3.trim()] = alpha2.trim();
}

// Stats
const subdivisionCount = Object.values(countries).reduce((s, c) => s + Object.keys(c.sub).length, 0);
const deprecatedCount = Object.values(countries).reduce(
  (s, c) => s + Object.values(c.sub).filter((v) => v.isDeprecated).length, 0
);
console.log("Countries: %d, Subdivisions: %d (deprecated: %d)", Object.keys(countries).length, subdivisionCount, deprecatedCount);
console.log("Country codes: %d", Object.keys(codes).length);

// Combine data + functions
const dataJS =
  "var data = " + JSON.stringify(countries, null, 0) + ";" +
  "var codes = " + JSON.stringify(codes, null, 0) + ";";
const functionsJS = fs.readFileSync(path.join(__dirname, "functions.js"), "utf8");

// Minify
const result = UglifyJS.minify(dataJS + functionsJS, { fromString: true, compress: true, mangle: true });
if (result.error) {
  console.error("Minification error:", result.error);
  process.exit(1);
}

const output = ";(function () {\n" + result.code + "\n})();";
fs.writeFileSync(path.join(__dirname, "iso3166.min.js"), output, "utf8");
console.log("Built iso3166.min.js");
