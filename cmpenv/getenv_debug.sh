printenv > org.sh
# get file directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# print current dir
echo "Current directory: $DIR"
VULKAN_SIM_ROOT_DIR="$(realpath $DIR/../..)"
echo "Vulkan simulation root directory: $VULKAN_SIM_ROOT_DIR"
export CUDA_INSTALL_PATH="/usr/local/cuda-11.8"
cd $VULKAN_SIM_ROOT_DIR/embree-3.13.4.x86_64.linux
source embree-vars.sh
cd $VULKAN_SIM_ROOT_DIR/vulkan-sim
source setup_environment debug
export VK_DRIVER_FILES="$VULKAN_SIM_ROOT_DIR/mesa-vulkan-sim/lib/share/vulkan/icd.d/lvp_icd.x86_64.json"
cd $DIR
printenv > later.sh

cd $DIR && python3 compare.py