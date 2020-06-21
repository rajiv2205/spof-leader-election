import etcd3
import sys
import time
from threading import Event, Thread
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename=None)

class LeaderElection:

    def __init__(self, unique_key_name, executable_fxn, execution_interval=30):
        """
        takes key name, script and execution interval for script

        :param key_name:
        :param executable_fxn:
        :param execution_interval:

        """
        self.leader_key = unique_key_name
        self.execute_work = executable_fxn
        self.intvl = execution_interval


    def executor(self, server_name):
        """
        The main function for leader election takes the endpoint of etcd as argument, other args are also available
        for production use, like auth.
        :param server_name:
        :return:
        """

        client = etcd3.client(host='localhost', port=2379)

        while True:

            is_leader, lease = self.leader_election(client, server_name)

            if is_leader:
                logging.info('I am the leader')
                self.on_leadership_gained(lease)
            else:
                logging.info('I am a follower')
                self.waiting_next_election(client)



    def leader_election(self, client, server_name):
        """
        initialise the key with 5 sec time as expiry, can be changed
        :param client:
        :param server_name:
        :return:
        """
        logging.info('Time to elect the leader')
        try:
            lease = client.lease(5)
            is_leader = self.try_insert(client, self.leader_key, server_name, lease)
        except Exception as e:
            logging.info('unable to connect to etcd')
            sys.exit(1)
        return is_leader, lease

    def refresh_lease(self, lease):
        """
        every second leader will try to refresh the lease of key
        :param lease:
        :return:
        """
        while True:
            time.sleep(1)
            logging.info('Refreshing lease, still the leader')
            try:
                lease.refresh()
            except Exception as e:
                logging.info('connection to etcd lost')
                sys.exit(1)

    def on_leadership_gained(self, lease):
        """
        start a thread to refresh the lease of key every second and execute the user script provided with the interval
        :param lease:
        :return:
        """
        logging.info('Starting healthcheck thread')
        t1= Thread(target=self.refresh_lease, args=(lease,))
        t1.setDaemon(True)
        t1.start()

        while True:
            try:

                if t1.isAlive():
                    time.sleep(self.intvl)
                    self.execute_work()
                else:
                    logging.info('Healthcheck thread is died, exiting now')
                    sys.exit(1)
            except Exception:
                lease.revoke()
            except KeyboardInterrupt:
                logging.info('Revoking lease, no longer the leader')
                lease.revoke()
                sys.exit(1)

    def waiting_next_election(self, client):
        """
        watch for events on leader key, deletion will start re-election
        :param client:
        :return:
        """
        election_event = Event()

        def watch_callback(resp):
            for event in resp.events:
                if isinstance(event, etcd3.events.DeleteEvent):
                    logging.info('LEADERSHIP CHANGE REQUIRED')
                    election_event.set()
        watch_id = client.add_watch_callback(self.leader_key, watch_callback)

        # while we have not seen that leadership needs change, just sleep
        try:
            while not election_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:

            client.cancel_watch(watch_id)
            sys.exit(1)

        #cancel the watch, we see that election should happen again
        client.cancel_watch(watch_id)

    def try_insert(self, client, key, value, lease):
        # insert the key if not exists in etcd
        insert_succeeded, _ = client.transaction(
            failure=[],
            success=[client.transactions.put(key, value, lease)],
            compare=[client.transactions.version(key) == 0],
        )
        return insert_succeeded


def executable():
    logging.info('testing the leader-election script itself')

if __name__ == '__main__':
    server_name = sys.argv[1]
    exec_intvl = 5
    le = LeaderElection('/spof-leader-election/leader', executable, exec_intvl)
    le.executor(server_name)

