import os
import csv
import json
from random import randint,shuffle
from tqdm import tqdm

datas = []
data_folder_path = './weather_datas/'
keys_to_drop = [
    'name','sealevelpressure','cloudcover',
    'visibility','sunrise','sunset',
    'moonphase','conditions','description',
    'icon','stations',
    'tempmax','tempmin','feelslikemax',
    'feelslikemin','feelslike','precipprob',
    'precipcover','temp']
perciptype_list = []
failure_types = ['none','thermal_runaway','wear_and_tear','abnormal_fail']
base_amps = 5
round_off_value = 2
wear_and_tear_index = 0
dummy_amps_increment = 0.0001
current_reset = False

def print_entry_types(entry):
    for key in entry.keys():
        print('  ',key,' : ',type(entry[key]))

def try_string_to_num(data):
    for entry in tqdm(data,desc="\nConverting possible values to float"):
        for key in entry.keys():
            try:
                entry[key] = float(entry[key])
            except ValueError:
                entry[key] = entry[key]
                # print('Unable to convert to Numeric')
    return data

def remove_none_null(data):
    empty_types = ()
    for entry in tqdm(data, desc="\nReplacing Empty values"):
        keys = entry.keys()
        for key in keys:
            if entry[key] in empty_types and isinstance(entry[key],(int, float)):
                entry[key] = 0.0
            elif entry[key] in empty_types and isinstance(entry[key],str):
                entry[key] = 'none'
    return data

def replaceNan(data):
    for entry in tqdm(data, desc='\nReplacing NaN values'):
        for key in entry.keys():
            if isinstance(entry[key],(int, float))==False:
                entry[key] = 0.0
    return data

def generate_heat_dissipation(current_amps):
    mass = 0.5 # kg
    specific_heat_capacity = 1250 # Joules/kg°C
    operational_voltage = 230 # Volts
    generated_heat = (current_amps*operational_voltage*86400)/(mass*specific_heat_capacity) # Modified Joule's Law of Heating
    return generated_heat/21600

def get_count(data, value, key):
    count = 0
    for entry in data:
        if entry[key]==value:
            count = count+1
    # print("Count of ",value,' under ',key,' : ',count)

def generate_dummy_data(item, index):
    global wear_and_tear_index
    global current_reset
    wear_and_tear_index += 1
    
    # Generate Current usage that gradually increases over time
    if index>0 :
        item['current_usage'] = round(datas[index-1]['current_usage']+dummy_amps_increment, ndigits=round_off_value)
    elif current_reset:
        item['current_usage'] = base_amps
        current_reset = False
    else : 
        item['current_usage'] = base_amps

    # Generate Processor Temperature based on max temp and heat dissipation by an average resistor
    item['processor_temp'] = round(float(item['tempmax'])+generate_heat_dissipation(item['current_usage']), ndigits=round_off_value)

    # Generate Ambient Temperature around board
    item['ambient_temp'] = item['temp']

    # Generate Failure case
    fail_stat = 'none'
    if randint(0,150)==88 or float(item['solarenergy'])>15:
        fail_stat = 'abnormal_fail'
    elif item['current_usage']>(base_amps+3) or item['processor_temp']>50:
        fail_stat = 'thermal_runaway'
        current_reset = True
    elif wear_and_tear_index>50:
        fail_stat = 'wear_and_tear'
        wear_and_tear_index = 0
    else:
        fail_stat = 'none'
    item['fail_stat'] = fail_stat

    return item

def read_csv(file_path):
    data = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Get the headers
        for row in csv_reader:
            data.append(dict(zip(headers, row)))  # Create a dictionary for each row using headers as keys
    return data

def write_csv(file_path, data):
    # Check if data is not empty
    if not data:
        print("No data provided.")
        return
    
    # Get the headers from the keys of the first dictionary
    headers = data[0].keys()

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.DictWriter(file, fieldnames=headers)
        csv_writer.writeheader()  # Write headers
        csv_writer.writerows(data)  # Write rows

    print(f"Data written to {file_path} successfully.")

def list_files_in_folder(folder_path):
    file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def delete_keys_from_item(item, keys):
    for key in keys:
        del item[key]
    return item

def merge_datas(type='other'):
    global round_off_value
    if type=='self':
        round_off_value = None
    weather_file_list = list_files_in_folder(data_folder_path)
    for weather_file in weather_file_list:
        temp_data = read_csv(weather_file_list[0])
        index = weather_file_list.index(weather_file)
        temp_data = remove_none_null(temp_data)
        for item in temp_data:
            if item['preciptype'] not in perciptype_list:
                perciptype_list.append(str(item['preciptype']))
        for item in tqdm(temp_data, desc="\nImporting Data from file "+str(index)):
            i = temp_data.index(item)
            item = generate_dummy_data(item,i)
            delete_keys_from_item(item, keys_to_drop)
            if type!='self':
                del item['datetime']
                item['preciptype'] = perciptype_list.index(str(item['preciptype']))
                item['fail_stat'] = failure_types.index(str(item['fail_stat']))
            datas.append(item)
        if type!='self':
            temp_data = try_string_to_num(temp_data)
            temp_data = replaceNan(temp_data)
    if type!='self':
        shuffle(datas)
    print("\nTotal Data Size : ",len(datas))
    print("\nSample Data : ",json.dumps(datas[0], indent=4))
    print('\nSample Data Format :')
    print_entry_types(datas[0])
    return datas

# merged_output_file = './Stockholm_merged_dataset.csv'
# merge_datas('self')
# write_csv(merged_output_file,datas)

merged_output_file = './Stockholm_merged_dataset_processed.csv'
merge_datas()
write_csv(merged_output_file,datas)