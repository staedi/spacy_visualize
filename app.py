import frontend
import generic
import streamlit as st

if __name__ == '__main__':
    # Initialize
    generic.init_session()
    generic.init_params()
    # Sidebar
    groups = frontend.display_sidebar()
    if groups:
        pages = frontend.show_layout(type='page')
        prev_page, next_page, update_status = frontend.display_texts(pages=pages,groups=groups)