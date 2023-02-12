import pandas as pd
import numpy as np
from io import StringIO
import requests
import streamlit as st
import re
import ast
from functools import reduce

def init_session(session_key=None):
    if not session_key:
        if 'page' not in st.session_state:
            st.session_state['page'] = 0
        if 'region' not in st.session_state:
            st.session_state['region'] = {'US':None,'KR':None}
        if 'file_path' not in st.session_state:
            st.session_state['file_path'] = {'quotes':{'dir':None,'file':None},'news':{'dir':None,'file':None}}
        if 'git_path' not in st.session_state:
            st.session_state['git_path'] = {'api':None,'owner':None,'repo':None}
        if 'git_header' not in st.session_state:
            st.session_state['git_header'] = {'accept':None,'authorization':None}
        if 'data' not in st.session_state:
            st.session_state['data'] = {'news':pd.DataFrame(),'quotes':pd.DataFrame(),'filtered':pd.DataFrame()}

    else:
        if session_key == 'page':
            st.session_state['page'] = 0
        if session_key == 'region':
            st.session_state['region'] = {'US':'','KR':''}
        elif st.session_state == 'file_path':
            st.session_state['file_path'] = {'quotes':{'dir':None,'file':None},'news':{'dir':None,'file':None}}
        elif st.session_state == 'git_path':
            st.session_state['git_path'] = {'api':None,'owner':None,'repo':None}
        elif st.session_state == 'git_header':
            st.session_state['git_header'] = {'accept':None,'authorization':None}
        elif st.session_state == 'data':
            st.session_state['data'] = {'news':pd.DataFrame(),'quotes':pd.DataFrame(),'filtered':pd.DataFrame()}


def update_session(session_key,value,key=None):
    if session_key in st.session_state:
        # selectbox for Title
        if session_key == 'select_title':
            st.session_state.select_title = None

        # File name for region 
        elif session_key == 'region':
            if key != None:
                st.session_state.region[key] = value
            else:
                st.session_state.region = value
        # Directory and File paths
        elif session_key == 'file_path':
            if key != None:
                st.session_state.file_path[key] = value
            else:
                st.session_state.file_path = value
        # Git Crendentials and paths
        elif session_key == 'git_path':
            if key != None:
                st.session_state.git_path[key] = value
            else:
                st.session_state.git_path = value
        # Header for Git Request
        elif session_key == 'git_header':
            if key != None:
                st.session_state.git_header[key] = value
            else:
                st.session_state.git_header = value
        # Page
        elif session_key == 'page':
            st.session_state.page = value
        # Data
        elif session_key == 'data':
            if key != None:
                st.session_state.data[key] = value
            else:
                st.session_state.data = value


def init_params():
    update_session(session_key='region',value={'US':'US_topics','KR':'KR_equity'})
    update_session(session_key='file_path',key='quotes',value={'dir':st.secrets.data_dir.quotes,'file':'quotes.csv'})
    update_session(session_key='git_path',value={'api':st.secrets.git.api,'owner':st.secrets.git.owner,'repo':st.secrets.git.repo})
    update_session(session_key='git_header',value={'accept':st.secrets.header.accept,'authorization':st.secrets.header.authorization})


def read_data(path=None):
    if not path:
        path_dir = {'dir':'assets','file':'sample.txt'}
    else:
        path_dir = {'dir':None,'file':path.name}

    filename = '/'.join(filter(lambda file:file != None,path_dir.values()))

    # Check if the same data exists (already loaded)
    if '/'.join(filter(lambda file:file != None,st.session_state.file_path['news'].values())) == filename:
        return
    
    elif filename:
        init_session('page')
        init_session('data')

        regions, file_paths, git_paths, headers = st.session_state.region, st.session_state.file_path, st.session_state.git_path, st.session_state.git_header
        data = dict.fromkeys(file_paths.keys())

        for keys, paths in file_paths.items():
            for region_atr in regions.values():
                if keys == 'quotes':
                    site_request = requests.get(f"{'/'.join(git_paths.values())}/contents/{paths['dir']}{region_atr}_{paths['file']}",headers=headers)
                    string_io_obj = StringIO(site_request.text)
                    df = pd.read_table(string_io_obj,sep=",",encoding='utf-8-sig',dtype={'symbol':object,'summary':object})
                    data[keys] = pd.concat([data[keys],df])

                else:
                    # No file uploaded
                    if not path:
                        with open(filename, "r", encoding="utf-8") as file:
                            df = [line.rstrip('\n') for line in file.readlines()]
                        
                    else:
                        string_io = StringIO(path.getvalue().decode('utf-8'))
                        df = [line.rstrip('\n') for line in string_io.readlines()]

                    data[keys] = pd.DataFrame({'region':map(lambda x:'KR' if re.search(r'^[ㄱ-ㅎ가-힣]',x) else 'US',df),'headline':map(lambda x:re.search(r'(\W?\b\w+\b){,5}',x)[0].strip(),df),'text':df})
                    # Update to session file_paths
                    update_session(session_key='file_path',key=keys,value=path_dir)

            if keys == 'quotes':
                cols = ['region','symbol','name','summary']
                data[keys] = data[keys][cols]
                data[keys][['symbol','name']] = data[keys][['symbol','name']].applymap(lambda x:str(x))
                data[keys]['symbol'] = data[keys]['symbol'].apply(lambda x:x[1:] if re.search(r'\b[A-Z]\d+\b',x) else x)
                data[keys]['summary'] = data[keys]['summary'].apply(lambda x:ast.literal_eval(x))
                data[keys]['summary_compact'] = data[keys]['summary'].apply(lambda x:x['company']+x['details'])
            # Update to session data
            update_session(session_key='data',key=keys,value=data[keys])


def filter_text(keywords):
    if len(st.session_state.data['news'])>0:
        # Read session data
        data = st.session_state.data['news']
        group_cols = ['region','headline','text']
        data = data[group_cols].drop_duplicates().reset_index(drop=True)

        processed_data = pd.DataFrame()

        if keywords:
            for group in keywords:
                df = data.copy()
                dfs = map(lambda keyword:df.loc[df.text.apply(lambda x:x.lower().find(keyword.lower())!=-1)],group)
                df = reduce(lambda left,right: pd.merge(left,right), dfs)
                processed_data = pd.concat([processed_data,df])

            processed_data = processed_data.reset_index(drop=True)
            # Update session data        
            update_session(session_key='data',key='filtered',value=processed_data)

        # return processed_data


def extract_text(sel_article,keywords):
    sel_df = st.session_state.data['news'].loc[st.session_state.data['news']['headline']==sel_article].reset_index(drop=True)
    group_cols = ['region','headline','text']

    sel_text = {type:sel_df[type][0] for type in group_cols}
    symbol_df = st.session_state.data['quotes'].loc[(st.session_state.data['quotes']['region']==sel_text['region']),['symbol','summary_compact']]
    symbol_dict = {symbol:summary for symbol,summary in zip(symbol_df['symbol'],symbol_df['summary_compact'])}

    keywords = [keyword for group in keywords for keyword in group]
    symbol_dup_dict = {symbol:filter(lambda x:list(filter(lambda keyword:x.find(keyword)!=-1,keywords)),summary) for symbol,summary in symbol_dict.items()}
    symbol_dict = {symbol:summary for symbol,summary in symbol_dict.items() if summary not in symbol_dup_dict[symbol]}
    
    return sel_text, symbol_dict


def get_term_idx(keywords):
    keywords = [list(map(lambda x:x.lower(),keyword)) for keyword in keywords]
    terms_idx = {keyword.lower():None for group in keywords for keyword in group}
    for term in terms_idx:
        terms_idx[term] = [len(np.where(np.array(keyword)==term.lower())[0])>0 for idx,keyword in enumerate(keywords)].index(1)

    return terms_idx


def match_pattern(text_dict,keywords,symbol_dict):
    region, text = text_dict['region'], text_dict['text']
    
    # Keywords
    terms = [keyword for group in keywords for keyword in group]
    key_re_spans = set(map(lambda x:re.finditer(rf"\b{x.lower()}",text.lower()) if region != 'KR' else re.finditer(rf"{x.lower()}",text.lower()),terms))
    key_spans = sorted(set([span.span() for spans in key_re_spans for span in spans]))

    # Symbols
    symbol_pre_spans = {symbol:set(filter(lambda x:len(list(re.finditer(rf"\b{x.lower()}(\.?)\b",text.lower()) if region != 'KR' else re.finditer(rf"\b{x.lower()}(\w?)\b",text.lower())))>0,summary)) for symbol,summary in symbol_dict.items()}
    symbol_re_spans = {symbol:set(map(lambda x:re.finditer(rf"\b{x.lower()}(\.?)\b",text.lower()) if region != 'KR' else re.finditer(rf"\b{x.lower()}(\w?)\b",text.lower()) ,summary)) for symbol,summary in symbol_pre_spans.items()}
    symbol_re_spans = {symbol:spans for symbol,spans in symbol_re_spans.items() if len(spans)>0}
    symbol_spans = {symbol:sorted(set([span.span() for spans in summary for span in spans if span.span() not in key_spans])) for symbol,summary in symbol_re_spans.items()}

    # Filter duplicating symbols
    symbol_spans = {symbol:{span[0]:span[-1] for span in spans} for symbol,spans in symbol_spans.items()}
    symbol_spans = {symbol:{end:start for start,end in spans.items()} for symbol,spans in symbol_spans.items()}
    symbol_spans = [{symbol:[start,end]} for symbol,spans in symbol_spans.items() for end,start in spans.items()]

    return key_spans, symbol_spans


def check_iterator(iter_obj,page_num):
    try:
        text_idx, line = page_num, iter_obj.headline[page_num] #list(iter_obj)[page_num]
        return text_idx, line
    except:
        return None, ''


def process_displayc(text_dict,keywords,symbol_dict=None):
    # Get outer index
    terms_idx = get_term_idx(keywords)
    # Find spans (Keywords, Symbol)
    key_spans, symbol_spans = match_pattern(text_dict,keywords,symbol_dict)

    region, text = text_dict['region'], text_dict['text']

    ## Spans for manual Doc
    # Keywords
    spans_key = [{'start':span[0],'end':span[1],'label':f'Group #{terms_idx[text[span[0]:span[1]].lower()]+1}'} for span in key_spans]
    # Symbol
    spans_symbol = [{'start':span[0],'end':span[1],'label':symbol} for spans in symbol_spans for symbol,span in spans.items()]

    spans = spans_key+spans_symbol

    ## Labeling
    labels = sorted(set([span['label'] for span in spans]),key=lambda x:x.lower().find('group')!=-1)

    # Make output Doc
    doc = [{'text':text,'ents':spans}]

    return doc, labels


def process_sel():
    if st.session_state.select_title:
        sel_article = st.session_state.select_title
        sel_article = re.search(r'(\d+)(:\s)(.+)',sel_article).groups()
        sel_headline = sel_article[-1]
        update_session(session_key='page',value=int(sel_article[0])-1)
        update_session(session_key='select_title',value=None)


def process_btn(pages,page_num=0):
    if pages[0]:    # prev_page
        if st.session_state.page > 0:
            update_session(session_key='page',value=st.session_state.page-1)

    if pages[1]:    # next_page
        if st.session_state.page < len(st.session_state.data['filtered'])-1:
            update_session(session_key='page',value=st.session_state.page+1)

    page_num = st.session_state.page
    prev_page, next_page = False, False

    return prev_page, next_page, page_num