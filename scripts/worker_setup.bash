docker build --no-cache -t workflow_base ../src/container
python3 ../benchmark/generator/translator.py
../benchmark/wordcount/create_image.sh
../benchmark/fileprocessing/create_image.sh
../benchmark/illgal_recognizer/create_image.sh
../benchmark/video/create_image.sh