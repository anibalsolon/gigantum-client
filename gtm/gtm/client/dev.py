# Copyright (c) 2017 FlashX, LLC
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
import os
import subprocess
import shlex
import yaml
import sys
import platform
import re

from gtm.dockerutils import get_docker_client, DockerVolume
from gtm.common import get_resources_root, get_client_root


class DevClientRunner(object):
    """Class to manage using docker dev containers outside of PyCharm
    """
    def __init__(self):
        self._docker_compose_dir = os.path.join(get_resources_root(), 'developer', 'docker_compose')
        self._build_dir = os.path.join(get_client_root(), 'build', 'developer')

    def _docker_compose_exists(self) -> bool:
        """Method to check if the docker compose file has been created

        Returns:
            Bool
        """
        if os.path.exists(os.path.join(self._build_dir, 'docker-compose.yml')):
            return True
        else:
            raise IOError("docker-compose.yml missing. Did you run `gtm dev setup`?")

    def _verify_shell_config(self) -> None:
        """Method to check if the docker compose file is configured for shell based development

        Returns:
            None
        """
        with open(os.path.join(self._build_dir, 'docker-compose.yml'), 'rt') as dcf:
            data = dcf.read()

        if "PYCHARM-DEV" in data:
            # Configured for PYCHARM
            print("\n   You are currently configured for PyCharm based development")
            print("   Run the API from PyCharm to debug and test\n")
            print("   To change configuration to shell-based dev, `gtm developer setup`\n")
            sys.exit(1)

    def _get_env_vars(self) -> dict:
        """Method to get the environment variables from the docker compose file

        Returns:
            dict
        """
        data = {}
        with open(os.path.join(self._build_dir, 'docker-compose.yml'), 'rt') as dcf:
            yaml_data = yaml.load(dcf)
            yaml_data = yaml_data['services']['labmanager']['environment']

        for var in yaml_data:
            vals = var.split("=")
            data[vals[0]] = vals[1]

        return data

    def run(self) -> None:
        """Method to run Docker up on the generated docker-compose file

        Returns:
            None
        """
        if self._docker_compose_exists():
            # Make sure you are configured for "shell" debugging
            self._verify_shell_config()

            # Make sure the container-container share volume exists
            share_volume = DockerVolume("labmanager_share_vol")
            if not share_volume.exists():
                share_volume.create()

            # get the nvidia driver as available 
            if platform.system() == 'Linux':
                bash_command = "nvidia-smi --query-gpu=driver_version --format=csv,noheader --id=0"
                process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE) 
                output, error = process.communicate()
            if not error:
                m = re.match(r"([\d\.]+)", output.decode())
                nvidia_driver_version = m.group(1)
            else:                     
                nvidia_driver_version = None

            print("Running docker up. CTRL+C to exit.")
            docker_cmd = 'docker-compose -f {} run -T --service-ports labmanager'.format(
                                                                                   os.path.join(self._build_dir,
                                                                                  'docker-compose.yml'))
            cmd = f'bash -c "export NVIDIA_DRIVER_VERSION={nvidia_driver_version}; {docker_cmd}"'
            try:
                process = subprocess.run(shlex.split(cmd, posix=not platform.system() == 'Windows'),
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                print(process)
            except KeyboardInterrupt:
                print("\ndocker-compose exited")

    def attach(self) -> None:
        """Method to attach to a running dev container for debugging or interaction with the sw

        Returns:
            None
        """
        client = get_docker_client()

        containers = client.containers.list()

        container_id = None
        for container in containers:
            if "_labmanager_" in container.name:
                container_id = container.id

        if not container_id:
            print("  \nNo Client dev container running. Did you run `gtm dev start` first?\n")
            sys.exit(1)

        if self._docker_compose_exists():
            override_command = '/bin/bash -c \"cd /opt/project; echo \'-- Run /opt/setup.sh to switch to giguser context\'; /bin/bash"'
            command = 'docker exec -it {} {}'.format(container_id, override_command)
            os.system(command)
