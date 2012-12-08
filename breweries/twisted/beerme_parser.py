from bs4 import BeautifulSoup

class BeerMeParser():

    def __init__(self, data):
        self.soup = BeautifulSoup(data)
        self.table = self.soup.find('form',attrs={'name':'breweryinformation'}).table

    @staticmethod
    def parse(data):
        return BeerMeParser(data).parseData()

    def parseData(self):
        info = {}
        info['name'] = self.getName()
        info['location'] = self.getLocation()
        info['status'] = self.getStatus()
        info['opened'] = self.getOpened()
        info['brewer'] = self.getBrewers()
        info['production'] = self.getProduction()
        info['websites'] = self.getWebsites()
        info['contact'] = self.getContact()
        info['amenities'] = self.getAmenities()
        info['type'] = 'brewery'
        info['source'] = 'beerme'
        info['beerme_id'] = self.soup.find('input',attrs={'name':'brewid'}).attrs['value']
        return info

    def getLocation(self):
        loc = {}
        loc['address'] = self.getAddress()
        loc['city'] = self.getCity()
        loc['region'] = self.getRegion()
        loc['country'] = self.getCountry()
        loc['zip'] = self.getZip()
        loc['geo'] = {}
        loc['geo']['lat'] = self.getLat()
        loc['geo']['lon'] = self.getLon()
        return loc
  
    def getContact(self):
        con = {}
        con['phone'] = self.getPhone()
        con['toll_free'] = self.getTollFree()
        con['email'] = self.getEmail()
        return con

    def getAmenities(self):
        amt = []
        # get amentities
        return amt

    def getName(self):
        fst = self.tableInputFind('brewname')
        scd = self.tableInputFind('brewname2')
        name = ' '.join([fst,scd])
        return name.strip() if name != ' ' else None

    def getAddress(self):
        fst = self.tableInputFind('brewaddress')
        scd = self.tableInputFind('brewaddress2')
        addr = ' '.join([fst,scd])
        return addr.strip() if addr != ' ' else None

    def getCity(self):
        city = self.tableInputFind('brewcity')    
        return city if city != ' ' else None

    def getRegion(self):
        region = self.table.find('select',attrs={'name':'brewregion'}).find('option',attrs={'selected':'selected'})
        return region.attrs['value'] if region is not None else None

    def getCountry(self):
        region = self.table.find('select',attrs={'name':'brewregion'}).find('option',attrs={'selected':'selected'})
        return region.parent.attrs['label'] if region.parent.name == 'optgroup' else None

    def getZip(self):
        zipcode = self.tableInputFind('brewzip')
        return zipcode if zipcode != ' ' else None

    def getLat(self):
        lat = self.tableInputFind('brewlatitude')
        return float(lat) if lat != '' else None
    
    def getLon(self):
        lon = self.tableInputFind('brewlongitude')
        return float(lon) if lon != '' else None

    def getStatus(self):
        status = self.table.find('select',attrs={'name':'brewstatus'}).find('option',attrs={'selected':'selected'})
        return status.attrs['value'] if status is not None else None

    def getOpened(self):
        # think about converting to datetime
        opened = self.tableInputFind('brewopened')
        return opened if opened != '' else None

    def getBrewers(self):
        brewers = self.tableInputFind('brewbrewer').split(',')
        return [b.strip() for b in brewers]

    def getProduction(self):
        cap = self.tableInputFind('brewcapacity')
        if cap == '': return None
        captype = self.table.find('select',attrs={'name':'brewcapacityunit'}).find('option',attrs={'selected':'selected'})
        captype = captype.attrs['value'] if captype is not None else None
        capacity = {}
        capacity['value'] = int(cap)
        capacity['unit'] = captype
        return capacity

    def getWebsites(self):
        pages = self.tableInputFind('brewhomepage').split(' ')
        pages = filter(lambda x: x != '', pages)
        return pages

    def getPhone(self):
        phone = self.tableInputFind('brewphone')
        return phone if phone != '' else None

    def getTollFree(self):
        tollfree = self.tableInputFind('brewtollfree')
        return tollfree if tollfree != '' else None

    def getEmail(self):
        email = self.tableInputFind('brewemail')
        return email if email != '' else None

    #utility methods
    def tableInputFind(self, name):
        val = self.table.find('input',attrs={'name':name}).attrs['value']
        return val 
