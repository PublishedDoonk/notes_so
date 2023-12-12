import PyPDF2
import os
import nltk
import re
import json
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def read_all_pdfs(path: str):
    '''Returns a list of all pdfs in a given path'''
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".pdf")]

def get_pages(path: str):
    '''Returns text from all pages in a given pdf as a list'''
    reader = PyPDF2.PdfReader(path)
    pages = [i.extract_text() for i in reader.pages]
    return pages

def retrieve_pdfs(path: str):
    '''Returns a list of all pdfs in a given path and its subfolders'''
    if not os.path.exists(path):
        os.makedirs(path)
        return []
    
    subfolders = [os.path.join(path, dir) for dir in os.listdir(path) if os.path.isdir(os.path.join(path, dir))]
    pdfs = read_all_pdfs(path)
    
    for subfolder in subfolders:
        pdfs = pdfs + read_all_pdfs(subfolder)
    
    return pdfs

def get_search_terms(query: str):
    '''Returns a set of search terms from a given query'''
    query = re.sub(r'[^\w\s]', '', query)
    stop_words = set(stopwords.words('english'))
    terms = word_tokenize(query)
    return {w.lower() for w in terms if w.lower() not in stop_words}

def get_hits(page: str, terms: set):
    '''Returns the number of hits for a given page and set of search terms'''
    lower_page = [w.lower() for w in page.split(' ')]
    return sum([lower_page.count(i) + 10 for i in terms if lower_page.count(i) > 0])

def check_data():
    '''Creates data dir if it doesn't exist'''
    if not os.path.exists('data') or not os.path.isdir('data'):
        os.makedirs('data')
    

def get_processed():
    '''Returns a list of all processed page names'''
    check_data() # makes data dir if not already made
    
    if not os.path.exists('data/processed.json'):
        open('data/processed.json', 'w').close()
        return []
    
    return json.load(open('data/processed.json', 'r'))

def get_page_data():
    '''Returns a list of all processed page data'''
    if not os.path.exists('data/pages_data.json'):
        open('data/pages_data.json', 'w').close()
        return []
    
    return json.load(open('data/pages_data.json', 'r'))

def load_page_data(pdfs: list):
    processed = get_processed()
    page_data = get_page_data()
    
    for p in pdfs:
        # skip if already processed
        if p in processed:
            print('Skipping:', p[:25], '...')
            continue
        processed.append(p)
        print('Processing:', p[:25], '...')
        pages = get_pages(p)
        for i in range(len(pages)):
            print('Processing page', i+1,'of', len(pages))
            filename = os.path.basename(p)[:-4].replace('_', ' ').title() + ' - pg: ' + str(i+1)
            page_data.append({'filename': filename, 'page': pages[i], 'path': p})
    
    # save processed list
    with open('data/processed.json', 'w') as f:
        json.dump(processed, f)
    
    return page_data

def process_pdfs(pdfs: list):
    '''Processes all pdfs in a given list and saves the results to pages_data.json'''
    page_data = load_page_data(pdfs)
    
    os.system('cls') #clear screen on windows
    print('Successfully processed', len(page_data), 'pages from', len(pdfs), 'pdfs!')
    
    with open('data/pages_data.json', 'w') as f:
        json.dump(page_data, f)
    print('Saved as data/pages_data.json')

def sort_results(results: dict, num: int = -1):
    if num == -1:
        num = len(results)
    return list(dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:num]).keys())

def display_results(results):
    if len(results) == 0:
        print('Sorry. No results found.')
    else:
        top_results = sort_results(results)
        print('Top results saved to results.md')
        with open('results.md', 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(['# Top Results'] + top_results))

def start():
    print('Enter search queries to find notes!')
    sel = ''
    while True:
        #get user query
        sel = input('Enter search query (q to quit): ').lower().strip()
        if sel == 'q' or sel == 'quit':
            return
        
        #load page data, get search terms, and initialize results
        page_data = json.load(open('data/pages_data.json', 'r'))
        terms = get_search_terms(sel)
        results = {}
        
        # Finds all pages with hits and highlights the search terms
        for page in page_data:
            hits = get_hits(page['page'], terms)
            if hits > 0:
                for term in terms:
                    page['page'] = re.sub(term, '<mark style="background-color: #FFFF00">' + term.upper() + '</mark>', page['page'], flags=re.IGNORECASE)
                result = '## <a href="file:\\\\\\' + os.path.abspath(page['path']).replace(' ', '%20') + '#page=' + page['filename'].split(':')[-1].strip() + '">' + page['filename'] + '</a>\nhits: ' + str(hits) + '\n' + page['path'] + '\n\n' + page['page']
                results[result] = hits
        
        display_results(results)

def main():
    pdfs = retrieve_pdfs('PDF Resources')
    process_pdfs(pdfs)
    #tk_init()
    start()

if __name__ == "__main__":
    main()
