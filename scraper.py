from typing import Dict
from itertools import chain
from collections import Counter
import requests
from bs4 import BeautifulSoup

def main():
    news_pages_urls = get_news_pages_urls()
    if news_pages_urls is None:
        return
    print(f"INFO: {len(news_pages_urls)} news pages to read")
    if len(news_pages_urls) == 0:
        return
    counter = count_words_from_paragraphs(news_pages_urls)
    print(counter.most_common(30))


def get_news_pages_urls() -> set:
    BBC_URL = "https://www.bbc.com"
    BBC_NEWS_URL = "https://www.bbc.com/news"
    try:
        page = requests.get(BBC_NEWS_URL)
    except Exception as e:
        print(f"ERROR: get response from {BBC_NEWS_URL} failed: {e}")
        return None

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("a", class_="gs-c-promo-heading")

    # get distinct urls only for news
    news_pages_urls = set()
    for result in results:
        link = result['href']
        if "news/" not in link or "/world_radio_and_tv" in link:
            continue
        full_link = link if link.startswith("https://") else BBC_URL + link
        news_pages_urls.add(full_link)

    return news_pages_urls


def count_words_from_paragraphs(urls: set) -> Counter:
    counter = Counter()
    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all("p", class_="eq5iqo00")
        for paragraph in results:
            if not paragraph_is_promo(paragraph):
                counter += Counter(paragraph.text.split())
    return counter


def paragraph_is_promo(paragraph) -> bool:
    PROMO_CLASSES = ['ssrcss-190o9en-PromoGroupWrapper']
    classes_for_each_parent = (
        pp["class"] for pp in paragraph.parents if pp.has_attr("class")
    )
    all_parent_classes = chain.from_iterable(classes_for_each_parent)
    if any(class_name in all_parent_classes for class_name in PROMO_CLASSES):
        return True


if __name__ == "__main__":
    main()
