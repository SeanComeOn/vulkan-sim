printenv > org.sh
cd .. && export CUDA_INSTALL_PATH=/usr/local/cuda-11.8 && source setup_environment && cd cmpenv && printenv > later.sh
python3 compare.py