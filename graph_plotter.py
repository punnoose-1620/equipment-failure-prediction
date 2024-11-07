import json
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from pre_processor import *

primary_types = (int, float, str)

def print_subtype(list_data):
    if isinstance(list_data[0],primary_types):
        print('List of ', type(list_data[0]))
    else:
        for item in list_data:
            if isinstance(item, list):
                print("[",print_subtype(item),"]", end=None)
            elif isinstance(item, dict):
                print_data_heirarchy(item)

def print_data_heirarchy(dict_data):
    keys = list(dict_data.keys())
    print("Dict : ",keys, end=None)
    for key in keys:
        value = dict_data[key]
        if isinstance(value, primary_types):
            print(key," : ", type(value), end=None)
        elif isinstance(value, list):
            print(key," : ",print_subtype(value), end=None)
        elif isinstance(value, dict):
            print(key," : ",print_data_heirarchy(value), end=None)
        
def plot_param_count(
        json_data, 
        parameter, 
        title='Count of Items', 
        save_path='count_graph.png'
        ):
    # Extract values for the specified parameter
    values = [item.get(parameter) for item in json_data if parameter in item]

    # Count occurrences of each unique value
    counts = Counter(values)

    # Extract keys and values for plotting
    labels = list(counts.keys())
    frequencies = list(counts.values())

    # Plot the bar graph
    plt.figure(figsize=(10, 6))
    plt.bar(labels, frequencies, color='skyblue')
    plt.xlabel(parameter.capitalize().replace('_',' '))
    plt.ylabel('Count')
    plt.title(title)
    plt.xticks(rotation=90, ha='right')
    plt.tight_layout()
    plt.savefig('./generated_graphs/model_stats/'+save_path)
    # plt.show()
    return values

def plot_temperature_ranges(
        data, 
        keys=['ambient_temp', 'processor_temp'],
        x_label='Data Point Index', 
        y_label='Temperature (°C)',
        title='Ambient vs Processor Temperature',
        save_path='data_comparison.png',
        show_ticks=True
        ):
    # Check if we have data for both temperature keys
    if not data or not keys:
        print("Data or Keys Missing")
        return

    # Plotting
    plt.figure(figsize=(20, 15))
    x_values = [entry['datetime'] for entry in data if 'datetime' in entry]
    max_val = 0
    for key in keys:
        label_temp = key.replace('_',' ')
        values = [float(entry[key]) for entry in data if key in entry]
        if len(values)>0:
            if max(values)>float(max_val) or len(y_values)==0:
                if max(values)>max_val:
                    max_val = max(values)
        # Add data as line to graph
        plt.plot(x_values, values, label=label_temp, marker='o', markersize=1)
    
    y_values = np.linspace(0, max_val, 20).tolist()
    # Adding labels and title
    plt.xlabel(x_label, labelpad=15)
    plt.ylabel(y_label)
    if show_ticks:
        plt.yticks(sorted(y_values))
        plt.xticks(x_values[::50],rotation=90, ha='right', fontsize=10)
    plt.title(title)
    plt.legend()
    plt.grid(True)

    # Display the plot
    plt.savefig('./generated_graphs/model_stats/'+save_path)
    # plt.show()

def get_percipitation_types(data):
    new_data = {}
    for item in perciptype_list:
            item = item.replace(',',' & ').strip()
            if item not in new_data.keys():
                new_data[item] = []
    for entry in data:
        percip_type = str(entry['preciptype'])
        if(percip_type.lower().strip() in ('','null','none')):
            percip_type = 'none'
        percip_type = percip_type.replace(',',' & ')
        if percip_type in new_data.keys():
            new_data[percip_type].append(float(entry['precip']))
            for item in perciptype_list:
                item = item.replace(',',' & ').strip()
                if item!=percip_type:
                    new_data[item].append(0.0)
        else:
            new_data[percip_type] = []
    return new_data

def plot_line_graphs(data, lines, x_label, y_label, title='', save_path='line_graphs.png'):
    plt.figure(figsize=(20, 15))
    x_values = [entry['datetime'] for entry in data if 'datetime' in entry]
    keys = lines.keys()
    maxx_val = 0
    for key in keys:
        x_len = len(x_values)
        y_len = len(lines[key])
        for i in range(0,(x_len-y_len)):
            if x_len<y_len:
                x_values.append(x_values[-1])
            else:
                lines[key].append(0.0)
        plt.plot(x_values, list(lines[key]), label=key, marker='o', markersize=1)
        if max(lines[key])>maxx_val:
            maxx_val = max(lines[key])
    y_values = np.linspace(0, maxx_val, 20).tolist()
    plt.title(title)
    plt.yticks(sorted(y_values))
    plt.xticks(x_values[::70],rotation=90, ha='right', fontsize=10)
    # Adding labels and title
    plt.xlabel(x_label, labelpad=15)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)

    # Display the plot
    plt.savefig('./generated_graphs/model_stats/'+save_path)
    # plt.show()

def generate_all_graphs():
    data = merge_datas('self')
    get_count(data, 'wear_and_tear', 'fail_stat')
    # Generate a graph for the frequency of each type of failures
    plots = [
        # Generate a graph for Count of Different Types of Equipment Failures
        {
            'type': 'param_count',
            'params': 'fail_stat',
            'title': 'Count of Failure Types in Data'
        },
        # Generate a graph for changes in processor temps with respect to ambient temps
        {
            'data': data,
            'type': 'plot_temperature',
            'keys': ['ambient_temp', 'processor_temp'],
            'x_label': 'Date',
            'y_label': 'Temperature (°C)',
            'title': 'Temperature Graph',
            'save_path': 'temperature_comparison.png',
            'show_ticks': True
        },
        # Generate a graph for current usages in response to temperatures
        {
            'data': data,
            'type': 'plot_temperature',
            'keys': ['current_usage', 'processor_temp'],
            'x_label': 'Date',
            'y_label': 'Values',
            'title': 'Temperature vs Current',
            'save_path': 'temperature_current.png',
            'show_ticks': True
        },
        # Generate a graph for current usages
        {
            'data': data,
            'type': 'plot_temperature',
            'keys': ['current_usage'],
            'x_label': 'Date',
            'y_label': 'Amperes',
            'title': 'Current Usage',
            'save_path': 'current_usage.png',
            'show_ticks': False
        },
        # Generate a graph for dew values and humidity
        {
            'data': data,
            'type': 'plot_temperature',
            'keys': ['dew', 'humidity'],
            'x_label': 'Date',
            'y_label': 'Percentatage',
            'title': 'Dew vs Humidity',
            'save_path': 'dew_humidity.png',
            'show_ticks': True
        },
        ]
    for plot in tqdm(plots, desc='Plotting All Graphs'):
        if(plot['type']=='param_count'):
            plot_param_count(
                data, 
                "fail_stat", 
                'Count of Failure Types in Data'
                )
        elif plot['type']=='plot_temperature':
            plot_temperature_ranges(
                plot['data'], 
                plot['type'], 
                plot['x_label'], 
                plot['y_label'], 
                plot['title'], 
                plot['save_path'],
                plot['show_ticks']
                )
    
    percip_types = get_percipitation_types(data)
    plot_line_graphs(
        data, 
        percip_types, 
        'Date', 
        'Amount of Percipitation', 
        'Different Percipitation Types over a year', 
        'percipitation_types.png'
        )
    # Generate a graph for Solar Radiation Levels
    plot_temperature_ranges(
        data, 
        ['solarradiation'], 
        'Date', 
        'Amounts', 
        'Solar Radiation Levels', 
        'solar_radiation.png',
        False
        )
    # Generate a graph for Solar Energy Levels vs Severe Risk levels
    plot_temperature_ranges(
        data, 
        ['solarenergy', 'severerisk'], 
        'Date', 
        'Values', 
        'Solar Energy Levels vs Severe Risk Levels', 
        'solar_energy_severe_risk.png',
        False
        )
    # Generate a graph for UV index
    plot_temperature_ranges(
        data, 
        ['uvindex'], 
        'Date', 
        'Index Values', 
        'UV Index', 
        'uv_index.png',
        False
        )
    print("Plotting all graphs completed....")

# generate_all_graphs()