
import csv
import yaml

def csv_to_yaml(csv_file_path, yaml_file_path):
    # Reading the CSV data
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = []
        for row in reader:
            # Clean up and prepare the data dictionary
            entry = {key: value.replace('\n', '\\n') for key, value in row.items()}
            data.append(entry)
    
    # Writing to a YAML file
    with open(yaml_file_path, 'w', encoding='utf-8') as yamlfile:
        yaml.dump(data, yamlfile, allow_unicode=True, default_flow_style=False)

# File paths
csv_file_path = 'examples.csv'  # Replace with your CSV file path
yaml_file_path = 'examples.yaml'  # Replace with your desired output YAML file path

csv_to_yaml(csv_file_path, yaml_file_path)
