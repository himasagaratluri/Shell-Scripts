#python code to parse json and export to csv

import csv, json
import pandas as pan

input_csv_file = pan.read_csv("jsonFile.csv")
list_of_dict = input_csv_file['{"UserName":"@gmail.com"}'].tolist()
mydict={key:value for elem in list_of_dict for key,value in eval(elem).items()}

with open('outputfile.csv', 'wb') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in mydict.items():
        writer.writerow([key,value])
