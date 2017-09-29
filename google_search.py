import os
import sys
import csv
import random
from time import sleep
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from bs4 import BeautifulSoup


def filter_result(link):
    try:
        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urlparse(link, 'http')
        if o.netloc and 'google' not in o.netloc:
            return link

        # Decode hidden URLs.
        if link.startswith('/url?'):
            link = parse_qs(o.query)['q'][0]

            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
        return None

def get_links(url):
    # article_links = []
    driver =  webdriver.Chrome(executable_path=os.path.join(cur_dir, 'driver', 'chromedriver.exe'))

    driver.maximize_window()
    driver.set_page_load_timeout(600)

    base_url = url + "&start=%s"
    start = 0
    while True:
        url = base_url %str(start)
        print (url)
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        anchors = soup.find(id='search').findAll('a')
        page_links = []
        for anchor in anchors:
            link = anchor.get('href')
            link = filter_result(link)
            if not link:
                continue
            if link in page_links:
                continue

            page_links.append(link)

        if not soup.find(id='pnnext'):
            break

        yield page_links

        start += 10

        sleep(random.randint(5,10))

    # return article_links

def get_bloombergArticle(url):
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.content, 'html.parser')
    article_name = url.split("/")[-1]
    title = soup.find('span', attrs={'class':'lede-text-only__highlight'}).text.strip()
    headline = "\n".join(filter(None, [item.strip() for item in soup.find('ul', attrs={'class':'abstract'}).text.split("\n")]))
    article = soup.find('div', attrs={'class':'body-copy'}).text.strip()

    published_date = soup.find(itemprop='datePublished').get('datetime')
    try:
        updated_date = soup.find(itemprop='dateModified').get('datetime')
    except:
        updated_date = ""

    with open(os.path.join('articles', article_name+".txt"), 'w') as f:
        f.write(article)

    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([article_name, title+"\n"+headline, published_date, updated_date])


def main():
    home_url = 'https://www.google.com/search?safe=off&hl=en&dcr=0&biw=1920&bih=974&tbs=cdr:1,cd_min:%s,cd_max:%s&tbm=nws&q=%s' %(start_date, end_date, query_string)
    article_links = get_links(home_url)
    for page_links in article_links:
        for article_link in page_links:
            print (article_link)
            get_bloombergArticle(article_link)


if __name__ == "__main__":
    query_string = '"markets+wrap"+in+site:bloomberg.com'
    cur_dir = os.path.dirname(os.path.realpath(__file__))

    # start_date = "1/1/2017"
    # end_date = "9/29/2017"
    try:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    except:
        print("Invalid Command.\n\tFormat: python google_search.py [start date] [end date]\n\tex: python google_search.py 9/1/2017 9/29/2017")
        sys.exit(2)

    csv_file = start_date.replace("/", "-")+"_"+end_date.replace("/", "-")+".csv"

    if not os.path.exists("articles"):
        os.mkdir('articles')

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['article', 'headlines', 'published_date', 'updated_date'])

    main()
    # article_link = "https://www.bloomberg.com/news/articles/2017-09-14/yen-jumps-after-report-of-north-korea-missile-markets-wrap"
    # get_bloombergArticle(article_link)