import streamlit as st
import requests
import pandas as pd
import math

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='北九州市の救急活動状況',
    page_icon=':ambulance:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_em_data():
    
    DATA_URI = 'https://ktq-dwh-api-cxafe3gpd2dcdjf7.japaneast-01.azurewebsites.net/emergencytransports/'
    res_data = requests.get(DATA_URI)
    datas= res_data.json()
    em_df_origin = pd.DataFrame(datas)
    em_df_ja = em_df_origin.rename(columns={'year': '年次',
                                         'Dispatch_Transport': '出動_搬送',
                                         'Type': '類型',
                                         'Number': '件数'})
    em_df = em_df_ja.replace({'Dispatch': '出動',
                              'Transport': '搬送',
                              'Traffic_accident': '交通事故',
                              'Work-related_accidents': '労働災害',
                              'General_injury': '一般負傷',
                              'Perpetrator': '加害',
                              'Self-inflicted_damage': '自損行為',
                              'Sudden_illness': '急病',
                              'Other': 'その他',})

    return em_df

em_df = get_em_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :ambulance: 北九州市の救急活動状況

[北九州市長期時系列統計](https://www.city.kitakyushu.lg.jp/shisei/menu05_0127.html)   
のウェブサイトから救急活動状況データを無料で閲覧できます。
'''

# Add some spacing
''
''

min_value = em_df['年次'].min()
max_value = em_df['年次'].max()

from_year, to_year = st.slider(
    '何年の状況を見たいですか？',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

dispatch_transport = em_df['出動_搬送'].unique()

if not len(dispatch_transport):
    st.warning("どの状況を確認したいですか？")

selected_dispatch_transport = st.selectbox(
    'どの状況を確認したいですか？',
    ('出動', '搬送'))

type = em_df['類型'].unique()

if not len(type):
    st.warning("どの類型を確認したいですか？")

selected_type = st.multiselect(
    'どの類型を確認したいですか？',
    type,
    ['交通事故', 
     '労働災害', 
     '一般負傷', 
     '加害', 
     '自損行為', 
     '急病',
     'その他'])

''
''
''

# Filter the data
filtered_em_df = em_df[
    (em_df['出動_搬送'] == (selected_dispatch_transport))
    & (em_df['類型'].isin(selected_type))
    & (em_df['年次'] <= to_year)
    & (from_year <= em_df['年次'])
]

st.header('経年の救急活動状況', divider='gray')

''

st.line_chart(
    filtered_em_df,
    x='年次',
    y='件数',
    color='類型',
)

''
''

selected_em_df = em_df[
    (em_df['出動_搬送'] == (selected_dispatch_transport))]

first_year = selected_em_df[selected_em_df['年次'] == from_year]
last_year = selected_em_df[selected_em_df['年次'] == to_year]

st.header(f'{to_year}年の救急活動', divider='gray')

''

cols = st.columns(4)

for i, types in enumerate(selected_type):
    col = cols[i % len(cols)]

    with col:
        first_number = first_year[first_year['類型'] == types]['件数'].iat[0]
        last_number = last_year[last_year['類型'] == types]['件数'].iat[0]

        if math.isnan(first_number):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_number / first_number:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{types} 件数',
            value=f'{last_number:,.0f}',
            delta=growth,
            delta_color=delta_color
        )
