DATETIME_F = ''.join([
        # 20110909T233600Z
        '%Y',
        '%m',
        '%d',
        'T',
        '%H',
        '%M',
        '%S',
        'Z',
        ])

def datefmt(dt):
    return dt.strftime(DATETIME_F)

def dateparse(dt_str):
    import datetime
    return datetime.datetime.strptime(dt_str, DATETIME_F)

def totimestamp(dt):
    from calendar import timegm
    return timegm(dt.timetuple())

