# deals with multiple practice locations
# each practice location on row
# change output filename on line 110
import requests
import pandas as pd
from bs4 import BeautifulSoup
from random import randint
import time

urls = pd.read_csv('RANZCP short urls.csv', dtype=object) # read urls from csv file
url_list = urls['A'][5:10] # make list of urls to loop through
url_listquotes = ', '.join('"{0}"'.format(w) for w in url_list) # so line 27 works

urlcount = len(url_list)
skipcount = 0

# make an empty dataframe - number of rows doesn't matter, set to number of urls
psych_df = pd.DataFrame(index=range(len(url_list)), columns=['Name','Location', 'Phone number', 'Website', 'Email', 'Fax', 'Expertise', 'Services offered', 'Treats these age groups', 'Experience with', 'Offers telepsychiatry', 'Qualifications', 'Languages spoken', 'Summary', 'Find a psych url'], dtype=object)

countindex = -1
for i in url_list:
    # wait 2-5 seconds between page requests
    time.sleep(randint(2,5))
    
    #get the HTML of the page
    page = requests.get(i)
    page # access page
    if str(page) == "<Response [500]>": # avoid server error pages
        skipcount += 1
        continue
    
    #make a variable called soup with the HTML of the page
    soup = BeautifulSoup(page.content, 'html.parser')
    
    countindex += 1
    
    # write url to dataframe
    url = i.replace("\"", "")
    psych_df.loc[countindex, 'Find a psych url'] = url
    # get doctor name as docname
    name_chunk = soup.find('h1', id="p_lt_ctl11_MainContentPlaceholder_p_lt_ctl01_RANZCPFindAPsychiatristProfile_h2PageTitle")
    try:
        docname = name_chunk.text.strip()
    except AttributeError:
        docname = ''
    psych_df.loc[countindex,'Name'] = docname # write to df

    # get location details as location
    loc_index = -1
    loc_count = soup.find('div', id="p_lt_ctl11_MainContentPlaceholder_p_lt_ctl01_RANZCPFindAPsychiatristProfile_divLocations").findAll('div', class_='s-psychprofile__locations__item')
    for loc_chunk in list(loc_count):
        loc_index += 1
        loc_chunk.find('div', class_='s-psychprofile__locations__item__group__content').find('a').replace_with('')
        for br_tag in loc_chunk.find('div', class_='s-psychprofile__locations__item__group__content').findAll('br'):
            br_tag.replace_with(', ')
        location = loc_chunk.find('div', class_='s-psychprofile__locations__item__group__content').text.strip()
        psych_df.loc[countindex + loc_index, "Location"] = location # write to df
        try:
            phone = loc_chunk.find('div', {'aria-label': "Phone number"}).text.strip()
        except AttributeError:
            phone = ''
        psych_df.loc[countindex + loc_index, "Phone number"] = phone # write to df
        # get web address as web_address
        try:
            web_address = loc_chunk.find('div', {'aria-label': "Website address"}).text.strip()
        except AttributeError:
            web_address = ''
        psych_df.loc[countindex + loc_index, "Website"] = web_address # write to df
        # get email as email
        try:
            email = loc_chunk.find('div', {'aria-label': "Email address"}).text.strip()
        except AttributeError:
            email = ''
        psych_df.loc[countindex + loc_index, "Email"] = email #write to df
        # get fax as fax
        try:
            fax = loc_chunk.find('div', {'aria-label': "Fax number"}).text.strip()
        except AttributeError:
            fax = ''
        psych_df.loc[countindex + loc_index, "Fax"] = fax #write to df

    content = soup.findAll('div', class_='s-psychprofile__contentgroup')
    for a in list(content):
        count = -1
        headers = list(a.findAll('h3'))
        for b in headers:
            if b.text.strip() == 'Services offered' or b.text.strip() == 'Expertise' or b.text.strip() == 'Qualifications' or b.text.strip() == 'Treats these age groups' or b.text.strip() == 'Languages spoken' or b.text.strip() == 'Experience with':
                headlist = []
                if len(list(b.parent.findAll('ul'))) > 1:
                    count += 1
                    for c in list(b.parent.findAll('ul')[count].findAll('li')):
                        headlist.append(c.text.strip())
                    headlist = str(headlist).replace('[', '')
                    headlist = headlist.replace(']', '')
                    headlist = headlist.replace('\'', '')
                    psych_df.loc[countindex, b.text.strip()] = headlist
                else:
                    for c in list(b.parent.findAll('li')):
                        if c.text.strip() != '':
                            headlist.append(c.text.strip())
                    headlist = str(headlist).replace('[', '')
                    headlist = headlist.replace(']', '')
                    headlist = headlist.replace('\'', '')
                    psych_df.loc[countindex, b.text.strip()] = headlist
            if b.text.strip() == 'Offers telepsychiatry' or b.text.strip() == 'Summary':
                psych_df.loc[countindex, b.text.strip()] = b.parent.find('p').text.strip()
    countindex += loc_index # makes sure the next psychiatrist record is entered on the correct line
completed = urlcount - skipcount
print("{}/{} pages scraped".format(completed, urlcount))
psych_df.to_csv('RANZCP records 1-537.csv') #change file name