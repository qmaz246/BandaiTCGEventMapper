#!/usr/bin/env python3

import gmplot
from bs4 import BeautifulSoup
import argparse
from pathlib import Path

# Generate list of unique shops that have events.
def genShopList(args):
    shops = {}
    if args.html:
        if args.multifile:
            # htmlFile is now dir
            pathlist = Path(args.inputFile).rglob('*.html')
            for path in pathlist:
                with open(path) as file:
                    soup = BeautifulSoup(file, "html.parser")
                    events = soup.findAll("li", class_="event-item")
                    for event in events:
                        address = event.findAll("p", "event-address")[1].contents[0].strip()
                        # either under event-name-link or event-name
                        try:
                            store_name = event.find("h2","event-name-link").find("span").contents[0]
                        except AttributeError:
                            store_name = event.find("h2","event-name").find("span").contents[0]
                        if store_name not in shops:
                            shops[store_name] = address

        else:
            with open(args.inputFile) as file:
                soup = BeautifulSoup(file, "html.parser")
                events = soup.findAll("li", class_="event-item")
                for event in events:
                    address = event.findAll("p", "event-address")[1].contents[0].strip()
                    # either under event-name-link or event-name
                    try:
                        store_name = event.find("h2","event-name-link").find("span").contents[0]
                    except AttributeError:
                        store_name = event.find("h2","event-name").find("span").contents[0]
                    if store_name not in shops:
                        shops[store_name] = address
    else:
        #text file input
        with open(args.inputFile) as file:
            line = file.readline()
            while line != "":
                store_name = line.split("\n")[0]
                store_date = file.readline()[5:].split("\n")[0]
                store_address = file.readline()[8:].split("\n")[0]
                
                shops[store_name] = (store_address, store_date)
                
                line = file.readline()
        
    return shops

# Process and Map locations
def plotMap(gmap, shops, args):
    if args.html:
        for shop in shops:
            try:
                loc = gmplot.GoogleMapPlotter.geocode(cleanup(shops[shop]), apikey=args.apikey)
                gmap.marker(loc[0], loc[1], color='cornflowerblue', title=shop)
            except:
                # try to combine store name and address
                try:
                    loc = gmplot.GoogleMapPlotter.geocode(shop+" "+cleanup(shops[shop]), apikey=args.apikey)
                    gmap.marker(loc[0], loc[1], color='cornflowerblue', title=shop)
                except Exception as e:
                    # oh well
                    print("Issue finding %s: %s: %s"%(shop,cleanup(shops[shop]),e))
    
    else:
        for shop in shops:
            try:
                loc = gmplot.GoogleMapPlotter.geocode(cleanup(shops[shop][0]), apikey=args.apikey)
                gmap.marker(loc[0], loc[1], color='cornflowerblue', title=shop, info_window=shops[shop][1])
            except:
                # try to combine store name and address
                try:
                    loc = gmplot.GoogleMapPlotter.geocode(shop+" "+cleanup(shops[shop][0]), apikey=args.apikey)
                    gmap.marker(loc[0], loc[1], color='cornflowerblue', title=shop, info_window=shops[shop][1])
                except Exception as e:
                    # oh well
                    print("Issue finding %s: %s: %s"%(shop,cleanup(shops[shop]),e))

    # Draw the map to an HTML file:
    gmap.draw('%s.html'%(args.mapName))

def cleanup(address):
    # Various cases of parts of the address that Google doesn't like UxU
    
    for offender in ["#"]:
        if offender in address:
            address = address.replace(offender, "")
    
    
    return address

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k',dest="apikey")
    parser.add_argument('-f',dest="inputFile")
    parser.add_argument('-m',dest="mapName")
    parser.add_argument('-n',action="store_true",dest="multifile")
    parser.add_argument('-l',action="store_true",dest="html")
    args = parser.parse_args()
    # Create the map plotter:
    # Starting Point, should default to entire view of US\\
    gmap = gmplot.GoogleMapPlotter.from_geocode("United States", zoom=4, apikey=args.apikey)
    
    shops = genShopList(args)
    print("%i Shops Found"%(len(shops)))
    plotMap(gmap, shops, args)
    

if __name__=="__main__":
    main()