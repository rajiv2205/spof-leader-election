# spof-leader-election

No more Single Point Of Failure for scheduled python scripts. Run multiple replicas of python script without worrying about duplicacy and its failover. It uses etcd for leader-election so that you can run multiple replicas of your script and if leader goes down then only one of the replica will take over and start working. Once the old leader is back, it will join the cluster as a follower.

Interesting!!! Keep reading to use it.

## Getting Started

Importing leader-election.py in your python script will enable that piece of code to run as replicas. It also allows to set customised execution time interval in seconds.



### Prerequisites

To use it, you require the following:

```
1. Docker (I used it for etcd, if you have it already then there is no need to install docker)
2. Python3

```

### Installing

Once you got the requisites on your machine, execute the following command:


```
$ pip install -r requirements.txt

```

This will install all the required libraries for you. 


Execute the following command to run etcd:

```
$ sudo docker run -d --name etcd-server \
    --publish 2379:2379 \
    --publish 2380:2380 \
    --env ALLOW_NONE_AUTHENTICATION=yes \
    bitnami/etcd

```

The above will expose etcd on your host network.



## Run the following test


```
$ python example-spof.py server1 

```

Open a new terminal and execute the following:


```
$ python example-spof.py server2

```

The leader will keep printing 'Refreshing lease, still the leader' to tell the other instances about it. 

The follower will print 'I am a follower' and waits for next election. If the leader goes down, the follower will take the place and start doing the leader function.

Just like example-spof.py, you can write your script to user  leader-follower model provided by 'leader_election.py'


##### Note: 

You can change the etcd endpoint as per your need.

```
client = etcd3.client(host='localhost', port=2379)

# inside 'leader_election.py'

```

## Built With

* [ETCD IMAGE](https://hub.docker.com/r/bitnami/etcd/) - Docker Image of Etcd
* [ETCD](https://etcd.io/) - Manages Key/Value and watch for the events happening on the key
* [PYTHON](https://www.python.org/) - Build the spof-leader-election using it. 


