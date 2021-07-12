docker build --no-cache -t workflow_base ../src/container
docker build --no-cache -t image_invalid ../examples/switch/functions/invalid
docker build --no-cache -t image_sqrt ../examples/switch/functions/sqrt
docker build --no-cache -t image_sub ../examples/switch/functions/sub
