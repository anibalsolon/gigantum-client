# Copyright (c) 2018 FlashX, LLC
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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

import re
import os

from gtmcore.logging import LMLogger
logger = LMLogger.get_logger()


class CudaDriverCompatible(object):

    # this table is a simplified version of https://github.com/NVIDIA/nvidia-docker/wiki/CUDA
    #  it should cover most reasonable configurations. 
    #  To interpret this data, cuda version 10.0 requires driver > 410.58
    cuda_driver_lookup= {10: {0: (410, 58)},
                         9: {0: (384, 81),
                             1: (387, 26),
                             2: (396, 26)},
                         8: {0: (375, 51)}}
                                            
    @classmethod
    def check_version (cls, cuda_version: str ) -> bool : 
        """Method to test wheter the CUDA version and the driver
            interoperate.

            Args: 
                cuda_version: str -- something like 9.2 or 10.0

            Returns: 
                True -> yes run CUDA 
                False -> no CUDA not supported
        """
<<<<<<< HEAD
        try:
            # get driver version major/minor
            driver=os.environ['NVIDIA_DRIVER_VERSION']
            m = re.match("^([0-9]+)\.([0-9]+)$", str(driver))
            if m:
                driver_major = int(m.group(1))
                driver_minor = int(m.group(2))

                # get cuda verison major/minor
                m = re.match("^([0-9]+)\.([0-9]+)$", str(cuda_version))
                if m:
                    cuda_major = int(m.group(1))
                    cuda_minor = int(m.group(2))

                    # lookup table to check compatibility.
                    # if driver exceeds major and minor versions for this cuda, launch with cuda.
                    mindriver = CudaDriverCompatible.cuda_driver_lookup[cuda_major][cuda_minor]
                    if driver_major > mindriver[0] or \
                        (driver_major == mindriver[0] and driver_minor >= mindriver[1]):
                            return True
        except KeyError as ke:
            pass

        return False

=======
        # get cuda verison major/minor
        m = re.match("^([0-9]+)\.([0-9]+)$", str(cuda_version))
        if m:
            cuda_major = int(m.group(1))
            cuda_minor = int(m.group(2))
        else:
            return False

        # get driver version major/minor
        driver=os.environ['NVIDIA_DRIVER_VERSION']
        m = re.match("^([0-9]+)\.([0-9]+)$", str(driver))
        if m:
            driver_major = int(m.group(1))
            driver_minor = int(m.group(2))

            # lookup table to check compatibility.
            # if driver exceeds major and minor versions for this cuda, launch with cuda.
            try:
                mindriver = CudaDriverCompatible.cuda_driver_lookup[cuda_major][cuda_minor]
                if driver_major > mindriver[0] or \
                    (driver_major == mindriver[0] and driver_minor >= mindriver[1]):
                    return True
            except:
                return False

        return False                
       
>>>>>>> 4ffa1291d819583fc94dd8afd3a742eda4e0905f
