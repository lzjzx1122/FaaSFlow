docker build --no-cache -t wc_start ~/FaaSFlow/benchmark/wordcount/start
docker build --no-cache -t wc_count ~/FaaSFlow/benchmark/wordcount/count
docker build --no-cache -t wc_merge ~/FaaSFlow/benchmark/wordcount/merge