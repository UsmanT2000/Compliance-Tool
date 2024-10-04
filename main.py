import os
import csv
from dotenv import load_dotenv
import requests
from transformers import pipeline
import time 
from scrapper import scrape_interpol_red_notices
import sys

news_outlets = [
    "The New York Times",
    "The Washington Post",
    "BBC News",
    "CNN",
    "Reuters",
    "Al Jazeera",
    "The Guardian",
    "Bloomberg",
    "NPR",
    "Fox News",
    "The Wall Street Journal",
    "USA Today",
    "The Independent",
    "HuffPost",
    "Los Angeles Times",
    "ABC News",
    "The Atlantic",
    "Politico",
    "Time",
    "The Economist",
    "CBS News",
    "Financial Times",
    "The Telegraph",
    "The Times",
    "Slate",
    "Newsweek",
    "ProPublica",
    "Vox",
    "The Hill",
    "Business Insider",
    "Politifact",
    "Mashable",
    "The New Yorker",
    "Vice News",
    "Axios",
    "The Associated Press",
    "The Daily Beast",
    "The Spectator",
    "The Chicago Tribune",
    "Wired",
    "The Sun",
    "Express Tribune",
    "Dawn",
    "L'Express",
    "The Globe and Mail",
    "CBC News",
    "The Australian",
    "The Age",
    "The Sydney Morning Herald",
    "Financial Post",
    "The National Post",
    "The Independent (UK)",
    "The Irish Times",
    "The Times of India",
    "India Today",
    "The Hindu",
    "Dhaka Tribune",
    "The Straits Times",
    "South China Morning Post",
    "The Japan Times",
    "Asahi Shimbun",
    "The Moscow Times",
    "Russia Today (RT)",
    "Sofia Globe",
    "Al Arabiya",
    "Arab News",
    "Haaretz",
    "The Jerusalem Post",
    "Euronews",
    "Deutsche Welle (DW)",
    "RTÉ News",
    "Sky News",
    "Channel News Asia (CNA)",
    "Zee News",
    "PTI",
    "The Economic Times",
    "Forbes",
    "Fortune",
    "The Wrap",
    "The Verge",
    "TechCrunch",
    "Gizmodo",
    "Engadget",
    "CNET",
    "Mashable",
    "The Fader",
    "Billboard",
    "Variety",
    "Rolling Stone",
    "Pitchfork",
    "NME",
    "MTV News",
    "The Ringer",
    "Bleacher Report",
    "ESPN",
    "Sports Illustrated",
    "WWE",
    "The Athletic",
    "Golf Digest",
    "Outdoor Life",
    "Men's Health"
]

load_dotenv()

# Your NewsAPI key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
# Your CSE API key and CSE ID
CSE_API_KEY = os.getenv("CSE_API_KEY")
CSE_ID = os.getenv("CSE_ID")
SCRAPEOPS_API_KEY = os.getenv("SCRAPEOPS_API_KEY")

# Initialize the sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_news_about_person(person_name):
    url = 'https://newsapi.org/v2/everything'
    exact_person_name = f'"{person_name}"'  # Exact match for the person's name

    # Enhance the search query with relevant keywords
    keywords = 'discuss OR interview OR coverage OR profile'

    # Refine the query to ensure we're getting news articles
    params = {
        'q': f'{exact_person_name} AND ({keywords}) -wikipedia -twitter -reddit -blog -forum',
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 100,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        articles = response.json().get('articles', [])
        if articles:
            print(f"\nNews articles about {person_name} from NewsAPI:")
            fetched_urls = {article['url'] for article in articles}
            all_articles = []  
            
            for i, article in enumerate(articles, 1):
                article_title = article.get('title', '')
                article_description = article.get('description', '')
                
                
                if person_name.lower() in article_title.lower() or person_name.lower() in article_description.lower():
                    article_info = print_article_info(article, i)  

                    if article_info:  # Only append if article_info is not None
                        all_articles.append(article_info)  
                else:
                    print(f"Article '{article_title}' is not relevant, skipping.")

            fetch_articles_using_cse(exact_person_name, fetched_urls, all_articles)
            save_articles_to_csv(all_articles, person_name)  
        else:
            print(f"No articles found for {person_name}.")
    else:
        print(f"Failed to fetch news articles from NewsAPI: {response.status_code} - {response.text}")




def fetch_articles_using_cse(person_name, existing_urls, all_articles):
    cse_url = 'https://www.googleapis.com/customsearch/v1'
    
    
    news_outlets_query = ' OR '.join(f'"{outlet}"' for outlet in news_outlets)

    # Refine the query to include relevant terms for news articles
    refined_query = f'{person_name} AND ({news_outlets_query}) AND (news OR report OR article) -wikipedia -twitter -reddit -blog -forum -site:linkedin.com -YouTube'

    cse_params = {
        'key': CSE_API_KEY,
        'cx': CSE_ID,
        'q': refined_query,
        'num': 10  # Adjust this number to fetch more articles if needed
    }

    cse_response = requests.get(cse_url, params=cse_params)

    if cse_response.status_code == 200:
        cse_articles = cse_response.json().get('items', [])
        if cse_articles:
            print(f"\nNews articles about {person_name} from Custom Search Engine:")
            for i, article in enumerate(cse_articles, 1):
                article_url = article.get('link', None)
                if article_url and article_url not in existing_urls:
                    article_info = print_article_info(article, i, is_cse=True)
                    all_articles.append(article_info)  # Store article info for CSV
                else:
                    print(f"Article '{article.get('title')}' is already fetched from NewsAPI, skipping.")
        else:
            print(f"No additional articles found for {person_name} in Custom Search Engine.")
    else:
        print(f"Failed to fetch news articles from CSE: {cse_response.status_code} - {cse_response.text}")

def print_article_info(article, index, is_cse=False):
    source = article['source']['name'] if not is_cse else "CSE"
    title = article['title']
    url = article.get('link', None)
    description = article.get('snippet', '') if is_cse else article.get('description', '')
    content = article.get('content', '')

    # Analyze sentiment using BERT
    title_sentiment = analyze_sentiment(title)
    description_sentiment = analyze_sentiment(description)
    content_sentiment = analyze_sentiment(content)

    if not content:
        content_sentiment = 0  

    
    aggregated_sentiment = aggregate_sentiment(title_sentiment, description_sentiment, content_sentiment)

    # Convert aggregated sentiment to words
    aggregated_sentiment_word = sentiment_to_words(aggregated_sentiment)

    print(f"{index}. {title} (Source: {source})")
    print(f"   URL: {url}")
    print(f"   Description: {description}")
    print(f"   Aggregated Sentiment: {aggregated_sentiment} ({aggregated_sentiment_word})\n")

    return {
        'title': title,
        'url': url,
        'source': source,
        'description': description,
        'content': content,
        'title_sentiment': title_sentiment,
        'description_sentiment': description_sentiment,
        'content_sentiment': content_sentiment,
        'aggregated_sentiment': aggregated_sentiment,
        'aggregated_sentiment_word': aggregated_sentiment_word
    }

def analyze_sentiment(text):
    """Analyze sentiment of the given text using BERT."""
    if text: 
        result = sentiment_analyzer(text)[0] 
        sentiment_label = result['label']
        sentiment_score = result['score']
        
        # Convert sentiment labels to a polarity scale
        if sentiment_label == 'POSITIVE':
            return sentiment_score  # Positive score
        elif sentiment_label == 'NEGATIVE':
            return -sentiment_score  # Negative score
        else:
            return 0  # Neutral
    return 0  # Neutral if text is empty

def aggregate_sentiment(title_sentiment, description_sentiment, content_sentiment):
    """Calculate the average sentiment from title, description, and content."""
    count = 3  
    if content_sentiment == 0:
        count = 2
    total_sentiment = title_sentiment + description_sentiment + content_sentiment
    return total_sentiment / count  

def save_articles_to_csv(articles, person_name):
    os.makedirs('output', exist_ok=True)
    
    # Create a CSV file named after the person
    file_path = f'output/{person_name.replace(" ", "_")}_articles.csv'
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'title', 'url', 'source', 'description', 'content',
            'title_sentiment', 'description_sentiment', 'content_sentiment',  
            'aggregated_sentiment', 'aggregated_sentiment_word'  
        ])
        writer.writeheader()
        writer.writerows(articles)
    print(f"Articles saved to {file_path}")


def sentiment_to_words(sentiment):
    """Convert sentiment polarity to descriptive words."""
    if sentiment > 0.5:
        return "Very Positive"
    elif sentiment > 0:
        return "Positive"
    elif sentiment == 0:
        return "Neutral"
    elif sentiment > -0.5:
        return "Negative"
    else:
        return "Very Negative"


def check_name_in_csv(person_name, csv_filename='output/red_notices.csv'):
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Iterate over each row in the CSV
            for row in reader:
                # Remove any extra spaces and join the lines inside the 'name' field
                csv_name = " ".join(row['name'].splitlines()).strip().lower()

                if csv_name == person_name.strip().lower():
                    print(f"{person_name} is found in the Red Notices.")
                    return True

        print(f"{person_name} is not found in the Red Notices.")
        os.remove(csv_filename)
        return False
    except FileNotFoundError:
        print(f"The file {csv_filename} does not exist.")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        person_name = sys.argv[1]
    else:
        person_name = input("Enter the name of the person to search for: ")
    fetch_news_about_person(person_name)
    scrape_interpol_red_notices()
    check_name_in_csv(person_name)