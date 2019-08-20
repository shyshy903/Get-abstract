from datetime import datetime
import requests
from bs4 import BeautifulSoup

''' Search query '''
input_search_term = input('Enter search term: ')

search_tag = input_search_term

''' Filtering '''
input_after_year = input('Enter year after: ')

if int(input_after_year) < 1935:
    print('Minimum input date is 1935...defaulting to this value')
    after_year_tag = str(1935)
elif int(input_after_year) > datetime.today().year:
    print('Maximum input date is '+str(datetime.today().year - 1)+ '...defaulting to this value')
    after_year_tag = str(2018)
elif input_after_year == '':
    after_year_tag = str(1935)
else:
    after_year_tag = input_after_year 

''' Sorting Filtered results '''
input_sort_by = input('What would you like to sort by?Please pick one of the following - mr (most relevant) or date (by date descending): ')

allowed_sort_by = ['mr','date']

if input_sort_by not in allowed_sort_by:
    print('Error! Wrong input...defaulting to relevancy')
    sort_by_tag = 'relevancy' 
elif input_sort_by == '':
    sort_by_tag = 'relevancy'
elif input_sort_by == 'mr':
    sort_by_tag = 'relevancy'
elif input_sort_by == 'date':
    sort_by_tag = 'Ppub'


journal_title = {'jams':'Journal of Academy of Marketing Science',
                  'jm':'Journal of Marketing',
                  'jmr':'Journal of Marketing Research',
                  'mktsc':'Marketing Science',
                  'mgmtsc':'Management Science'}


def url_builder(journal, search_tag, after_year_tag, sort_by_tag):
    
    if journal == 'jams':
        ''' change sort by tags for jams '''
        if sort_by_tag == 'relevancy':
            sort_by_tag2 = 'relevance'
        else:
            sort_by_tag2 = 'newestFirst'
            
        payload = {'query':search_tag,
                   'date-facet-mode':'between',
                   'facet-start-year':after_year_tag,
                   'previous-start-year':'1975',
                   'facet-end-year':'2019',
                   'previous-end-year':'2019',
                   'sortOrder':sort_by_tag2}
        
        base_url = 'https://link.springer.com/search?search-within=Journal&facet-journal-id=11747'
        
    elif journal == 'jm':
        payload = {'text1':search_tag,
                   'AfterYear':after_year_tag,
                   'sortBy':sort_by_tag}
        
        base_url = 'https://journals.sagepub.com/action/doSearch?&publication=jmxa'
        
    elif journal == 'jmr':
        payload = {'text1':search_tag,
                   'AfterYear':after_year_tag,
                   'sortBy':sort_by_tag}
        base_url = 'https://journals.sagepub.com/action/doSearch?&publication=mrja'

    elif journal == 'mktsc':
        payload = {'text1':search_tag,
                   'AfterYear':after_year_tag,
                   'sortBy':sort_by_tag}

        base_url = 'https://pubsonline.informs.org/action/doSearch?&publication[]=mksc'

    elif journal == 'mgmtsc':
        payload = {'text1':search_tag,
                   'AfterYear':after_year_tag,
                   'sortBy':sort_by_tag}

        base_url = 'https://pubsonline.informs.org/action/doSearch?&publication[]=mnsc'
    return ( requests.get(base_url, params = payload).url )    


''' Get max results for each website one by one '''

def get_max_results(journal):
    url = url_builder(journal, search_tag, after_year_tag, sort_by_tag)
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    if journal == 'mktsc':
        total_hits = soup.find('span', {'class' :'result__count'}).text
        print('Total number of results returned for',journal_title[journal],' is ',total_hits,'\n')
        return (int(total_hits))
    elif journal == 'mgmtsc':
        total_hits = soup.find('span', {'class' :'result__count'}).text
        print('Total number of results returned for',journal_title[journal],' is ',total_hits,'\n')
        return (int(total_hits))
    elif journal == 'jm':
        total_hits = soup.find('div', {'class' :'paginationStatus'}).text.split()
        print('Total number of results returned for journal',journal_title[journal],' is ',total_hits[-1],'\n')
        return (int(total_hits[-1]))
    elif journal == 'jmr':
        total_hits = soup.find('div', {'class' :'paginationStatus'}).text.split()
        print('Total number of results returned for',journal_title[journal],' is ',total_hits[-1],'\n')
        return (int(total_hits[-1]))
    elif journal == 'jams':
        total_hits = soup.find('div', {'class': 'header'}).text.split()
        print('Total number of results returned for',journal_title[journal],' is ',total_hits[0],'\n')
        return (int(total_hits[0]))




''' Get search results from other pages '''

def crawler(journal,list_of_pages):
    ''' container for search urls '''
    search_urls = []
    ''' data for the function '''
    if sort_by_tag == 'relevancy':
            sort_by_tag2 = 'relevance'
    else:
        sort_by_tag2 = 'newestFirst'
    payload = {'query':search_tag,'date-facet-mode':'between','facet-start-year':after_year_tag,'previous-start-year':'1975','facet-end-year':'2019','previous-end-year':'2019','sortOrder':sort_by_tag2}
    ''' Easier to build it this way for these journals'''
    if journal != 'jams':
        for page in list_of_pages:
            url = url_builder(journal, search_tag, after_year_tag, sort_by_tag)+'&startPage='+str(page)
            search_urls.append(url)
    else:
        modified_base_url = ['https://link.springer.com/search/page/'+str(pg)+'?search-within=Journal&facet-journal-id=11747' for pg in list_of_pages]
        for link in modified_base_url:
            url = requests.get(link, params = payload).url
            search_urls.append(url)
    return search_urls
            

''' Get abstract '''

def get_abstracts(journal,page_urls):
    if max_results > 0:
        print('\nFetching abstracts from '+journal_title[journal]+'\n')
        journal_links = []
        for url in page_urls:
            html = requests.get(url).text
            soup = BeautifulSoup(html, features="html.parser")
            if journal == 'jm' or journal == 'jmr':
                for element in soup.find_all('a',{'class':'ref nowrap'}):
                    full_link = 'https://journals.sagepub.com'+element.get('href')
                    journal_links.append(full_link)
            elif journal == 'mgmtsc' or journal == 'mktsc':
                for element in soup.find_all('h5', {'class':'hlFld-Title meta__title meta__title__margin'}):
                    full_link = 'https://pubsonline.informs.org'+element.a.get('href')
                    journal_links.append(full_link)
            elif journal == 'jams':
                for element in soup.find_all('a', {'class': 'title'}):
                    full_link = 'https://link.springer.com'+element.get('href')
                    journal_links.append(full_link)

        journal_links_required = journal_links[:int(number_needed)]
        count = 0
        for link in journal_links_required:
            count += 1
            print('Article number: '+str(count))
            html = requests.get(link).text
            soup = BeautifulSoup(html, features="html.parser")
            if journal == 'jm' or journal == 'jmr':
                if soup.find('div', {'class': 'abstractSection abstractInFull'}) is not None:
                    abs_result = soup.find('div', {'class': 'abstractSection abstractInFull'}).text
                    title = soup.find('div', {'class': 'publicationContentTitle'}).text
            elif journal == 'mgmtsc' or journal == 'mktsc':
                if soup.find('div', {'class': 'abstractSection abstractInFull'}) is not None:
                    abs_result = soup.find('div', {'class': 'abstractSection abstractInFull'}).text
                    title = soup.find('h1', {'class': 'citation__title'}).text
            elif journal == 'jams':
                if soup.find('section', {'class': 'Abstract'}) is not None:
                    abs_result = soup.find('section', {'class': 'Abstract'}).text
                    title = soup.find('h1', {'class': 'ArticleTitle'}).text
            print(title)
            print('Abstract:')
            print (abs_result)
            print('\nFind article here: '+link)    
            print('===================================================================================================================\n')
    else:
        print('There was 0 searches in '+journal_title[journal])


        

journals_to_print = input('Enter the list of journal you want to search separated by comma: ')

journals_to_print_list = [x.strip() for x in journals_to_print.split(',')]

for journal in journals_to_print_list:
    print('\nLooking up '+journal_title[journal]+'\n')
    max_results = get_max_results(journal)
    number_needed = input('Enter number of results needed: ')
    if max_results > 20 and int(number_needed) > 20:
        page_number_needed = int(( ( int(number_needed) - int(number_needed) % 10 ) / 20) + 1) 
        if journal == 'jams':
            page_nos = [x+1 for x in list(range(1, page_number_needed))]
            page_urls = [url_builder(journal, search_tag, after_year_tag, sort_by_tag)] + crawler(journal, page_nos)
            get_abstracts(journal, page_urls)
        else:
            page_nos = list(range(1, page_number_needed))
            page_urls = [url_builder(journal, search_tag, after_year_tag, sort_by_tag)] + crawler(journal, page_nos)
            get_abstracts(journal, page_urls)
    else:
        page_urls = [url_builder(journal, search_tag, after_year_tag, sort_by_tag)]
        get_abstracts(journal, page_urls)
        
        
    
    











