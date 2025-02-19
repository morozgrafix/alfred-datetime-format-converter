# -*- coding: utf-8 -*-

import alfred
import arrow
import calendar
from delorean import utcnow, parse, epoch


def process(query_str):
    """ Entry point """
    value = parse_query_value(query_str)
    if value is not None:
        results = alfred_items_for_value(value)
        xml = alfred.xml(results)  # compiles the XML answer
        alfred.write(xml)  # writes the XML back to Alfred


def parse_query_value(query_str):
    """ Return value for the query string """
    try:
        query_str = str(query_str).strip('"\' ')
        if query_str == "" or query_str.lower() == 'now':
            d = utcnow()
        else:
            # Parse datetime string or timestamp
            if query_str.replace('.', '', 1).isdigit():
                val = float(query_str)
                # If the value is very large (e.g. more than 10 digits long), consider it milliseconds
                if val > 3e10:
                    val = val / 1000.0
                d = epoch(val)
            else:
                d = parse(str(query_str))
    except (TypeError, ValueError):
        d = None
    return d


def alfred_items_for_value(value):
    """
    Given a delorean datetime object, return a list of
    alfred items for each of the results
    """

    index = 0
    results = []

    # First item as timestamp
    item_value = calendar.timegm(value.datetime.utctimetuple())
    results.append(alfred.Item(
        title=str(item_value),
        subtitle=u'UTC Timestamp',
        attributes={
            'uid': alfred.uid(index),
            'arg': item_value,
        },
        icon='icon.png',
    ))
    index += 1

    # Local time
    arrow_time = arrow.get(value.datetime).to('local') 
    item_value = arrow_time.datetime.strftime("%a, %d %b %Y %H:%M:%S")
    timezone = arrow_time.datetime.strftime('%Z')
    results.append(alfred.Item(
        title=item_value,
        subtitle=u'Local time (%s)' % timezone,
        attributes={
            'uid': alfred.uid(index),
            'arg': item_value + " " + timezone,
        },
        icon='icon.png',
    ))
    index += 1

    # Various formats
    formats = [
        # 1937-01-01 12:00:27
        ("%Y-%m-%d %H:%M:%S", 'UTC Timestamp'),
        # 19 May 2002 15:21:36
        ("%d %b %Y %H:%M:%S", 'UTC Timestamp'),
        # Sun, 19 May 2002 15:21:36
        ("%a, %d %b %Y %H:%M:%S", 'UTC Timestamp'),
        # 1937-01-01T12:00:27
        ("%Y-%m-%dT%H:%M:%S", 'UTC Timestamp'),
        # 1996-12-19T16:39:57-0800
        ("%Y-%m-%dT%H:%M:%S%z", 'UTC Timestamp'),
    ]
    for format, description in formats:
        item_value = value.datetime.strftime(format)
        results.append(alfred.Item(
            title=str(item_value),
            subtitle=description,
            attributes={
                'uid': alfred.uid(index),
                'arg': item_value,
            },
            icon='icon.png',
        ))
        index += 1

    return results

if __name__ == "__main__":
    try:
        query_str = alfred.args()[0]
    except IndexError:
        query_str = None
    process(query_str)

