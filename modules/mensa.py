import lib.cmd
import datetime
import urllib.error
import urllib.request
import xml.etree.ElementTree
import xml.parsers.expat


API_URI = ('http://www.akafoe.de/gastronomie/mensen/ruhr-universitaet-bochum/'
           '?mid=1&tx_akafoespeiseplan_mensadetails%5Baction%5D=feed&tx_akafo'
           'espeiseplan_mensadetails%5Bcontroller%5D=AtomFeed&cHash=131da6102'
           'c27a372087f39f4c47be1e9')


NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'xhtml': 'http:/www.w3.org/1999/xhtml',
}


def _to_weekday(n):
    return ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag'][n]


@lib.cmd.command(private=False)
def mensa(msg=None):
    """Zeigt den derzeitigen Speiseplan der RUB Mensa."""
    tree = xml.etree.ElementTree.ElementTree()
    with urllib.request.urlopen(API_URI) as h:
        tree.parse(h)
    desired_date = datetime.datetime.now()
    if desired_date.hour > 15:  # after 15:00: show next day
        desired_date += datetime.timedelta(days=1)
    if desired_date.weekday() >= 5:  # saturday and sunday: show monday
        desired_date += datetime.timedelta(days=desired_date.weekday() - 5)
    day_name = _to_weekday(desired_date.weekday())
    desired_date_str = '%02d.%02d.' % (desired_date.day, desired_date.month)
    for entry in tree.findall('{%(atom)s}entry' % NS):
        title = entry.findtext('{%(atom)s}title' % NS)
        if desired_date_str in title:
            areas = {}
            current_area = ''
            for element in entry.iter():
                if element.tag == '{%(xhtml)s}strong' % NS:
                    current_area = element.text
                    areas[current_area] = []
                if element.tag == '{%(xhtml)s}li' % NS:
                    areas[current_area].append(element.text.strip())
            return '%s, der %s: %s' % (
                day_name,
                desired_date_str,
                '\n'.join('[%s] %s' % (a, ', '.join(v))
                          for a, v in areas.items() if a != 'Beilagen')
            )
    return 'Kein Speiseplan für %s, den %s gefunden.' % (day_name,
                                                         desired_date_str)
