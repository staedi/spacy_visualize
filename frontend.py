import generic
from datetime import datetime, date
import os
import re
import sys
import spacy_streamlit
import streamlit as st

def show_layout(type='page',data=None,layout=[.1,.6]):
    cols = st.columns(layout)
    returns = []

    if type == 'page':
        data = ['Prev Text','Next Text']

    for col_idx, col in enumerate(cols):
        with col:
            # if type == 'page':
            #     returns.append(st.button(data[col_idx],key=data[col_idx].lower().replace(' ','_')))
            if data:
                returns.append(st.button(data[col_idx],key=data[col_idx].lower().replace(' ','_')))                

    return returns


def show_table(sel_text):
    columns = ['region','symbol','name','headline']

    df_header = f"Columns | Values \n---|---\n"
    df_data = [f"***{col}*** | `{sel_text[col]}`" for col in columns]
    
    df = df_header + '\n'.join(df_data)

    st.subheader('Text Summary')
    st.markdown(df)
    st.markdown('\n')


def display_sidebar():
    with st.sidebar:
        st.subheader('Select a file to upload')
        upload = st.file_uploader('Upload',type=['txt'],key='upload')
        
        # Data
        generic.read_data(upload)

        st.subheader('Search keywords')

        # 1) Total keywords to search
        st.markdown('Enter keywords to search (Diff group: ; / Same group: ,)')
        texts = st.text_input(label='Keywords to search',key='text_keyword',value='')
        keywords = list(map(lambda x:x.split(','),re.sub(r'\s{1,}','',texts).split(';')))

        # 2) Confirm groups
        if texts:
            st.markdown('Entered keyword groups')
            groups = list(map(lambda idx:st.multiselect(label=f'Group #{idx+1}',options=keywords[idx],key=f'multiselect_{idx}',default=keywords[idx]),range(len(keywords))))

        if texts and groups:
            generic.filter_text(groups)
            filtered_data = st.session_state.data['filtered']

            if len(filtered_data)>0:
                # 3) Article collector
                st.subheader('Article selection')
                st.markdown('Select a title of the article to view')
                sel_article = st.selectbox(label='Title to view',options=[None]+filtered_data.reset_index()[['index','headline']].apply(lambda x:f'{x[0]+1}: {x[1]}',axis=1).tolist(),key='select_title',on_change=generic.process_sel)

                return groups

        return None


def display_spacy(doc,labels):
    colors = ['#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#d9d9d9','#bc80bd','#ccebc5','#ffed6f']
    symbol_cnt = len([label.lower().find('group')==-1 for label in labels])-1
    colors_dict = {label:colors[0] if label.lower().find('group')==-1 else colors[label_idx-symbol_cnt+1] for label_idx, label in enumerate(labels)}

    spacy_streamlit.visualize_ner(doc=doc,labels=labels,colors=colors_dict,show_table=False,title='',manual=True)


def process_iterator(iter_obj,page_num,groups):
    text_idx, line = generic.check_iterator(iter_obj,page_num)

    if len(line) > 0:
        st.markdown(f'Current Page: `{page_num+1}` of `{len(iter_obj)}`')
        generic.update_session(session_key='page',value=page_num)
        sel_text, symbol_dict = generic.extract_text(line,groups)
        doc, labels = generic.process_displayc(sel_text,groups,symbol_dict)
        sel_text['symbol'] = [symbol for symbol in labels if symbol.lower().find('group')==-1]
        sel_text['name'] = st.session_state.data['quotes'].loc[st.session_state.data['quotes']['symbol'].isin(sel_text['symbol']),'name'].tolist()
        show_table(sel_text)
        display_spacy(doc,labels)

        return True

    return False


def display_texts(pages,groups,page_num=0):
    prev_page, next_page, page_num = generic.process_btn(pages,page_num)
    iter_obj = st.session_state.data['filtered']
    update_status = process_iterator(iter_obj,page_num,groups)

    return prev_page, next_page, update_status