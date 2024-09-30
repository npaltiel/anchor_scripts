import pandas as pd

leads = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Marketer Leads\\Test CSV.csv")
leads.fillna("", inplace=True)

a = {}
b = {}
c = {}
d = {}
e = {}
f = {}

for i in range(len(leads)):
    medicaid = leads['Medicaid ID'][i].lower()
    if medicaid not in a:
        a[medicaid] = leads.iloc[i]
    elif medicaid not in b:
        b[medicaid] = leads.iloc[i]
    elif medicaid not in b:
        c[medicaid] = leads.iloc[i]
    elif medicaid not in b:
        d[medicaid] = leads.iloc[i]
    elif medicaid not in b:
        e[medicaid] = leads.iloc[i]
    else:
        f[medicaid] = leads.iloc[i]


for lead in a:
    for i in range(len(a[lead])):
        first = a[lead][i]
        second = b[lead][i]
        third = False
        fourth = False
        fifth = False
        sixth = False
        if lead in c:
            third = c[lead][i]
        if lead in d:
            fourth = d[lead][i]
        if lead in e:
            fifth = e[lead][i]
        if lead in f:
            sixth = f[lead][i]
        if not first:
            if second:
                a[lead][i] = second
            elif third:
                a[lead][i] = third
            elif fourth:
                a[lead][i] = fourth
            elif fifth:
                a[lead][i] = fifth
            elif sixth:
                a[lead][i] = sixth

# Convert the dictionary to a DataFrame
df = pd.DataFrame.from_dict(a, orient='index')

# Reset index to make the Medicaid ID a column
df = df.reset_index().rename(columns={'index': 'Medicaid_ID'})

# Display the resulting DataFrame
print(df)

df.to_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Marketer Leads\\Output CSV.csv", index=False)  # index=False to avoid saving the DataFrame's index as a separate column
