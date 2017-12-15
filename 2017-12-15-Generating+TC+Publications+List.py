
# coding: utf-8

# # Generate TC Publications List

# In[110]:


# import all Python libraries needed
import pandas as pd
import numpy as np
import glob
import datetime
import xlrd
import re


# We define the source file (downloaded from IFC intranet using Alberto's link). We make sure the source file is XLS (not XLSX) for the URL extraction code to work.

# In[173]:


src_file = "Copy of TC%20Related%20Publications%20from%20FY12_FY17_as%20of%20June%2020.xls"
map_file = 'TC_Publications-category_mapping.csv'
cou_file = 'CountryClassification.csv'


# define custom function for list padding

# In[ ]:


# define custom function for list padding
def pad_list(cat, max_cat_length, fillvalue=np.nan):
    return cat + [fillvalue] * (max_cat_length - len(cat))


# ## Extract URLs from "Title" column

# In[50]:


tc_pub_workbook = xlrd.open_workbook(src_file, formatting_info=True)
tc_pub_sheet = tc_pub_workbook.sheet_by_index(0)

url_list = {}
for row in range(1, tc_pub_src.nrows):
    rowValues = tc_pub_sheet.row_values(row, start_colx=0, end_colx=6)
    link = tc_pub_sheet.hyperlink_map.get((row, 1))
    url = np.nan if link is None else link.url_or_path
    url_list[row] = url
    
df_url = pd.DataFrame.from_dict(url_list, orient='index')
df_url.columns = ['URL']


# ## Convert TC Publications sheet to Dataframe + Do preprocessing
# 
# Processing code:
# - append merge extracted URL list with full publications metadata
# - clean up empty rows/columns (based on Title column)
# - clean up Abstract - replace "\r\n" with ";", and "• " with ""
# - Date Published: convert to datetime format
# - map DatascopeTopic and DatascopeSubtopic based on Category
# - extract countries from publication title using "Country Classification" columns - Country, CountryShort

# In[51]:


df_pub = pd.read_excel(src_file, sheet_name="TC Publications")

# merge extracted URL list with full publications metadata
df_pub = df_pub.join(df_url)

# clean up empty rows/columns (based on Title column)
df_pub = df_pub[df_pub['Title'].notnull()]

# clean up Abstract - replace "\r\n" with ";", and "• " with ""
df_pub['Abstract'] = df_pub['Abstract'].apply(lambda x: x.replace(r"\r\n", ";").replace("• ", ""))

# Date Published: convert to datetime format
df_pub['Date Published'] = pd.to_datetime(df_pub['Date Published'], errors='ignore')


# ### map DatascopeTopic and DatascopeSubtopic based on Category

# In[197]:


# parse Category column
cat_list = df_pub['Category'].apply(lambda topic_list: [topic.strip() for topic in topic_list.split("; ")])

# get max length of category list
max_cat_length = cat_list.apply(lambda x: len(x)).max()

for topic_col in ['DatascopeTopic', 'DatascopeSubtopic']:

    # get DatascopeTopic and DatascopeSubtopic mapping dictionaries based on Category
    dict_topic = pd.read_csv(map_file)[['Category', topic_col]].set_index('Category').to_dict()[topic_col]
    
    # pad all category lists to max length
    df_topic = pd.DataFrame(cat_list.apply(lambda topic_list: pad_list(topic_list, max_cat_length)).tolist())
    
    # map topic based on Category but if no match, put NA
    for col in df_topic.columns:
        df_topic[col] = df_topic[col].map(dict_topic)
    
    # combine all matches with semicolon separator and fill blanks with NaN
    df_pub[topic_col] = df_topic.apply(lambda x: "; ".join([val for val in x.tolist() if str(val) != 'nan']), axis=1).replace({"":np.nan})


# ## extract countries from publication title using "Country Classification" columns - Country, CountryShort

# In[199]:


# load country search query
df_cou = pd.read_csv(cou_file, encoding='latin-1')[['CountryShort','Country']]
cou_list = df_cou['CountryShort'].tolist()

# search for country search query in Title column
cou_list_series = df_pub['Title'].apply(lambda text: list(set(cou for cou in cou_list if cou in text)))

# get max length of country list
max_cou_length = cou_list_series.apply(lambda x: len(x)).max()

# load country name mapping to search query
cou_dict = df_cou.set_index('CountryShort').to_dict()['Country']


# In[204]:


# pad all country lists to max length
df_cou_searches = pd.DataFrame(cou_list_series.apply(lambda topic_list: pad_list(topic_list, max_cou_length)).tolist())

# map country based on country search query but if no match, put NA
for col in df_cou_searches.columns:
    df_cou_searches[col] = df_cou_searches[col].map(cou_dict)

# combine all matches with semicolon separator and fill blanks with NaN
df_pub['country'] = df_cou_searches.apply(lambda x: "; ".join([val for val in x.tolist() if str(val) != 'nan']), axis=1).replace({"":np.nan})


# In[206]:


df_pub.to_csv("Datascope_TnC_Publications.csv")

