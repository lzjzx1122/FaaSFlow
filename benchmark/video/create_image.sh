docker build --no-cache -t workflow_video_base ~/CodeLess/benchmark/template_functions/video__base
docker build --no-cache -t video__upload ~/CodeLess/benchmark/template_functions/video__upload
docker build --no-cache -t video__split ~/CodeLess/benchmark/template_functions/video__split
docker build --no-cache -t video__group0 ~/CodeLess/benchmark/template_functions/video__group0
docker build --no-cache -t video__transcode ~/CodeLess/benchmark/template_functions/video__transcode
docker build --no-cache -t video__merge ~/CodeLess/benchmark/template_functions/video__merge
docker build --no-cache -t video__simple_process ~/CodeLess/benchmark/template_functions/video__simple_process

