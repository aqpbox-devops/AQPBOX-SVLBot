import pandas as pd

def parse_names(names: str):
    lastnames, names = names.split(', ')
    p_lastname, m_lastname = lastnames.split(' ')

    return p_lastname, m_lastname, names

def verify_gender(gender, options):
    
    """options: tuple[M, F]"""
    return options[0] if gender == 'M' else options[1] 