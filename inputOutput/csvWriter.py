'''
Created on Feb 19, 2013

@author: snorre
'''

def writeFile(filename, results):
    csvFile = open('../' + filename, "w")

    for result in results:
        for member in result:
            pass
