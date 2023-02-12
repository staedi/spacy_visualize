# spacy_visualize

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/staedi/spacy_visualize/main/app.py)

Visualization of keywords on texts using `spacy-streamlit` on [Streamlit](https://www.streamlit.io) module .
You can try [here](https://share.streamlit.io/staedi/spacy_visualize/main/app.py).


## Overall interface

[<img src="https://github.com/staedi/spacy_visualize/raw/main/images/interface.png" width="750" />](https://github.com/staedi/spacy_visualize/raw/main/images/interface.png)

The dashboard has the classic two-side design. Options to choose on the left **sidebar** and the results on the right-side **main** page.


## Usage

### Upload file to analyze
Firstly, upload a text file (`.txt`) to analyze. For simplicity, the file **SHOULD** have single column. Header (if exists) will become the first row.

Before a file is uploaded, the default file provided will be used instead.

[<img src="https://github.com/staedi/spacy_visualize/raw/main/images/upload.png" width="350" />](https://github.com/staedi/spacy_visualize/raw/main/images/upload.png)

### Enter Keywords
Keywords search allows AND and/or OR operation.
When searching the terms, case sensitivity is ignored. 

For **AND** operation, use `,` (comma) separator (w/space allowed) and for **OR** operation, use `;` (colon) separator (w/space allowed).

For example,
```
microsoft,chatgpt,ai;earning
```
will construct search terms.
```
(microsoft AND chatgpt AND ai)
OR 
(earning)
```

Be sure to type **Enter** after completing the keywords in the text box.

[<img src="https://github.com/staedi/spacy_visualize/raw/main/images/keywords-textbox.png" width="350" />](https://github.com/staedi/spacy_visualize/raw/main/images/keywords-textbox.png)

### (Optional)Restrict Keywords
Once the keywords are entered, groups of search terms are constructed and shown below.
If you like, you may unselect certain keyword from each group.

[<img src="https://github.com/staedi/spacy_visualize/raw/main/images/keywords-entered.png" width="350" />](https://github.com/staedi/spacy_visualize/raw/main/images/keywords-entered.png)

### Select Article
Once the entered search terms are processed (articles containing those terms are searched), the bottom `selectbox` populates available article to parse (Initially, set to ***None***).
Select an article you want to parse.

Be advised that once selected, the `selectbox` turns back to **None**, which is normal.

[<img src="https://github.com/staedi/spacy_visualize/raw/main/images/selectbox.png" width="350" />](https://github.com/staedi/spacy_visualize/raw/main/images/selectbox.png)

## Parsing features

### Keywords 
Basically, this visualization aims at highlighting keywords in the article. Found search terms within the article are higlighted according to their **group**, which is shown below the textbox you wrote the search terms.

### Company
Additionally, pre-populated names or relevant services or products of companies are higlighted as well. They are labelled with their **ticker** in the ***US*** (`NYSE`, `NASDAQ`) or ***KR*** (`KOSPI`, `KOSDAQ`) markets.

[<img src="https://github.com/staedi/spacy_visualize/raw/main/images/text.png" width="750" />](https://github.com/staedi/spacy_visualize/raw/main/images/text.png)
