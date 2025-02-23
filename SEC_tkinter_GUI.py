import tkinter as tk
from tkinter import simpledialog
from tkinter import *
from tkinter import simpledialog, scrolledtext
from tkinter.scrolledtext import ScrolledText
import platform
import os
import pandas as pd
import re
from bs4 import BeautifulSoup
import html

hostname = platform.node()

if hostname == "T_800_Model_101":
   directory = "D:/Dropbox/foreign_earnings/"

if hostname == "ECON-STAFF-ASSOC-2022IMAC-H4TJ80ZFQ6X9-2":
   directory = "/Users/gr2757/Dropbox/foreign_earnings/"
   
if hostname == "jeff":
    directory = "C:/Users/gabri/Dropbox/foreign_earnings/"

tenQ = (directory + "data/archive_10-Q_full") #file path for all 10-Qs collected
tenK = (directory + "data/archive_10-K_full") #file path for all 10-Ks collected

#here is the function to shorten text. 
def merge_paragraphs(line_by_line):
    target_lines = []
    paragraphs_index = []
    paragraphs_list = []

    # Assuming line_by_line is already defined
    for i in range(len(line_by_line)):
        if re.search(r"repatriat", line_by_line[i],re.IGNORECASE):  # if there is a match, save the index
            start_index = max(0, i - 15)
            end_index = min(len(line_by_line), i + 15)

            index = [start_index, end_index]
            target_lines.append(index)

    # Merge overlapping or close indices
    if target_lines:
        current_start_index = target_lines[0][0]
        current_end_index = target_lines[0][1]

        for i in range(1, len(target_lines)):
            next_start_index = target_lines[i][0]
            next_end_index = target_lines[i][1]

            if next_start_index <= current_end_index + 15:  # Merge if within 15 lines
                current_end_index = next_end_index
            else:
                paragraphs_index.append([current_start_index, current_end_index])
                current_start_index = next_start_index
                current_end_index = next_end_index

        paragraphs_index.append([current_start_index, current_end_index])

    # Extract paragraphs
    for index in paragraphs_index:
        paragraph_string = ""
        for i in range(index[0], index[1]):
            paragraph_string += line_by_line[i] + "\n"

        paragraphs_list.append(paragraph_string.strip())

    return(paragraphs_list)

#this take a start index and returns the relevant file path
def create_file_path(start):
    row_values = input_df.iloc[start, :].values
    gvkey = row_values[0]
    form = row_values[3]
    accession_num = row_values[4]

    if form == "10-K" or "10-K/A":
        file_path = os.path.join(tenK, str(gvkey), str(accession_num) + ".txt")
    elif form == "10-Q" or "10-Q/A":
        file_path = os.path.join(tenQ, str(gvkey), str(accession_num) + ".txt")

    return (file_path)

#this function takes a file path and returns the string of useful paragraphs
def file_to_string(file_path):
    with open(file_path, 'r') as file: #open the file
        text = file.read()

    #some of the html encoding is strange, so we need to decode it
    decoded_html = html.unescape(text)


    soup = BeautifulSoup(decoded_html, 'html.parser') #parse the html
    text = soup.get_text() #grab just the text

    line_by_line = text.split("\n") #turn the text into a list of lines
    paragraphs_list = merge_paragraphs(line_by_line) #turning that list of lines to be a list of paragraphs that contain the word "repatriat"

    string = "" #initialize the string
    
    for paragraph in paragraphs_list: #flatten this list of paragraphs into a string
        string += paragraph + "\n"


    return string    

#function to retrieve values from input df
def column_values(start):
    row_values = input_df.iloc[start, :].values
    gvkey = row_values[0]
    firm_name = row_values[1]
    year = row_values[2]
    form = row_values[3]
    accession_num = row_values[4]

    return(gvkey, firm_name, year, form, accession_num)

# Function to highlight words
def highlight_words(text_widget, words, tag_name="highlight", background="yellow", foreground="black"):
    text_widget.tag_configure(tag_name, background=background, foreground=foreground)
    for word in words:
        start_idx = "1.0"
        word = word.lower()
        while True:
            start_idx = text_widget.search(word, start_idx, tk.END)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(word)}c"
            text_widget.tag_add(tag_name, start_idx, end_idx)
            start_idx = end_idx

#this is the fuction that goes to the next item in the df
def iterate_function(event=None):
    text_area.config(state=tk.NORMAL)  # Enable text area for editing
    text_area.delete("1.0", tk.END)  # Clear current text
    
    global start  # Ensure start is treated as a global variable

    try:
        if start >= len(input_df): #if we are at the end of the df, then we are done
            text_area.insert(tk.END, "You have reached the end of the list")
            text_area.config(state=tk.DISABLED)
        else:
            start = start + 1
            file_path = create_file_path(start) #create the file path
            text_area_text = file_to_string(file_path) #grab the text from the file path
            text_area.insert(tk.END, text_area_text)  #Go to the next text in the list
        
        text_area.config(state=tk.DISABLED)  # Make text area read-only again


        input_text.delete(0, tk.END)  # Clear the entry widget
        highlight_words(text_area, words_to_highlight) #highlight the words

        print("start:",start)
        
        global counter
        counter = counter + 1

        if counter == 10:
            output_df.to_csv(directory + "/interface/output_df.csv", index = False) #to save, just write the output_df to a csv
            counter = 0
            print("---------------------------------------------------------------------------- auto saved!")
    except:
        print("error in reading the file, used a recursive function")
        iterate_function()

#save and exit function
def save_and_exit(event=None):
    output_df.to_csv(directory + "/interface/output_df.csv", index = False) #to save, just write the output_df to a csv
    root.quit()

# Function to get the to do a lot
def get_input_text(event=None):
    input_value = input_text.get() #this is to grab the text from the input box
    gvkey, firm_name, year, form, accession_num = column_values(start) #grab the column values
    new_row = {'gvkey': gvkey, 'firm_name': firm_name, 'year': year, 'form': form, 'accession_num': accession_num, 'amount':  input_value} #grab the values needed for the df
    output_df.loc[len(output_df)] = new_row #append the new row to the output_df
    print("value worked", "file:", accession_num)
    iterate_function() #run the iterate function

#function for inputting NA
def NA_function(event=None):
    input_text.insert(tk.END, "NA")  # Show NA in ther entry widget
    input_value = input_text.get() #this is to grab the text from the input box
    gvkey, firm_name, year, form, accession_num = column_values(start) #grab the column values
    new_row = {'gvkey': gvkey, 'firm_name': firm_name, 'year': year, 'form': form, 'accession_num': accession_num, 'amount':  input_value} #grab the values needed for the df
    output_df.loc[len(output_df)] = new_row #append the new row to the output_df
    print("NA worked")
    iterate_function() #run the iterate function

counter = 0 #intialize the counter

#dataframes 
output_df = pd.read_csv(directory + "/interface/output_df.csv") #read the output_df
input_df = pd.read_csv (directory + "interface/input_df.csv") #read the input_df

try:
    start = len(output_df) #this should the last element of the df (where to start the iteration)
    file_path = create_file_path(start) #create the file path
    text_area_text = file_to_string(file_path) #grab the text from the file path
except:
    print('error in reading the file')
    start = start + 1
    file_path = create_file_path(start) #create the file path
    text_area_text = file_to_string(file_path) #grab the text from the file path
    
#create the tkinter window
root = tk.Tk()
root.geometry("1200x1000")
root.title("Repatriation") 

#create the text area
text_area = ScrolledText(root, wrap=tk.WORD, width=1100, height=750)
text_area.insert(tk.END, text_area_text)  #Insert text
text_area.config(state=tk.DISABLED)  # Make the text area read-only

#highlight the words
words_to_highlight = ["Repatriate","Repatriation","Repatriated", "$", "million", "repatriating"]
highlight_words(text_area, words_to_highlight)

#save and exit button
save_and_exit = tk.Button(root, text="Save & Exit", command = save_and_exit)

# Input box
input_text = tk.Entry(root, width=100, bg="light grey")
input_text.bind("<Return>", get_input_text)

# Button for the input of NA
NA_button = tk.Button(root, text="Not Applicable", command = NA_function)

# Button for the input
get_text_button = tk.Button(root, text="Store Input", command = get_input_text)

#pack statments
save_and_exit.pack(side=tk.BOTTOM)
NA_button.pack(side=tk.BOTTOM)
get_text_button.pack(side=tk.BOTTOM)
input_text.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
text_area.pack(padx=10, pady=(10,10), expand=True, fill="both")

root.mainloop()
