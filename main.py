import pandas as pd
import re

df = pd.read_excel('data.xlsx', sheet_name=None)

for key, value in df.items():
    print(key)
    print(value.info())

employers = df['Trabajadores']
gender = df['Sexo']
beneficiers = df['Familiares']
addresses = df['Direccion del trabajador']

def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'[^0-9a-zA-Z\s]', '', text).strip()
    return text

def process_doc(doc):
    doc = str(doc)
    if doc.isdigit():
        return str(int(doc))
    else:
        return str(doc)

employers['DOCUMENTO_IDENTIDAD'] = employers['DOCUMENTO_IDENTIDAD'].apply(lambda x: process_doc(x.split(' - ')[1]))
beneficiers['DNI COLABORADOR'] = beneficiers['DNI COLABORADOR'].apply(process_doc)

filtered_beneficiers = employers.merge(beneficiers, left_on='DOCUMENTO_IDENTIDAD', right_on='DNI COLABORADOR')

addresses_relevant = addresses[['TIPO_DOCUMENTO', 'NRO_DOCUMENTO', 'DIRECCION_TRABAJADOR', 'UBIGEO']]

ubigeo_split = addresses_relevant['UBIGEO'].str.split(' - ', expand=True)
addresses_relevant = addresses_relevant.assign(
    DEPARTAMENTO=ubigeo_split[0],
    PROVINCIA=ubigeo_split[1],
    DISTRITO=ubigeo_split[2]
)

addresses_relevant = addresses_relevant.assign(
    DEPARTAMENTO=addresses_relevant['DEPARTAMENTO'].apply(clean_text),
    PROVINCIA=addresses_relevant['PROVINCIA'].apply(clean_text),
    DISTRITO=addresses_relevant['DISTRITO'].apply(clean_text),
    NRO_DOCUMENTO=addresses_relevant['NRO_DOCUMENTO'].apply(process_doc)
)

fully_addresses = addresses_relevant[['TIPO_DOCUMENTO', 'NRO_DOCUMENTO', 'DIRECCION_TRABAJADOR', 'DEPARTAMENTO', 'PROVINCIA', 'DISTRITO']]

result = filtered_beneficiers.merge(fully_addresses, left_on='DOCUMENTO_IDENTIDAD', right_on='NRO_DOCUMENTO', how='left')
result = result.fillna("")

gender['NUMERO DE DOCUMENTO BENEFICIARIO'] = gender['NUMERO DE DOCUMENTO'].apply(process_doc)
result['DNI FAMILIAR'] = result['DNI FAMILIAR'].apply(lambda x: process_doc(clean_text(str(x))))

print(gender.info())
print(result.info())

result = result.merge(gender, left_on='DNI FAMILIAR', right_on='NUMERO DE DOCUMENTO BENEFICIARIO', how='left')
result = result.fillna("")

result.to_excel('result.xlsx')