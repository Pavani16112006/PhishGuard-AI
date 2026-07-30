import csv
from urllib.parse import urlparse
import json

domains = set()

with open("online-valid.csv", newline='', encoding='utf-8') as file:

    reader = csv.DictReader(file)

    for row in reader:

        url = row['url']

        try:
            domain = urlparse(url).netloc
            domain = domain.replace("www.", "")

            domains.add(domain)

        except:
            pass

blacklist = list(domains)

with open("blacklist.json", "w") as outfile:

    json.dump(blacklist, outfile, indent=2)

print("Blacklist created successfully!")
print("Total domains:", len(blacklist))