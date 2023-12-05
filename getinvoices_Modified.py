import requests
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






def create_df(records):
    column = ['Invoice Date','Beneficiary Name','Due Date','Grand Total','Service Code',
                       'ClientNumber','Invoice #','Confirmation Number','Line Item Number','Cost Description',
                       'GL Description #1','GL Description #2','Gl Account #','Sub Account #','Bank','Status',
                       'Terms Code','Date of Order','Transaction Type','Detail Type','Currency','Currency Date',
                       'Office','Tax Code']
    
    data = ({'Invoice Date': records.get('field_2'),'Beneficiary Name': records.get('field_3'),'Due Date': records.get('field_4'),
                       'Grand Total':records.get('field_5'),'Service Code': records.get('field_6'),'ClientNumber': records.get('field_7'),'Invoice #':records.get('field_8'),
                       'Confirmation Number':records.get('field_9'),'Line Item Number':records.get('field_10'),
                       'Cost Description':records.get('field_11'),'GL Description #1':records.get('field_12'),'GL Description #2':records.get('field_13'),
                       'Gl Account #':records.get('field_14'),'Sub Account #' :records.get('field_15'),'Bank' :records.get('field_16'),'Status' :records.get('field_17'),
                       'Terms Code' :records.get('field_18'),'Date of Order' :records.get('field_19'),'Transaction Type' :records.get('field_20'),
                       'Detail Type' :records.get('field_21'),'Currency' :records.get('field_22'),'Currency Date' :records.get('field_23'),'Office':records.get('field_24'),
                       'Tax Code':records.get('field_25')})
    df = pd.DataFrame([data], columns = column)
    return df
    



############## This phase is updating the record in knack ###################### all good.
def update_record_on_knack(record_id, updated_data):
    """Update a single record on the Knack platform."""
    url = f"{BASE_URL}/{record_id}"
    response = requests.put(url, headers=HEADERS, data=json.dumps(updated_data))
    if response.status_code != 200:
        print(f"Failed to update record with ID {record_id}. Status code: {response.status_code}, Response text: {response.text}")

def create_Vendor_Specific_Csv(records):
    "Creting Vendor Specific_CSV"

    sorted_data = sorted(records, key=lambda x: x["field_1"])
    vendor = 'N'
    
    column = ['Invoice Date','Beneficiary Name','Due Date','Grand Total','Service Code',
                       'ClientNumber','Invoice #','Confirmation Number','Line Item Number','Cost Description',
                       'GL Description #1','GL Description #2','Gl Account #','Sub Account #','Bank','Status',
                       'Terms Code','Date of Order','Transaction Type','Detail Type','Currency','Currency Date',
                       'Office','Tax Code']
    df1 = pd.DataFrame(columns = column)
    record_data = {'column_name': column}
    
    for record in sorted_data:
        if vendor == 'N':
            vendor = record.get("field_1")
        if vendor == record.get("field_1"):
            df2 =  create_df(record)                     
            df1 = df1._append(df2, ignore_index =True)
        elif vendor != record.get("field_1"):
            save_records_to_csv(df1, vendor)
            df1 = pd.DataFrame()
            record_data = create_df(record)
            df2 =pd.DataFrame(record_data)            
            df1 = df1._append(df2, ignore_index=True)
            vendor = record.get("field_1")
    save_records_to_csv(df1, vendor)
    
def update_records(records):
    ##Update the records both locally and on the Knack platform. 
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

def save_records_to_csv(x,vendor):
    
    currentdatetime =  datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename=f"\\\\biztalk\\3EDrop\\vchr3eloadfile_{vendor}_{currentdatetime}.csv" 
    additional_filename = f"e:\\APInvoicesv2AttachCSV\\vchr3eloadfile_{vendor}_{currentdatetime}.csv"  
    # testdrive = f"B:\\Python\\Git\\Knack_Voucher_detail_Extraction\\Test\\vchr3eloadfile_{vendor}_{currentdatetime}.csv"
    # testdrive2 = f"B:\\Python\\Git\\Knack_Voucher_detail_Extraction\\Test2\\vchr3eloadfile_{vendor}_{currentdatetime}.csv"
   # Function to save records to a given filename
    def write_to_csv(filename):
        x.to_csv(filename,index = False, encoding='utf-8')
        status = print(f"A file is created with the name of {filename}")
        return status
    # Save to both file locations
    write_to_csv(filename)
    write_to_csv(additional_filename)
    # write_to_csv(testdrive)
    # write_to_csv(testdrive2)
    

def main():
    records = get_all_records()
    if len(records) > 1:
        create_Vendor_Specific_Csv(records)
    else:
        print("No record Found")
    
if __name__ == "__main__":
    main()