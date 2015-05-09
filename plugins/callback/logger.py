import os
import json
import datetime

TIMESTAMP_FORMAT = "%b %d %Y %H:%M:%S"
LOG_LINE = "{timestamp} {name} {msg}\n"
ANSIBLE_PER_HOST_LOG_DIR = os.environ["ANSIBLE_PER_HOST_LOG_DIR"]

DEBUG=False

def write_log(host,module_name, category, name=False,msg=False):
    if not name or not msg:
        return
    now = datetime.datetime.now()
    todays_log_dir = now.strftime("%m/%d")
    log_path = "{0}/{1}/{2}".format(ANSIBLE_PER_HOST_LOG_DIR,todays_log_dir,host)
    log_file = "{0}/ansible-{1}-{2}.log".format(log_path,module_name,category)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    fd = open(log_file, "a")
    timestamp = now.strftime(TIMESTAMP_FORMAT)
    line = LOG_LINE.format(timestamp=timestamp,name=name,msg=msg)
    fd.write(line)
    fd.close()

def log(host, category, data):
    if type(data) == dict:
        data = data.copy()
        invocation = data.pop('invocation', None)
        stdout = data.pop('stdout', None)
        stderr = data.pop('stderr', None)
        changed = data.pop('changed', None)
        msg = data.pop('msg', None)
        if DEBUG:
            print
            print "msg",msg
            print "changed",changed
            print "invocation",invocation
            print "stdout",stdout
            print "stderr",stderr
            print
            print "keys left:",data.keys()
        if invocation:
            module_name=invocation['module_name']
            module_args=invocation['module_args']
            if DEBUG:
                print "name and args"
                print module_name
                print module_args
                print "..."
        else:
            module_name='none'
        write_log(host, module_name, category, "Module name",module_name)
        write_log(host, module_name, category, "Module args",module_args)
        write_log(host, module_name, category, "Changed",changed)
        write_log(host, module_name, category, "Message",msg)
        write_log(host, module_name, category, "Stdout",stdout)
        write_log(host, module_name, category, "Stderr",stderr)
        data = json.dumps(data)
        if invocation is not None:
            rest_of_data = json.dumps(invocation) + " => %s " % data
    else:
        # if data == "..." then this means ansible skipped some task 
        if data == "...":
            print "Stuff got skipped"
        elif data.startswith("error while evaluating conditional"):
            print "Error:",data
        else:
            import sys
            print "Unexpected error"
            print "This is the data we got from ansible:"
            print data
            print
            print "Exiting now, please report this bug!"
            sys.exit(1)


class CallbackModule(object):
    """
    logs playbook results, per host, in ./log/ansible/hosts
    """

    def on_any(self, *args, **kwargs):
        pass

    def runner_on_failed(self, host, res, ignore_errors=False):
        log(host, 'FAILED', res)

    def runner_on_ok(self, host, res):
        log(host, 'OK', res)

    def runner_on_skipped(self, host, item=None):
        log(host, 'SKIPPED', '...')

    def runner_on_unreachable(self, host, res):
        log(host, 'UNREACHABLE', res)

    def runner_on_no_hosts(self):
        pass

    def runner_on_async_poll(self, host, res, jid, clock):
        pass

    def runner_on_async_ok(self, host, res, jid):
        pass

    def runner_on_async_failed(self, host, res, jid):
        log(host, 'ASYNC_FAILED', res)

    def playbook_on_start(self):
        pass

    def playbook_on_notify(self, host, handler):
        pass

    def playbook_on_no_hosts_matched(self):
        pass

    def playbook_on_no_hosts_remaining(self):
        pass

    def playbook_on_task_start(self, name, is_conditional):
        pass

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        pass

    def playbook_on_setup(self):
        pass

    def playbook_on_import_for_host(self, host, imported_file):
        log(host, 'IMPORTED', imported_file)

    def playbook_on_not_import_for_host(self, host, missing_file):
        log(host, 'NOTIMPORTED', missing_file)

    def playbook_on_play_start(self, name):
        pass

    def playbook_on_stats(self, stats):
        pass

