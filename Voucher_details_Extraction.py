import requests
import csv
import json
import datetime
import pandas as pd

# Knack API endpoint and headers
BASE_URL = "https://api.knack.com/v1/objects/object_1/records"
HEADERS = {
    "Content-Type": "application/json",
    "X-Knack-Application-Id": "6495b7dd8e222e002606f178", 
    "X-Knack-REST-API-Key": "c5690383-a6fa-4581-b770-c1d8c3f291ae"
}

# List of fields to exclude from downloading
EXCLUDED_FIELDS = ["id", "field_50", "field_46", "field_1", "field_30", "field_49","field_26"]

def fetch_field_metadata():
    response = requests.get(f"https://api.knack.com/v1/objects/object_1", headers=HEADERS)
    metadata = response.json().get("object", {}).get("fields", [])
    print("Field Metadata:", json.dumps(metadata, indent=4))
    return metadata

def get_header_mappings():
    field_metadata = fetch_field_metadata()
    return {field["key"]: field.get("name", field["key"]) for field in field_metadata}


############## This phase is updating the record in knack ###################### all good.
def update_record_on_knack(record_id, updated_data):
    """Update a single record on the Knack platform."""
    url = f"{BASE_URL}/{record_id}"
    response = requests.put(url, headers=HEADERS, data=json.dumps(updated_data))
    if response.status_code != 200:
        print(f"Failed to update record with ID {record_id}. Status code: {response.status_code}, Response text: {response.text}")

def create_Vendor_Specific_Csv(records, headers_mapping, current_datetime):
    "Creting Vendor Specific_CSV"

    sorted_data = sorted(records, key=lambda x: x["field_1"])
    vendor = 'N'
    Name = ''
    rec = []
    for record in sorted_data:
        if vendor == 'N':
            vendor = record.record.get("field_1")
        if vendor == record.get("field_1"):
            rec.extend(record)
            
        elif vendor != record.get("field_1"):
            save_records_to_csv(rec, headers_mapping, current_datetime, vendor)
            rec.clear()
            rec.extend(record)
            vendor == record.get("field_1")





def update_records(records):
    ##Update the records both locally and on the Knack platform. # save_records_to_csv(records, headers_mapping, currentdatetime)
    for record in records:
        if record.get("field_49") == "N":
            record["field_49"] = "Y"
            update_record_on_knack(record["id"], {"field_49": "Y"})

def get_all_records():
    all_records = []
    page_number = 1
    filter_param = {
        "match": "and",
        "rules": [{
            "field": "field_49",
            "operator": "is",
            "value": "N"
        }]
    }

    while True:
        response = requests.get(
            BASE_URL, 
            headers=HEADERS, 
            params={'page': page_number, 'filters': json.dumps(filter_param)}
        )
        if response.status_code != 200:
            print(f"Failed to fetch data on page {page_number}. Status code: {response.status_code}, Response text: {response.text}")
            break
        records = response.json().get("records", [])
        if not records:
            break
        all_records.extend(records)
        page_number += 1

    update_records(all_records)
    

    return all_records

def save_records_to_csv(records, headers_mapping, currentdatetime, vendor):
    filename=f"\\\\biztalk\\3EDrop\\vchr3eloadfile_{vendor}_{currentdatetime}.csv"
    if not records:
        print("No records to save.")
        return

    
    
    
      
    # Function to save records to a given filename
    def write_to_csv(filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=header_labels)
            writer.writeheader()
            for record in records:
                writer.writerow({headers_mapping.get(key, key): record[key] for key in record.keys() if key not in EXCLUDED_FIELDS and not key.endswith("_raw")})
        print(f"Data saved to {filename}")

    header_labels = [headers_mapping.get(key, key) for key in records[0].keys() if key not in EXCLUDED_FIELDS and not key.endswith("_raw")]

    # Save to both file locations
    write_to_csv(filename)
    

if __name__ == "__main__":
    records = get_all_records()
    headers_mapping = get_header_mappings()
    current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    create_Vendor_Specific_Csv(records, headers_mapping, current_datetime)
    
