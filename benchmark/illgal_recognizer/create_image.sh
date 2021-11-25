docker build --no-cache -t recognizer_upload ../benchmark/illgal_recognizer/upload
docker build --no-cache -t recognizer_adult ../benchmark/illgal_recognizer/adult_detector
docker build --no-cache -t recognizer_violence ../benchmark/illgal_recognizer/violence_detector
docker build --no-cache -t recognizer_mosaic ../benchmark/illgal_recognizer/mosaic
docker build --no-cache -t recognizer_extract ../benchmark/illgal_recognizer/extract
docker build --no-cache -t recognizer_translate ../benchmark/illgal_recognizer/translate
docker build --no-cache -t recognizer_word_censor ../benchmark/illgal_recognizer/word_censor