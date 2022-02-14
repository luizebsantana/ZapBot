from datetime import datetime

MONTHS = {
    'janeiro': 1,
    'fevereiro': 2,
    'março': 3,
    'abril': 4,
    'maio': 5,
    'junho': 6,
    'julho': 7,
    'agosto': 8,
    'setembro': 9,
    'outubro': 10,
    'novembro': 11,
    'dezembro': 12
}

def __parse_date(datestr: str) -> datetime:
    try:
        return datetime.strptime(datestr.replace(' ',''), '%d/%m/%Y')
    except ValueError:
        pass
    try:
        return datetime.strptime(datestr.replace(' ',''), '%d/%m/%y')
    except ValueError:
        pass
    try:
        return datetime.strptime(datestr.replace(' ',''), '%d-%m-%Y')
    except ValueError:
        pass
    try:
        return datetime.strptime(datestr.replace(' ',''), '%d-%m-%y')
    except ValueError:
        pass
    try:
        return datetime.strptime(datestr, '%d %m %Y')
    except ValueError:
        pass

def date_parser(datestr: str) -> datetime:
    dt = __parse_date(datestr)
    if dt:
        return {'day': dt.day, 'mouth': dt.month, 'year': dt.year}
    d, m, y = None, None, None
    for substr in datestr.split(' '):
        if d is None:
            try:
                d = int(substr)
            except:
                pass
        elif m is None:
            try:
                _m = int(substr)
                if _m > 0 and _m <= 12:
                    m = _m
            except:
                pass
        else:
            try:
                y = int(substr)
                if y < 1900 and y > (datetime.now().year - 2000):
                    y += 1900
                elif y < 1900 and y < (datetime.now().year - 2000):
                    y += 2000
            except:
                pass
        if substr in MONTHS:
            m = MONTHS[substr]
    dt = {}
    if d: dt['day'] = d
    if m: dt['mouth'] = m
    if y: dt['year'] = y
    return dt