import requests
import re
import itertools
import pandas as pd
import csv
from bs4 import BeautifulSoup

#get the HTML of the page
page = requests.get("https://www.yourhealthinmind.org/find-a-psychiatrist/results/psychiatrist-profile?memberid=343")
page # access page

#make a variable called soup with the HTML of the page
soup = BeautifulSoup(page.content, 'html.parser')

# find the doctor name, strip tags and save the doctor name as docname
name_box = soup.find('span', id='p_lt_ctl11_MainContentPlaceholder_p_lt_ctl01_RANZCPFindAPsychiatristProfile_lblFullName')
docname = name_box.text.strip() 
print(docname)

# get html of details as details_box
details_box = soup.find('div', class_="e-editable-text s-psych-profile-content")

#get headers as list object
headers = [i.text for i in details_box.find_all('h5')]

full_data = [[i.text, i] for i in details_box.find_all(re.compile('h5|p'))]
new_data = [[a, list(b)] for a, b in itertools.groupby(full_data, key=lambda x:x[0] in headers)]
grouped = [new_data[i]+new_data[i+1] for i in range(0, len(new_data), 2)]
final_data = {c:{i:str(h)[3:-4].split('<br/>')[1:] for i, h in results} for [_, [[c, _]], _, results] in grouped}

# turn final_data into a series
final_dataFrame = pd.Series(final_data, index=headers, name=docname)

#write to .csv file
csvname= str(docname) +".csv"
final_dataFrame.to_csv(csvname, index=True, header=False)

# save caption text to variable caption
caption_box = soup.find('p', class_="e-caption s-find-psych-profile__notice")
caption = caption_box.text.strip()
print(caption)