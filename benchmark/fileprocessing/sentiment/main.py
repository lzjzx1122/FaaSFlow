import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import time
# nltk.download('vader_lexicon')

def main():
    content = store.fetch(['file'])['file']
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(content) # can't handle large dataset
    # time.sleep(7)
    store.put({'score': 0}, {})
