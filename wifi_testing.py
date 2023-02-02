import subprocess
import platform

def get_wifi_info():
    """gets wifi info and returns a dictionary

    Parameters
    ----------
    None
    
    Returns
    -------
    dictionary
        a dictionary of the wifi information including ssid and such
    """
    #macOS get ssid
    if platform.system() == 'Darwin':
        wifi = subprocess.check_output(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport','-I']).decode('utf-8', 'ignore')
        datalist = wifi.split("\n")
        datalist = [x.strip() for x in datalist if x if 'SSID' in x and 'BSSID' not in x]
        datalist = datalist[0].split(':')
        data = datalist[1].strip()
        
    #windows get ssid
    if platform.system() == 'Windows':
        wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces']).decode('utf-8', 'ignore')
        # turn lines into a list by splitting by \r\n
        datalist = wifi.split("\r\n")
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
                element = newelement + tempelement
            element = element.split(':')
            # remove whitespace from before and after text
            element = [x.strip() for x in element]
            # remove any empty strings after removing whitespaces
            element = [x for x in element if x]
            # now add it to the newlist
            newlist.extend(element)
        # now remove useless first element
        newlist = newlist[1:]
        data = newlist[newlist.index('SSID')+1]

    #linux get ssid
    elif platform.system() == 'Linux':
        #wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
        wifi = subprocess.check_output('iwgetid').decode('utf-8', 'ignore')
        data = wifi.split('"')[1]

    # return ssid
    return data
    

def main():
    test = get_wifi_info()
    print(f"Wifi name is {test}")

if __name__ == "__main__":
    main()
