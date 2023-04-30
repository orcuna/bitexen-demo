## Installation

1. Install docker on your system
2. Make sure Docker swarm is initialized, re-run `docker swarm init`
2. Pull required images with `docker pull orcuna/bitexen-demo:latest`, `docker pull timescale/timescaledb:latest-pg14`
3. Checkout project code and `cd` into root path.
4. Deploy stack in development mode with `docker stack deploy -c docker-compose.dev.yml`
5. Go to http://localhost and you should see live data of the stats :)

## Design choices
### TimescaleDB
TimescaleDB is an extension to PostgreSQL. It still offers standart PostgreSQL plus functionalities 
for working with timeseries data more efficiently. It's still PostgreSQL so managing the database (installing, backups, replication)
is same from the devops perspective.

Timescale introduces hypertables. We explicitly tell Timescale to convert specific tables into hypertables. 
Main difference is how data is stored on disk. 
Timescale divides time-series data into chunks of preferred intervals. When we retrieve data within a time
range, we would use B-Tree indexes of standart PostgreSQL which uses tree to locate each records. On the other hand, Timescale
uses B-Tree to locate chunks each containin multiple records of specified interval (etc. 1 day, 1 hour, 5 minutes). 
Thus retrieving large amounts of time-series records works much faster. It can still locate indivual records after 
finding out regarding chunk using optimized algorithms.

Below is a diagram of Timescale hypertable:


