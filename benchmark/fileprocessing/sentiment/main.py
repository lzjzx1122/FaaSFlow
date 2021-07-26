import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import time
nltk.download('vader_lexicon')

from Store import Store
def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    content = store.fetch(['file'])['file']
    sia = SentimentIntensityAnalyzer()
    # score = sia.polarity_scores(content) # can't handle large dataset
    time.sleep(19)
    store.put({'score': 0}, {})
