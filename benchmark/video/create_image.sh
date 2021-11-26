docker build --no-cache -t video_upload ~/FaaSFlow/benchmark/video/upload
docker build --no-cache -t video_simple_process ~/FaaSFlow/benchmark/video/simple_process
docker build --no-cache -t video_split ~/FaaSFlow/benchmark/video/split
docker build --no-cache -t video_transcode ~/FaaSFlow/benchmark/video/transcode
docker build --no-cache -t video_merge ~/FaaSFlow/benchmark/video/merge