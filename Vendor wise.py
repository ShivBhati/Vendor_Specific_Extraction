data_list = [
    {'key': 'value1', 'other': 'data1'},
    {'key': 'value2', 'other': 'data2'},
    {'key': 'value1', 'other': 'data3'},
    {'key': 'value3', 'other': 'data4'},
]

# Use a set to store distinct values
distinct_values = set(item['other'] for item in data_list)

# Convert the set back to a list if needed
distinct_list = list(distinct_values)

print(distinct_list)