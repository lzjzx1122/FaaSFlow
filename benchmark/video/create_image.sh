# docker build --no-cache -t video_upload ../benchmark/video/upload
# docker build --no-cache -t video_simple_process ../benchmark/video/simple_process
# docker build --no-cache -t video_split ../benchmark/video/split
docker build --no-cache -t video_transcode ../benchmark/video/transcode
docker build --no-cache -t video_merge ../benchmark/video/merge