import wikipedia as wiki
import pandas as pd
import os

GENRE_TYPES = 'Talk-Show|News'
TITLE_TYPE = 'tvSeries'
PROFESSION_TYPES =  [' host',' presenter',' journalist',' news anchor','correspondent',' anchor']
SPLIT_TYPES = [' is a ',' is an ',' was a ',' was an ',' is the ']
NONE = 'Not Found'
PAGE_ERROR = 'does not match any pages'
DISAMBIGUATION_ERROR = 'disambiguation'
NETWORK_TYPES = ['FOX','ABC','CBS','NBC','CNN','United Paramount Net','Warner Bros.','Pure Independent','PBS','Pax TV','Telemundo']
REGION_TYPE = 'US'
SHOW_NOT_IN_IMDB = 'Show is not present in IMDb'
NAME_BASICS = "IMDB_Datasets/name.basics.tsv/data.tsv"
TITLE_BASICS = "IMDB_Datasets/title.basics.tsv/data.tsv"
TITLE_PRINCIPALS = "IMDB_Datasets/title.principals.tsv/data.tsv"
TITLE_AKAS = "IMDB_Datasets/title.akas.tsv/data.tsv"
TITLE_CREW = "IMDB_Datasets/title.crew.tsv/data.tsv "
Read_Namebasics = pd.read_table(NAME_BASICS, sep='\t')

""" After getting all professions of a person we can easily confirm that
    our previous top 5 prediction is right or not & by using this we find 
    correct anchor.
"""       

def get_wiki_professions(Anchor_Name):

  if len(wiki.search(Anchor_Name)) == 0:
    return NONE

  Store_name = Read_Namebasics.primaryName.tolist()

  try:
    if Anchor_Name in Store_name:
      anchor_content = (((wiki.page(Anchor_Name,auto_suggest=False)).content).replace(' and ',', ').replace('.','. '))
    else:
      return NONE

  except wiki.exceptions.PageError as p:
    if PAGE_ERROR in str(p):
      return NONE

  except wiki.exceptions.DisambiguationError as e:
    if Anchor_Name in Store_name:
      list_disambiguation_error = e.options

      for i in list_disambiguation_error:
        if i.find(DISAMBIGUATION_ERROR)!= -1:
          return NONE

        anchor_content = (((wiki.page(i,auto_suggest=False)).content).replace(' and ',', ').replace('.','. '))
        split_type_list = []
        prefix = None
        for x in SPLIT_TYPES:
          if x in anchor_content:
            prefix = x
            split_type_index = anchor_content.find(prefix)
            split_type_list.append(split_type_index)
          else:
            split_type_list.append(1000)

        if prefix is None:
          return NONE
          
        low_index = SPLIT_TYPES[split_type_list.index(min(split_type_list))]   
        final_split = anchor_content.split(low_index)[1].split('. ')[0].split(', ')
        final_professions = [anchor_content.lower() for anchor_content in final_split]
        required_professions = PROFESSION_TYPES

        check_individual_prof = []
        for x in required_professions:
          final_check= [(x in y) for y in final_professions]
          check_individual_prof.append(any(final_check))
        
        if (any(check_individual_prof)==True):
          return final_professions
      else:
        return NONE
    
    else:
      return NONE     
  
  split_type_list = []
  prefix = None
  for x in SPLIT_TYPES:
    if x in anchor_content:
      prefix = x
      split_type_index = anchor_content.find(prefix)
      split_type_list.append(split_type_index)
    else:
      split_type_list.append(1000)

  low_index = SPLIT_TYPES[split_type_list.index(min(split_type_list))]
    
  if prefix is None:
    return NONE

  final_split = anchor_content.split(low_index)[1].split('. ')[0].split(', ')
  final_professions = [anchor_content.lower() for anchor_content in final_split]
  return final_professions

def check_wiki_professions(list_profession):
  required_professions = PROFESSION_TYPES

  check_individual_prof = []
  for x in required_professions:
    final_check= [(x in y) for y in list_profession]
    check_individual_prof.append(any(final_check))
  
  if (any(check_individual_prof)==True):
    return True
  else:
    return False

"""  From top 5 anchor we get most probable anchor in that show
     Make sure that the input anchors list follows given format. Here's an example
     Anchor_list = "Colleen-Williams_Ashwini-Bhave_Elaine-Quijano_Becky-Hobbs_Heidi-Collins"
"""
def get_correct_anchor(top_5):
  top_5_list = (top_5.replace('-',' ').replace('_',',')).split(',')
  top_5_list = list(filter(None, top_5_list))
  
  for x in top_5_list:
    if check_wiki_professions(get_wiki_professions(x)) is True:
      Read_Namebasics = pd.read_table(NAME_BASICS, sep='\t')
      Store_name = Read_Namebasics.primaryName.tolist()
      if x in Store_name:
        return x 
     
  return '' 

## get finals anchors from the multiple probable hosts

def Final_Anchor(last_line):
  filter_probable_list = []

  ## Here all_lines[len(all_lines)-1] == put from last year code
  
  last_line_anchors = last_line.split('ANC|')[1].split('\n')[0].replace(' ','')
  
  # print(last_line)
  avoid_num = ''.join([i for i in last_line_anchors if not i.isdigit()])
  probable_host_list = avoid_num.split('probable_host:')
  probable_host_list = list(filter(None, probable_host_list))

  # print(probable_host_list)

  for i in probable_host_list:
    filter_probable_list.append(get_correct_anchor(i))
    filter_probable_list = list(filter(None, filter_probable_list))
  return filter_probable_list


#this will give us network name either from anchor or show

def get_channel(name):
  try:
    anchor_content = ((((wiki.page(name,auto_suggest=False)).content).replace(' and ',', ').replace('.','. ')))
  
  except wiki.exceptions.PageError as p:
    if PAGE_ERROR in str(p):
      return NONE
  
  except wiki.exceptions.DisambiguationError as e:
    list_disambiguation_error = e.options
    for anchor_name in list_disambiguation_error:
      if anchor_name.find(DISAMBIGUATION_ERROR)!= -1:
        return NONE
      
      else:
        anchor_content = ((((wiki.page(anchor_name,auto_suggest=False)).content).replace(' and ',', ').replace('.','. ')))

  Networks_list = NETWORK_TYPES
  Network_filter = []
    
  for network in Networks_list:
    if anchor_content.find(network)!=-1:
      Network_filter.append(network)
  return Network_filter

def get_majority_network(anchors_list):
  list_of_network = []
  for anchorlist in anchors_list:
    for anchor in anchorlist:
      list_of_network.append(get_channel(anchor))
  list_of_network = list(filter(None,list_of_network))
  # print(list_of_network)

  X ={} #dict contains networks and respected votes 
  for network in list_of_network:
    for particular in network:
      if particular in X:
        X[particular] +=1
      else:
        X[particular] = 1   
  Max_votes = max(X.values())
  Majority_Network = [particular for particular, votes in X.items() if votes == Max_votes]
  return Majority_Network
