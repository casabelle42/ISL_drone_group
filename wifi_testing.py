'''
#################################################################################################
#
#
#   Fayetteville State University Intelligence Systems Laboratory (FSU-ISL)
#
#   Mentors:
#           Dr. Sambit Bhattacharya
#           Catherine Spooner
#
#   File Name:
#           wifi_testing.py
#
#   Programmers:
#           Antonio Ball
#           Ryan De Jesus
#           Garrett Davis
#           Kalsoom Bibi
#           Santino Sini
#           Daniel Bigler
#           Taryn Rozier
#           Ashley Sutherland
#           Tyuss Handley
#           Adriel Alvarez
#           Malik Brock
#           Raymond Poythress
#
#  Revision     Date                        Release Comment
#  --------  ----------  ------------------------------------------------------
#    1.0     01/12/2023  Initial Release
#
#  File Description
#  ----------------
#  This program determines which operating system 
#  is being used and then prints out the Wifi name
#  that is currently in use. Used to determine 
#  drone name.
#  
#  
#  *Classes/Functions organized by order of appearance
#
#  OUTSIDE FILES REQUIRED
#  ----------------------
#   None
#
#
#  CLASSES
#  -------
#   None
#
#  FUNCTIONS
#  ---------
#   get_wifi_info
#   main
#
'''
#################################################################################################
#Import Statements
#################################################################################################
import subprocess
import platform

#################################################################################################
#Functions
#################################################################################################

def get_wifi_info():
    """gets wifi info and returns a string

    Parameters
    ----------
    None
    
    Returns
    -------
    data: string
         The ssid of the wifi connection
    """
    #macOS get ssid
    if platform.system() == 'Darwin':
        wifi = subprocess.check_output(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport','--scan'])
        
    #windows get ssid
    if platform.system() == 'Windows':
        wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
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
    """Calls get wifi info and prints the results


    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    test = get_wifi_info()
    print(f"Wifi name is {test}")

if __name__ == "__main__":
    main()
