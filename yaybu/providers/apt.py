# Copyright 2011 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from yaybu.core import provider
from yaybu import resources

class Apt(provider.Provider):

    policies = (resources.package.PackageInstallPolicy,)

    @classmethod
    def isvalid(self, *args, **kwargs):
        return super(Execute, self).isvalid(*args, **kwargs)

    def apply(self, shell):
        command = ["apt-get", "install", "-q", "-y", self.resource.name]
        returncode, stdout, stderr = shell.execute(command)

        if returncode != 0:
            raise RuntimeError("%s failed with return code %d" % (self.resource, returncode))
