from celeb_wiki import *
import pandas as pd

def get_nconst(Anchor_Name,Pull_Year):

  Read_Titlebasics = pd.read_table(TITLE_BASICS, sep='\t')
  Read_Namebasics = pd.read_table(NAME_BASICS, sep='\t')
  
  Read_Namebasics.primaryProfession = Read_Namebasics.primaryProfession.fillna("Null")
  filter_year = Read_Namebasics[Read_Namebasics.deathYear >= Pull_Year]
  Search_name = filter_year[filter_year.primaryName == Anchor_Name]
  if len(Search_name.index) == 1:
    for index, row in Search_name.iterrows():
      prepare_list_kft = row.knownForTitles.split(',')
      return [row.nconst,prepare_list_kft]

  else:
     
    titleakas = pd.read_table(TITLE_AKAS, sep='\t')
    titleakas.region = titleakas.region.fillna(REGION_TYPE)
    filter_region = titleakas[titleakas.region == REGION_TYPE]
    filter_region_titleid = filter_region.titleId.tolist()

    for index, row in Search_name.iterrows():
      prepare_list_kft = row.knownForTitles.split(',')
      for i in prepare_list_kft:
        take_title = Read_Titlebasics[Read_Titlebasics.tconst == i]
        if i in filter_region_titleid:
          check_genres = take_title[take_title.genres.str.contains(GENRE_TYPES)]
          if len(check_genres.index) == 1:
            return [row.nconst,prepare_list_kft]
    return [NONE]

def get_all_shows(nConst):
  chunksize = 6*10**6
  titleprincipal = pd.read_table(TITLE_PRINCIPALS, chunksize = chunksize)
  all_shows = pd.DataFrame(columns=['tconst', 'ordering', 'nconst', 'category', 'job', 'characters'])
  #Initializing with the same columns as title.principals
  for i,chunk in enumerate((titleprincipal)):
    req_shows = chunk[chunk['nconst'] == nConst]
    # print(' {} shows in chunk {}'.format(len(req_shows), i))
    all_shows = all_shows.append(req_shows, ignore_index = True)

  return all_shows.tconst.tolist()


# get final titles afters union or filter
def get_show_names(Anchor_Name,Pull_Year):
  store_US_titles = []

  store_nconst = get_nconst(Anchor_Name,Pull_Year)

  if store_nconst[0] == NONE:
    return None

  titlecrew = pd.read_table(TITLE_CREW, sep='\t')
  nconst_in_dir = titlecrew[titlecrew.directors.str.contains(store_nconst[0])]
  nconst_in_writer = titlecrew[titlecrew.writers.str.contains(store_nconst[0])]
  tconst_in_crew = list(set().union(nconst_in_dir.tconst.tolist(),nconst_in_writer.tconst.tolist()))
  Combine_list_2 = set().union(store_nconst[1],get_all_shows(store_nconst[0]),tconst_in_crew)

# Here applying US(region) filter in the shows

  titleakas = pd.read_table(TITLE_AKAS, sep='\t')
  titleakas.region = titleakas.region.fillna(REGION_TYPE)
  filter_region = titleakas[titleakas.region == REGION_TYPE]
  filter_region_titleid = filter_region.titleId.tolist()
  for x in Combine_list_2:
    if x in filter_region_titleid:
      store_US_titles.append(x)
      
  tConsts= set(store_US_titles)

  chunksize = 6*10**6

  titlebasics = pd.read_table(TITLE_BASICS, chunksize = chunksize)
  Show_Names = pd.DataFrame(columns=['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear', 'endYear', 'runtimeMinutes', 'genres'])
  for i,chunk in enumerate(titlebasics):
    show_names = chunk[chunk['tconst'].isin(tConsts)]
    print('{} shows in chunk {}'.format(len(show_names), i))
    Show_Names = Show_Names.append(show_names, ignore_index = True)
    filter_title_type = Show_Names[Show_Names['titleType']==TITLE_TYPE]
    filter_genres = filter_title_type[filter_title_type.genres.str.contains(GENRE_TYPES)]
    filter_end_year = filter_genres[filter_genres.endYear >= Pull_Year]
    filter_start_year = filter_end_year[filter_end_year.startYear.apply(str) <=Pull_Year]
  return filter_start_year

def final_show(anchor_list,Pull_Year,subtitle_file):
  X = {} #dict contains show name and their votes
  for host in anchor_list:
    print(host)
    store_show_names = get_show_names(host,Pull_Year)
    if store_show_names is None:
      title = SHOW_NOT_IN_IMDB
      if title in X:
        X[title] +=1
      else:
        X[title] = 1
    
    else:
      for title in store_show_names.primaryTitle.tolist():
        if title in X:
          X[title] +=1
        else:
          X[title] = 1

  if bool(X) is False:
    return NONE

  else:
    Max_votes = max(X.values())
    # print(Max_votes)
    Majority_Shows = [title for title, votes in X.items() if votes==Max_votes]
    if len(Majority_Shows) is 1:
      print(Majority_Shows)
      return Majority_Shows
    else:
      Open_Subtitles = open(subtitle_file)
      Read_Subtitles = Open_Subtitles.read()
      
      for show in Majority_Shows:
        if Read_Subtitles.find(show.upper())!=-1:
          return [show]   

      # for show in Majority_Shows:
      #   for network in get_majority_network(anchor_list):
      #     if show.find(network)!=-1:
      #       return [show]

def final_show_1(anchor_list,Pull_Year):
  X = {} #dict contains show name and their votes
  for host in anchor_list:
    print(host)
    store_show_names = get_show_names(host,Pull_Year)
    if store_show_names is None:
      title = SHOW_NOT_IN_IMDB
      if title in X:
        X[title] +=1
      else:
        X[title] = 1
    
    else:
      for title in store_show_names.primaryTitle.tolist():
        if title in X:
          X[title] +=1
        else:
          X[title] = 1

  if bool(X) is False:
    return NONE

  else:
    Max_votes = max(X.values())
    Majority_Shows = [title for title, votes in X.items() if votes==Max_votes]
    if len(Majority_Shows) is 1:
      return Majority_Shows
    else:
      return [NONE]
      
