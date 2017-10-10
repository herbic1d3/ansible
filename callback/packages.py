# -*- coding: utf-8 -*-

import sys
import json

from ansible.cli.playbook import PlaybookCLI
from ansible.playbook import Playbook
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

response = {}

class CallbackModule(CallbackBase):
    def __init__(self):
        super(CallbackModule, self).__init__()

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if not 'error' in response:
            response['error'] = {}
        response['error'] = {str(result._host): ''.join(result._result['stderr'])}

    def v2_runner_on_ok(self, result):
        if result._result['changed']:
            for line in result._result['stdout_lines']:
                pkg, version = line.split('==')
                response[pkg] = version

class General(object):
    def __init__(self):
        self.cli = PlaybookCLI(sys.argv, callback=CallbackModule)
        self.cli.parse()

    def run(self):
        sshpass = None
        becomepass = None
        passwords = {}

        if not self.cli.options.listhosts and not self.cli.options.listtasks and not self.cli.options.listtags and not self.cli.options.syntax:
            self.cli.normalize_become_options()
            (sshpass, becomepass) = self.cli.ask_passwords()
            passwords = {'conn_pass': sshpass, 'become_pass': becomepass}

        loader, inventory, variable_manager = self.cli._play_prereqs(self.cli.options)

        for playbook_path in self.cli.args:
            pb = Playbook.load(playbook_path, variable_manager=variable_manager, loader=loader)
            plays = pb.get_plays()

            for play in plays:
                tqm = None
                try:
                    tqm = TaskQueueManager(
                        inventory=inventory,
                        variable_manager=variable_manager,
                        loader=loader,
                        options=self.cli.options,
                        passwords=passwords,
                        stdout_callback=CallbackModule(),
                    )
                    tqm.run(play)
                finally:
                    if tqm is not None:
                        tqm.cleanup()


def main():
    app = General()
    app.run()
    sys.stdout.write("{}\n".format(
        json.dumps(response)
    ))


if __name__ == '__main__':
    main()
