import csv

def open_csv_for_writing(file_path):
    """Open a CSV file for writing and return the file object and writer."""
    csvfile = open(file_path, 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvfile)
    return csvfile, writer

# def write_sample_data(writer):
#     """Write three sample rows to the CSV file using the provided writer."""
#     writer.writerow(['Name', 'Age', 'City'])
#     writer.writerow(['Alice', 30, 'New York'])
#     writer.writerow(['Bob', 25, 'London'])
#     writer.writerow(['Charlie', 35, 'Paris'])

# if __name__ == "__main__":
#     file_path = 'utils/sample_output.csv'
#     csvfile, writer = open_csv_for_writing(file_path)
#     write_sample_data(writer)
#     csvfile.close()
