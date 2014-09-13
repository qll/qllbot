from urllib.request import urlopen
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError
from datetime import date, timedelta, datetime
from lib.commands import command


# The time (in 24h format) from which on the plan for the next day will be retrieved, if not otherwise stated.
NEXT_DAY_TIME = 15

BASEURL = 'http://www.akafoe.de/gastronomie/mensen/ruhr-universitaet-bochum/?mid=1&tx_akafoespeiseplan_mensadetails%5Baction%5D=feed&tx_akafoespeiseplan_mensadetails%5Bcontroller%5D='
ATOM_STR = 'AtomFeed'
#RSS_STR  = 'RSSFeed'
URL = BASEURL + ATOM_STR

ATOM = 'http://www.w3.org/2005/Atom'
XHTML = 'http:/www.w3.org/1999/xhtml'

weekdays = ['mo', 'di', 'mi', 'do', 'fr']
weekday_names = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']

categories = [('Sprinter',0), ('Komponenten',1), ('Aktion',3), ('Bistro',5)]

@command()
def mensa(param):
    ''' Mensaplan. Parameter: heute, morgen, mo, di, mi, do, fr '''
    param = param.strip().lower().split(' ')[0]

    outstr = ''
    today = date.today()

    # Fetch the date to look up, based on supplied parameters.
    if param in weekdays:
        monday = today + timedelta(days=-today.weekday())
        date_wanted = monday + timedelta(days=weekdays.index(param))
        outstr += '{0} '.format(weekday_names[date_wanted.weekday()])
    else:
        if param == 'heute':
            date_wanted = today
            outstr += 'Heute '

        elif param == 'morgen':
            date_wanted = today + timedelta(days=1)
            outstr += 'Morgen '

        else:
            if datetime.now().hour < NEXT_DAY_TIME:
                date_wanted = today
                outstr += 'Heute '
            else:
                date_wanted = today + timedelta(days=1)
                outstr += 'Morgen '

    # When it is weekend, fetch the plan for next week [TODO].
    if date_wanted.weekday() in [5,6]: #saturday, sunday
        monday = date_wanted + timedelta(days=-date_wanted.weekday())
        date_wanted = monday + timedelta(weeks=1)
        outstr += 'Naechsten {0} '.format(weekday_names[date_wanted.weekday()])

    outstr += 'inner Mensa:\n'

    # Get the plan for the current week.
    try:
        handle = urlopen(URL)
    except Exception as error:
        return error
    info = ElementTree()
    try:
        info.parse(handle)
    except ExpatError:
        return 'Error: Malformed XML.'
    handle.close()

    found_entry = None

    # Loop through the entries until the date wanted is found.
    for entry in info.getiterator('{{{0}}}entry'.format(ATOM)):
        if date_wanted.strftime('%d.%m.') in entry.findtext('{{{0}}}title'.format(ATOM)):
            found_entry = entry

    # Now split the dishes and add them to the output string.
    if found_entry == None:
        raise Exception('No entry found for that day. The feed sucks!')
    else:
        content = found_entry.find('{{{0}}}content'.format(ATOM)).find('{{{0}}}div'.format(XHTML))
        dishes = content.findall('{{{0}}}ul'.format(XHTML))

        for name,id in categories:
            outstr += '[{0}]\n'.format(name)
            for dish in dishes[id].findall('{{{0}}}li'.format(XHTML)):
                outstr += dish.text.split('(')[0]+'\n'

        return outstr

#if __name__ == "__main__":
#    print(mensa("").encode("utf-8"))
