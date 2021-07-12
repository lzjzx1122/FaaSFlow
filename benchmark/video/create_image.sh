docker build --no-cache -t video_upload upload
docker build --no-cache -t video_simple_process simple_process
docker build --no-cache -t video_split split
docker build --no-cache -t video_transcode transcode
docker build --no-cache -t video_merge merge