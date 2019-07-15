'''
This is a wrapper API to make calls to PubMed
and translate the result to only the needed fields 
in JSON format.
'''

from flask_restful import request
from Camel import CamelResource

import requests as req
import xml.etree.ElementTree as et

pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&rettype=docsum"

class PubMed(CamelResource):

    def __init__(self):
        self.record = {
            'title': '',
            'authors': [],
            'year': None,
            'journal': '',
            'pages': {},
            'url': ''
        }
            
    
    def get(self, pubmed_id):
        response = req.get(pubmed_base_url+'&id='+str(pubmed_id))
        xml = response.text
        eSummaryResult = et.fromstring(xml)
        docsum = eSummaryResult[0]
        for item in docsum.iter('Item'):
            name = item.get('Name')
            value = item.text
            if name == 'Author':
                self.record['authors'].append(value)
            if name == 'Title':
                self.record['title'] = value
            if name == 'PubDate':
                year_string = value.split(' ')[0]
                try:
                    self.record['year'] = int(year_string)
                except:
                    pass                
            if name == 'Source':
                self.record['journal'] = value            
            if name == 'DOI' and value:
                self.record['url'] = "https://doi.org/"+value
            if name == 'Volume':
                self.record['pages']['vol'] = value
            if name == 'Issue':
                self.record['pages']['iss'] = value
            if name == 'Pages':
                self.record['pages']['pages'] = value

        self.record['authors'] = ', '.join(self.record['authors'])
        
        pagesField = ''
        if 'vol' in self.record['pages'] and self.record['pages']['vol']:
            pagesField = self.record['pages']['vol']
        if 'iss' in self.record['pages'] and self.record['pages']['iss']:
            pagesField+= '(' + self.record['pages']['iss'] +')'
        if 'pages' in self.record['pages'] and self.record['pages']['pages']:
            pagesField+= ': ' + self.record['pages']['pages']
        self.record['pages'] = pagesField
        
        return self.record
