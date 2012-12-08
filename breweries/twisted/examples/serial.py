ids = [10482,
10433,
12849,
13579,
11917,
13176,
10874,
13015,
11324,
5463,
5335,
11531,
13465,
12745,
12808,
11525,
4592,
13048,
11482,
12880,
12599,
13204,
13562,
11860,
13580,
13138,
12164,
6452,
12306,
11808]

import urllib2
from bs4 import BeautifulSoup

def parseData(data):
    soup = BeautifulSoup(data)
    table = soup.find('form',attrs={'name':'breweryinformation'}).table
    name = table.find('input',attrs={'name':'brewname'}).attrs['value']
    status = table.find('select',attrs={'name':'brewstatus'}).find('option',attrs={'selected':'selected'}).attrs['value']
    info = {'name': name, 'status': status}
    return info

for id in ids:
    url = 'http://beerme.com/fixerror.php?'+str(id)
    print parseData(urllib2.urlopen(url).read())
    
