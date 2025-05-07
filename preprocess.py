import csv
from urllib.parse import urlparse

def extract_company_slug(url):
    path = urlparse(url).path
    return path.rstrip("/").split("/")[-1]  # last non-empty part of path

input_csv = "supplier.csv"
output_csv = "supplier_slugs.csv"

unique_relationships = set()
unique_companies = set()

with open(input_csv, "r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    for row in reader:
        if "Parent" in row[0]:  # skip header
            continue
        if len(row) < 2:
            continue
        parent_url, child_url = row[0].strip(), row[1].strip()
        parent_slug = extract_company_slug(parent_url)
        child_slug = extract_company_slug(child_url)

        if parent_slug != child_slug:
            unique_relationships.add((parent_slug, child_slug))
            unique_companies.update([parent_slug, child_slug])

# Write unique relationships to output CSV
with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["Parent", "Child"])
    for relationship in sorted(unique_relationships):
        writer.writerow(relationship)

print(f"✅ Cleaned company slugs saved to {output_csv}")
print(f"🔢 Unique relationships: {len(unique_relationships)}")
print(f"🏢 Unique companies: {len(unique_companies)}")
