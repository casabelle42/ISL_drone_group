import subprocess

def get_wifi_info():
    """gets wifi info and returns a dictionary

    Parameters
    ----------
    None
    
    Returns
    -------
    info : dictionary
        a dictionary of the wifi information including ssid and such
    """    
    
    wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
    data = wifi.decode('utf-8')

    # turn lines into a list by splitting by \r\n
    datalist = data.split("\r\n")

    # remove any empty strings (multiple cases of \r\n)
    datalist = [x for x in datalist if x]
    
    newlist = []
    # Problem with bssid and physical address. They use colons to separate 
    # each element. Need to replace those particular colons with periods.
    # Then we can split each line by the colon and add all those into the 
    # list.
    for element in datalist:
        if 'BSSID' in element or 'Physical address' in element:
            
            newelement = element[:-17]
            tempelement = element[-17:].replace(":", ".")
            element = newelement+tempelement
        element = element.split(':')
        # remove whitespace from before and after text
        element = [x.strip() for x in element]
        # remove any empty strings after removing whitespaces
        element = [x for x in element if x]
        # now add it to the newlist
        newlist.extend(element)
    # now remove useless first element
    newlist = newlist[1:]
    
    # create dictionary and fill it
    info = {'name':newlist[newlist.index('Name')+1],
    'description':newlist[newlist.index('Description')+1],
    'guid':newlist[newlist.index('GUID')+1],
    'paddress':newlist[newlist.index('Physical address')+1],
    'interface':newlist[newlist.index('Interface type')+1],
    'state':newlist[newlist.index('State')+1],
    'ssid':newlist[newlist.index('SSID')+1],
    'bssid':newlist[newlist.index('BSSID')+1],
    'network':newlist[newlist.index('Network type')+1],
    'radio':newlist[newlist.index('Radio type')+1],
    'auth':newlist[newlist.index('Authentication')+1],
    'cipher':newlist[newlist.index('Cipher')+1],
    'connect':newlist[newlist.index('Connection mode')+1],
    'band':newlist[newlist.index('Band')+1],
    'channel':newlist[newlist.index('Channel')+1],
    'r_rate':newlist[newlist.index('Receive rate (Mbps)')+1],
    't_rate':newlist[newlist.index('Transmit rate (Mbps)')+1],
    'signal':newlist[newlist.index('Signal')+1],
    'profile':newlist[newlist.index('Profile')+1],
    'hosted_status':newlist[newlist.index('Hosted network status')+1]}
    
    # return dictionary
    return info
    

def main():
    test = get_wifi_info()
    print(f"Wifi name is {test['ssid']}")

if __name__ == "__main__":
    main()