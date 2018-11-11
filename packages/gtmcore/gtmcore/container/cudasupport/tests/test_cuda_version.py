# Copyright (c) 2018 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import pytest
import os

from gtmcore.container.cudasupport import CudaDriverCompatible

class TestCUDAVersion(object):
    def test_build_image_fixture(self):
        """ Check that all version checking logic works """

        """10: {0: (410, 58)},
            9: {0: (384, 81),
                1: (387, 26),
                2: (396, 26)},
            8: {0: (375, 51)}}"""   

        old_driver_version = os.environ.get('NVIDIA_DRIVER_VERSION')

        try:
            # For CUDA 8 
            os.environ['NVIDIA_DRIVER_VERSION'] = '375.51'
            assert(CudaDriverCompatible.check_version('8.0')) == True
            os.environ['NVIDIA_DRIVER_VERSION'] = '374.51'
            assert(CudaDriverCompatible.check_version('8.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '375.50'
            assert(CudaDriverCompatible.check_version('8.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '374.52'
            assert(CudaDriverCompatible.check_version('8.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '376.8'
            assert(CudaDriverCompatible.check_version('8.0')) == True
        
            # For CUDA 9.0 
            os.environ['NVIDIA_DRIVER_VERSION'] = '9.0'
            os.environ['NVIDIA_DRIVER_VERSION'] = '384.81'
            assert(CudaDriverCompatible.check_version('9.0')) == True
            os.environ['NVIDIA_DRIVER_VERSION'] = '383.81'
            assert(CudaDriverCompatible.check_version('9.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '384.80'
            assert(CudaDriverCompatible.check_version('9.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '383.82'
            assert(CudaDriverCompatible.check_version('9.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '385.8'
            assert(CudaDriverCompatible.check_version('9.0')) == True
        
            # For CUDA 9.1 
            os.environ['NVIDIA_DRIVER_VERSION'] = '387.26'
            assert(CudaDriverCompatible.check_version('9.1')) == True
            os.environ['NVIDIA_DRIVER_VERSION'] = '386.26'
            assert(CudaDriverCompatible.check_version('9.1')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '387.25'
            assert(CudaDriverCompatible.check_version('9.1')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '386.27'
            assert(CudaDriverCompatible.check_version('9.1')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '388.8'
            assert(CudaDriverCompatible.check_version('9.1')) == True

            # For CUDA 9.2 
            os.environ['NVIDIA_DRIVER_VERSION'] = '396.26'
            assert(CudaDriverCompatible.check_version('9.2')) == True
            os.environ['NVIDIA_DRIVER_VERSION'] = '395.26'
            assert(CudaDriverCompatible.check_version('9.2')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '396.25'
            assert(CudaDriverCompatible.check_version('9.2')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '395.27'
            assert(CudaDriverCompatible.check_version('9.2')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '397.8'
            assert(CudaDriverCompatible.check_version('9.2')) == True

            # For CUDA 10
            os.environ['NVIDIA_DRIVER_VERSION'] = '410.58'
            assert(CudaDriverCompatible.check_version('10.0')) == True
            os.environ['NVIDIA_DRIVER_VERSION'] = '409.58'
            assert(CudaDriverCompatible.check_version('11.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '410.57'
            assert(CudaDriverCompatible.check_version('10.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '409.59'
            assert(CudaDriverCompatible.check_version('10.0')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = '411.8'
            assert(CudaDriverCompatible.check_version('10.0')) == True

            # assert that key errors return false
            assert(CudaDriverCompatible.check_version('2.17')) == False

            # bad input for driver version and for version stroing 
            assert(CudaDriverCompatible.check_version('ab.cd')) == False
            os.environ['NVIDIA_DRIVER_VERSION'] = 'foo.bar'
            assert(CudaDriverCompatible.check_version('10.0')) == False

        finally:
            if old_driver_version:
                os.environ['NVIDIA_DRIVER_VERSION'] = old_driver_version
            else:
                del os.environ['NVIDIA_DRIVER_VERSION']
