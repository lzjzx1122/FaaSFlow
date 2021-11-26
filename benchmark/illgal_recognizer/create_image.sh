docker build --no-cache -t recognizer_upload ~/FaaSFlow/benchmark/illgal_recognizer/upload
docker build --no-cache -t recognizer_adult ~/FaaSFlow/benchmark/illgal_recognizer/adult_detector
docker build --no-cache -t recognizer_violence ~/FaaSFlow/benchmark/illgal_recognizer/violence_detector
docker build --no-cache -t recognizer_mosaic ~/FaaSFlow/benchmark/illgal_recognizer/mosaic
docker build --no-cache -t recognizer_extract ~/FaaSFlow/benchmark/illgal_recognizer/extract
docker build --no-cache -t recognizer_translate ~/FaaSFlow/benchmark/illgal_recognizer/translate
docker build --no-cache -t recognizer_word_censor ~/FaaSFlow/benchmark/illgal_recognizer/word_censor