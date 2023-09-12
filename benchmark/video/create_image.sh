docker build --no-cache -t workflow_video_base ~/FaaSFlow/benchmark/template_functions/video__base
docker build --no-cache -t video__upload ~/FaaSFlow/benchmark/template_functions/video__upload
docker build --no-cache -t video__split ~/FaaSFlow/benchmark/template_functions/video__split
docker build --no-cache -t video__group0 ~/FaaSFlow/benchmark/template_functions/video__group0
docker build --no-cache -t video__transcode ~/FaaSFlow/benchmark/template_functions/video__transcode
docker build --no-cache -t video__merge ~/FaaSFlow/benchmark/template_functions/video__merge
docker build --no-cache -t video__simple_process ~/FaaSFlow/benchmark/template_functions/video__simple_process

