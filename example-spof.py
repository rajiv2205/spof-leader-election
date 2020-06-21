from leader_election import LeaderElection
import sys

def executable():
    print('I will get executed at every 5 sec')

if __name__ == '__main__':
    server_name = sys.argv[1]
    exec_intvl = 5
    le = LeaderElection('/spof-leader-election/leader', executable, exec_intvl)
    le.executor(server_name)
