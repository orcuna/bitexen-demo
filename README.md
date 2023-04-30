## Live Demo
A live demo for this project can be found at:

[http://bitexen-demo.sk2tr.com](http://bitexen-demo.sk2tr.com)

## Installation

1. Install docker on your system
2. Make sure Docker swarm is initialized, re-run `docker swarm init`
2. Pull required images with `docker pull orcuna/bitexen-demo:latest`, `docker pull timescale/timescaledb:latest-pg14`
3. Checkout project code and `cd` into root path.
4. Deploy stack in development mode with `docker stack deploy -c docker-compose.dev.yml bitexen-demo`
5. Go to http://localhost and you should see live data of the stats :)

## Design choices
### TimescaleDB
TimescaleDB is an extension to PostgreSQL. It still offers standart PostgreSQL plus functionalities 
for working with timeseries data more efficiently. It's still PostgreSQL so making queries with SQL and 
managing the database (installing, backups, replication) stays same.

Django ORM can work with Timescale hypertables easily with extensions if we don't want to run raw SQL queries.

Timescale introduces hypertables. We explicitly tell Timescale to convert specific tables into hypertables. 
Main difference is how data is stored on disk. 
Timescale divides time-series data into chunks of preferred intervals. When we retrieve data within a time
range, we would use B-Tree indexes of standart PostgreSQL which uses tree to locate each records. On the other hand, Timescale
uses B-Tree to locate chunks each containin multiple records of specified interval (etc. 1 day, 1 hour, 5 minutes). 
Thus retrieving large amounts of time-series records works much faster. It can still locate indivual records after 
finding out regarding chunk using optimized algorithms.

Below is a diagram of Timescale hypertable:

![Hypertable](https://github.com/orcuna/bitexen-demo/raw/master/example-timescales.png "Hypertable")

Space-partitioning can be applied to a hypertable so that a parallel series of chunks created for each value of the specified partition key (symbol names in our case).
However in this demo, no space-partitioning is applied since we deal with only one symbol.


### Luigi

Luigi is a task pipeline framework originially developed in Spotify. We specify each task with parameters: 
Two tasks with same name and same parameters will point to same task in our task space. This helps building
a dependency resolution of tasks. Luigi also provides visualization, handling failures, a central scheduler with multiple workers attached, 
integration with Spark, Hadoop and much more.

For the purpuse of the demo, local scheduler with only 1 worker is used. You can find luigi tasks in `/app/scripts/aggregate.py`.

Below is an example diagram of dependency resolution for this project:

![Dependency Resolution](https://github.com/orcuna/bitexen-demo/raw/master/example-dependency-resolution.png "Example Dependecy Resolution ")




