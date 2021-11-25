docker build --no-cache -t wc_start ../benchmark/wordcount/start
docker build --no-cache -t wc_count ../benchmark/wordcount/count
docker build --no-cache -t wc_merge ../benchmark/wordcount/merge