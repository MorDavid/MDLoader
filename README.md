# MD Loader
This script analyzes the MD tools output file and load to Neo4j/Bloodhound database.
## Usage
```

 █▄█ █▀▄   █   █▀█ █▀█ █▀▄ █▀▀ █▀▄
 █ █ █ █   █   █ █ █▀█ █ █ █▀▀ █▀▄
 ▀ ▀ ▀▀    ▀▀▀ ▀▀▀ ▀ ▀ ▀▀  ▀▀▀ ▀ ▀

usage: MDLoader.py [-h] [--dburi DATABASEURI] [-u DATABASEUSER] [-p DATABASEPASSWORD] -d DOMAIN -f FILE_LOAD [-s] [-v]

MDLoader - This script analyzes the MD tools output file and load to Neo4j/Bloodhound database.

options:
  -h, --help            show this help message and exit
  --dburi DATABASEURI   Database URI
  -u DATABASEUSER, --dbuser DATABASEUSER
                        Database user
  -p DATABASEPASSWORD, --dbpassword DATABASEPASSWORD
                        Database password
  -d DOMAIN, --domain DOMAIN
                        Domain Name (example: lab.local)
  -f FILE_LOAD, --file FILE_LOAD
                        Select Output file of MDHound
  -s, --sessions        Load Sessions
  -v, --verbose         Verbose mode
```