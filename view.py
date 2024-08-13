import pandas as pd

#data = pd.read_excel('datos_excel.xlsx')

"""print(data.head())
print(data.info())
print(type(data.loc[1]['NOMBRES']))

employee_credentials = data.loc[0]
lastnames, names = employee_credentials['NOMBRES'].split(', ')
p_lastname, m_lastname = lastnames.split(' ')
print(p_lastname, m_lastname, names)

print(employee_credentials['SEXO'])"""

data = pd.read_excel('datos.xlsx')
#print(data.groupby(data[''])
print(data.head())
print(data.info())
print(data['FECHA DE NACIMIENTO'].dtype)
fil = data.filter(like='NRO DE DOCUMENTO', axis=1)
print(fil)
data = data.groupby(fil.columns[0])
print(data.head())

primera_mitad = data.iloc[:mitad]
segunda_mitad = data.iloc[mitad:].copy()

