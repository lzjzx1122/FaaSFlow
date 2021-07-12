docker build --no-cache -t recognizer_upload upload
docker build --no-cache -t recognizer_adult adult_detector
docker build --no-cache -t recognizer_violence violence_detector
docker build --no-cache -t recognizer_mosaic mosaic
docker build --no-cache -t recognizer_extract extract
docker build --no-cache -t recognizer_translate translate
docker build --no-cache -t recognizer_word_censor word_censor