import csv
import datetime
import urllib
import os

from dataconverters import xls

url = 'http://www.ici.org/info/flows_data_2014.xls'
archive = 'archive/flows_data.xls'

def download():
    urllib.urlretrieve(url, archive)

def extract():
    fields = [ 
        'Date',
        'Total Equity',
        'Domestic Equity',
        'World Equity',
        'Hybrid',
        'Total Bond',
        'Taxable Bond',
        'Municipal Bond',
        'Total'
        ]
    fin = open(archive)
    records, metadata = xls.parse(fin)
    records = [ [ r[f['id']] for f in metadata['fields'] ] for r in records ]
    # discard first 2 rows as blank / table title
    records = records[2:]
    
    for r in records:  
        if isinstance(r[0], datetime.datetime):
            # get rid of time part
            r[0] = r[0].isoformat()[:10]
        for idx in range(1, len(r)):
            if isinstance(r[idx], float):
                r[idx] = int(r[idx])

    # split out weekly from monthly
    # somewhere down sheet have blank line then heading for weekly stuff
    for count, r in enumerate(records):
        if r[0] == 'Estimated Weekly Net New Cash Flow':
            weekly = records[count+1:count+7]
            # -1 as blank line above
            monthly = records[:count-1]

    # here we just overwrite as they seem to append (earliest data still there)
    fo = open('data/monthly.csv', 'w')
    writer = csv.writer(fo)
    writer.writerow(fields)
    writer.writerows(monthly)

    # TODO: we actually need to merge this with the existing data ...
    weeklyfp = 'data/weekly.csv'
    existing = []
    if os.path.exists(weeklyfp):
        existing = csv.reader(open('data/weekly.csv'))
        existing.next()
        existing = [ x for x in existing ]
    # combine existing and weekly
    # weekly stuff should be newer so algorith is:
    # iterate through existing and add to weekly until we get
    # existing row with date equal to oldest new row and then we break
    oldest_new_week = list(weekly[0])
    for count,row in enumerate(existing):
        if row[0] == oldest_new_week[0]:
            weekly = existing[:count] + weekly
            break

    fo = open('data/weekly.csv', 'w')
    writer = csv.writer(fo)
    writer.writerow(fields)
    writer.writerows(weekly)


def process():
    download()
    extract()

if __name__ == '__main__':
    download()
    extract()

