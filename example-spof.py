from leader_election import LeaderElection
import sys
import os

# add your shell script command with args
execute_script = 'bash ./example-shell.sh hello world'


def execute_python_script():
    """
    logic for python script

    :return:
    """
    print('executing python script')


def execute_shell_script():
    """
    logic for shell script
    :return:
    """
    print('executing shell script')
    os.system(execute_script)


def executable_type(script_type):
    """
    choose the type and execute the respective
    :param script_type:
    :return:
    """
    if script_type == 'python':
        execute_python_script()
    elif script_type == 'shell':
        execute_shell_script()
    else:
        print('not a valid script type, Exiting now...')
        sys.exit(1)


def executable():
    executable_type(exec_type)


if __name__ == '__main__':
    server_name = sys.argv[1]
    exec_type = sys.argv[2]
    exec_intvl = 5
    le = LeaderElection('/spof-leader-election/leader', executable, exec_intvl)
    le.executor(server_name)
