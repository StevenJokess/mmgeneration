# Copyright (c) OpenMMLab. All rights reserved.
import os.path as osp
import subprocess
import sys
from collections import defaultdict

import cv2
import mmcv
import torch
import torchvision
from mmcv.utils import get_build_config, get_git_hash

import mmgen


def collect_env():
    """Collect the information of the running environments."""
    env_info = {}
    env_info['sys.platform'] = sys.platform
    env_info['Python'] = sys.version.replace('\n', '')

    cuda_available = torch.cuda.is_available()
    env_info['CUDA available'] = cuda_available

    if cuda_available:
        from mmcv.utils.parrots_wrapper import CUDA_HOME
        env_info['CUDA_HOME'] = CUDA_HOME

        if CUDA_HOME is not None and osp.isdir(CUDA_HOME):
            try:
                nvcc = osp.join(CUDA_HOME, 'bin/nvcc')
                nvcc = subprocess.check_output(
                    '"{}" -V | tail -n1'.format(nvcc), shell=True)
                nvcc = nvcc.decode('utf-8').strip()
            except subprocess.SubprocessError:
                nvcc = 'Not Available'
            env_info['NVCC'] = nvcc

        devices = defaultdict(list)
        for k in range(torch.cuda.device_count()):
            devices[torch.cuda.get_device_name(k)].append(str(k))
        for devname, devids in devices.items():
            env_info['GPU ' + ','.join(devids)] = devname

    gcc = subprocess.check_output('gcc --version | head -n1', shell=True)
    gcc = gcc.decode('utf-8').strip()
    env_info['GCC'] = gcc

    env_info['PyTorch'] = torch.__version__
    env_info['PyTorch compiling details'] = get_build_config()

    env_info['TorchVision'] = torchvision.__version__

    env_info['OpenCV'] = cv2.__version__

    env_info['MMCV'] = mmcv.__version__
    env_info['MMGen'] = f'{ mmgen.__version__ }+{get_git_hash()[:7]}'
    try:
        from mmcv.ops import get_compiler_version, get_compiling_cuda_version
        env_info['MMCV Compiler'] = get_compiler_version()
        env_info['MMCV CUDA Compiler'] = get_compiling_cuda_version()
    except ImportError:
        env_info['MMCV Compiler'] = 'n/a'
        env_info['MMCV CUDA Compiler'] = 'n/a'

    return env_info


if __name__ == '__main__':
    for name, val in collect_env().items():
        print('{}: {}'.format(name, val))
