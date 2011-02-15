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

import os, logging

from yaybu.core.provider import Provider
from yaybu import resources

log = logging.getLogger("subversion")

class Svn(Provider):

    resource = resources.checkout.Checkout

    def action_create(self, shell):
        #FIXME: Need to work out what to do with these
        return self.action_sync(shell)

    @classmethod
    def isvalid(self, *args, **kwargs):
        return super(Svn, self).isvalid(*args, **kwargs)

    @property
    def url(self):
        return self.resource.repository + "/" + self.resource.branch

    def action_checkout(self, shell):
        if os.path.exists(self.resource.name):
            return

        log.info("Checking out %s" % self.resource)
        self.svn(shell, "co", self.url, self.resource.name)
        #self.resource.updated()

    def action_sync(self, shell):
        if not os.path.exists(self.resource.name):
            self.action_checkout(shell)
            return

        log.info("Syncing %s" % self.resource)

        changed = False

        info = self.info(shell, self.resource.name)
        repo_info = self.info(shell, self.url)

        # If the 'Repository Root' is different between the checkout and the repo, switch --relocated
        old_repo_root = info["Repository Root"]
        new_repo_root = repo_info["Repository Root"]
        if old_repo_root != new_repo_root:
            log.info("Switching repository root from '%s' to '%s'" % (old_repo_root, new_repo_root))
            self.svn(shell, "switch", "--relocate", old_repo_root, new_repo_root, self.resource.name)
            changed = True

        # If we have changed branch, switch
        old_url = info["URL"]
        new_url = repo_info["URL"]
        if old_url != new_url:
            log.info("Switching branch from '%s' to '%s'" % (old_url, new_url))
            self.svn(shell, "switch", new_url, self.resource.name)
            changed = True

        # If we have changed revision, svn up
        # FIXME: Eventually we might want revision to be specified in the resource?
        current_rev = info["Last Changed Rev"]
        target_rev = repo_info["Last Changed Rev"]
        if current_rev != target_rev:
            log.info("Switching revision from %s to %s" % (current_rev, target_rev))
            self.svn(shell, "up", "-r", target_rev, self.resource.name)
            changed = True

        #if changed:
        #    self.resource.updated()

    def action_export(self, shell):
        if os.path.exists(self.resource.name):
            return
        log.info("Exporting %s" % self.resource)
        self.svn(shell, "export", self.url, self.resource.name)
        #self.resource.updated()

    def get_svn_args(self, action, *args):
        command = ["svn", action, "--non-interactive"]

        if self.resource.scm_username:
            command.extend(["--username", self.resource.scm_username])
        if self.resource.scm_password:
            command.extend(["--password", self.resource.scm_password])
        if self.resource.scm_username or self.resource.scm_password:
            command.append("--no-auth-cache")

        command.extend(list(args))
        return command

    def info(self, shell, uri):
        command = self.get_svn_args("info", uri)
        returncode, stdout, stderr = shell.execute(command, passthru=True)
        return dict(x.split(": ") for x in stdout.split("\n") if x)

    def svn(self, shell, action, *args):
        command = self.get_svn_args(action, *args)
        return shell.execute(command)

