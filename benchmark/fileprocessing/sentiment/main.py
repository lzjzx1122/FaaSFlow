import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

def main():
    content = store.fetch(['file'])['file']
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(content)
    # time.sleep(7) # if can't handle large dataset, please uncomment this to simulate sentiment processing
    store.put({'score': 0}, {})
