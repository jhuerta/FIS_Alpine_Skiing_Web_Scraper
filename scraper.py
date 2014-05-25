import os
#THIS LINES SHOULD BE BEFORE IMPORTING SCRAPERWIKI!!!!
DATABASE_NAME = 'data.sqlite'
os.environ['SCRAPERWIKI_DATABASE_NAME'] = DATABASE_NAME

import scraperwiki
import lxml.html
from pprint import pprint

def get_list_of_new_records(urlLink):
    newRaceResultsRecords = []
    for link, raceinfo in race_link_results(urlLink):
        
        # if you want to see how many races are being scraped, uncomment this
        #save_print(raceinfo['date'] + " " + raceinfo['place'] + " " + raceinfo['discipline'] + " " + raceinfo['codex'])
        
        raceResults = get_race_results(link)
        for raceResult in raceResults:
            complete_athlete_result_line = merge_two_dictionaries(raceResult,raceinfo)
            newRaceResultsRecords.append(complete_athlete_result_line)
    return newRaceResultsRecords

def insert_update_to_database(record, table):
    scraperwiki.sqlite.save(unique_keys=['name','date','discipline'], data=record, table_name=table)

def merge_two_dictionaries(dictA, dictB):
    return dict(dictA.items() + dictB.items())

# generator of FIS race links
def race_link_results(url):
    html = scraperwiki.scrape(url)
    root = lxml.html.fromstring(html)
    result_table = root.cssselect("table.fisfootable")[0]
    status_cells = result_table.cssselect("td.status")
    for status_cell in status_cells:
        result_div = status_cell.cssselect("div")[1]
        for element, attribute, link, pos in result_div.iterlinks():
            event_page = scraperwiki.scrape(link)
            event_root = lxml.html.fromstring(event_page)
            event_rows = event_root.cssselect("table.footable tbody tr")
            for event_row in event_rows:
                last_cell = event_row.cssselect("td:last-child")[0]
                for race_links in last_cell.iterlinks():
                    tdSelected = event_row.cssselect("td")
                    extra = {
                        'date': get_cell_value(tdSelected[1], "span a"),
                        'place': get_cell_value(tdSelected[2], "span a"),
                        'country': get_cell_value(tdSelected[3], "a span"),
                        'codex': get_cell_value(tdSelected[4], "a"),
                        'discipline': get_cell_value(tdSelected[5], "a"),
                    }
                    yield (race_links[2], extra)

def get_cell_value(element, css):
    return element.cssselect(css)[0].text_content()

def save_text_element_print(element):
    print element.text_content().encode('ascii', 'ignore')

def save_print(element):
    print element.encode('ascii', 'ignore')

def get_race_results(url):
    raceResults = []
    html = scraperwiki.scrape(url)
    root = lxml.html.fromstring(html)
    result_rows = root.cssselect("div.bloc-tab")[1].cssselect("table.footable tbody tr")
    for result_row in result_rows:
        if row_contains_information(result_row):
            athlete_data = extract_data_for_this_athlete(result_row)
            raceResults.append(athlete_data)
    return raceResults

def row_contains_information(row):
    NUMBER_OF_COLUMNS_WITH_INFO = 11
    #A row contains information if it has 11 columns. 
    #Some rows in the table don't have any information, stating only that the rider didn't start
    tdElementsInRow = row.cssselect("td")
    return len(tdElementsInRow) == NUMBER_OF_COLUMNS_WITH_INFO

def extract_data_for_this_athlete(row):
    return {
        'Rank': get_plain_element_from_column_number(row,0),
        'Bib': get_plain_element_from_column_number(row,1),
        'FISCode': get_plain_element_from_column_number(row,2),
        'Name': get_plain_element_from_column_number(row,3),
        'Year': get_plain_element_from_column_number(row,4),
        'Nation': get_plain_element_from_column_number(row,5),
        'Run_1': get_plain_element_from_column_number(row,6),
        'Run_2': get_plain_element_from_column_number(row,7),
        'Total_Time': get_plain_element_from_column_number(row,8),
        'Time_Diff': get_plain_element_from_column_number(row,9),
        'FIS_Points': get_plain_element_from_column_number(row,10),
    }

def get_plain_element_from_column_number(element,colNumber):
    return element.cssselect("td")[colNumber].text_content()        

def test_how_scraperwiki_save_works():
    record_A = { 'name': "Juan3",
                'lastname': "Huerta5",
                'age': 36}
    record_B = { 'name': "Juan3",
                'lastname': "Huerta6",
                'age': 36}
    records = []
    records.append(record_A)
    records.append(record_B)
    scraperwiki.sqlite.save(unique_keys=['name','lastname'], data=records, table_name="theTable")
    print os.environ.get('SCRAPERWIKI_DATABASE_NAME')
    print scraperwiki.sqlite.execute("select * from theTable") 

def main():
    FIS_URL = "http://data.fis-ski.com/alpine-skiing/results.html"
    #print "Pulling data out of the page ..."
    newRaceResultsRecords = get_list_of_new_records(FIS_URL)
    #print "Saving data in the database ..."
    insert_update_to_database(newRaceResultsRecords,"data")
    #print "Data stored. Displaying tables in database"
    #print scraperwiki.sqlite.show_tables() 
    #print "Displaying info from table data"
    #print scraperwiki.sqlite.execute("select * from data limit 50") 

# _____________________ START MAIN PROGRAM _____________________

#test_how_scraperwiki_save_works()
main()
print scraperwiki.sqlite.execute("select count(name) from data")['data']


# ______________________________________________________________


# _____________________ HELPERS AND INFORMATION _____________________

#save_print(complete_athlete_result_line)
#for raceResult in raceResults:
    #print raceResult
#print raceinfo

# html = scraperwiki.scrape(link)
# root = lxml.html.fromstring(html)
# result_table = root.cssselect("table.fisfootable")[0]
# print raceinfo['date']

# # Write out to the sqlite database using scraperwiki library
# data = {"name": "susan", "occupation": "software developer"}
# scraperwiki.sqlite.save(unique_keys=['name'], data=data, table_name="data")
# 
# An arbitrary query against the database
# pprint(scraperwiki.sql.select("* from data where 'name'='susan'"))

# ______________________________________________________________

