docker build --no-cache -t workflow_base ../container
docker build --no-cache -t image_add ../../examples/foreach/functions/add
docker build --no-cache -t image_rand ../../examples/foreach/functions/rand
docker build --no-cache -t image_square ../../examples/foreach/functions/square
