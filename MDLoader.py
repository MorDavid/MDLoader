#!/usr/bin/env python3
import argparse
import logging
import json
import time
from py2neo import Graph, NodeMatcher, Relationship

print("""
 █▄█ █▀▄   █   █▀█ █▀█ █▀▄ █▀▀ █▀▄
 █ █ █ █   █   █ █ █▀█ █ █ █▀▀ █▀▄
 ▀ ▀ ▀▀    ▀▀▀ ▀▀▀ ▀ ▀ ▀▀  ▀▀▀ ▀ ▀
""")

parser = argparse.ArgumentParser(description="MDLoader - This script analyzes the MD tools output file and loads it into the Neo4j/Bloodhound database.")
# Neo4j Settings
parser.add_argument('--dburi', dest='databaseUri', help='Database URI', default='bolt://localhost:7687')
parser.add_argument('-u', '--dbuser', dest='databaseUser', help='Database user', default='neo4j')
parser.add_argument('-p', '--dbpassword', dest='databasePassword', help='Database password', default='neo4j')
# Domain Information
parser.add_argument('-d', '--domain', dest='domain', help='Domain Name (example: lab.local)', required=True)
# Files
parser.add_argument('-f', '--file', dest='file_load', help='Select Output File of MDHound', required=True)
parser.add_argument('-s', '--sessions', dest='file_session', help='Load Sessions', action='store_true')
# My friend's requests
parser.add_argument('-o', '--owned', dest='file_owned', help='Mark Owned Users or Machines', action='store_true')
parser.add_argument('-ro', '--remove-owned', dest='file_remove_owned', help='Remove Owned Users or Machines', action='store_true')
# General
parser.add_argument('-v', '--verbose', dest='verbose', help='Verbose mode', action='store_true')
args = parser.parse_args()

# Set the logging level
loggingLevel = (logging.DEBUG if args.verbose else logging.INFO)

# Configure the root logger
logger = logging.getLogger('MDLoader')
logger.setLevel(loggingLevel)

# Configure the console logger
consoleLogger = logging.StreamHandler()
consoleLogger.setLevel(loggingLevel)
consoleFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleLogger.setFormatter(consoleFormatter)
logger.addHandler(consoleLogger)

# Set the path for the log file
log_file_path = 'MDLoader_logs.log'

# Configure the file logger
fileLogger = logging.FileHandler(log_file_path)
fileLogger.setLevel(loggingLevel)
fileFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileLogger.setFormatter(fileFormatter)
logger.addHandler(fileLogger)

# Add a log message
logger.debug('[*] Arguments: ' + str(args))

# Neo4j Connection with retry logic
logger.info("[+] Starting update neo4j aka your bloodhound...")
max_retries = 3
for attempt in range(max_retries):
    try:
        graph = Graph(args.databaseUri, auth=(args.databaseUser, args.databasePassword))
        logger.info(f"[+] Connected to Neo4j server: {args.databaseUri} ({args.databaseUser})")
        matcher = NodeMatcher(graph)
        break
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j on attempt {attempt + 1}/{max_retries}: {str(e)}")
        if attempt < max_retries - 1:
            time.sleep(5)
        else:
            logger.error("[+] Could not connect to the Neo4j server after multiple attempts. Exiting.")
            exit(1)

# Process the file
if args.file_load:
    logger.info(f"Reading {args.file_load}")
    try:
        f = open(args.file_load, "r", encoding="utf8")
        lines = f.read()
        f.close()
    except Exception as e:
        logger.error(f"Failed to read the file: {str(e)}")
        exit(1)
    
    if args.file_owned:
        lines = lines.splitlines()
        for x in lines:
            user_or_computer = x.upper()
            node = matcher.match(name=user_or_computer).first()
            if node:
                node["owned"] = True
                graph.push(node)
                logger.info(f"Marked {user_or_computer} as owned.")
                
    elif args.file_remove_owned:
        lines = lines.splitlines()
        for x in lines:
            user_or_computer = x.upper()
            node = matcher.match(name=user_or_computer).first()
            if node:
                node["owned"] = False
                graph.push(node)
                logger.info(f"Remove {user_or_computer} as owned.")
    elif args.file_session:
        json_lines = json.loads(lines)
        for x in json_lines:
            if("Host" in x):
                name = x["Host"].upper()+"."+args.domain.upper()
                if "@" in x["User"]:
                    user = x["User"].upper().split("@")[0]+"@"+args.domain.upper()
                else:
                    user = x["User"].upper()+"@"+args.domain.upper()
                node_computer=matcher.match("Computer", name=name).first()
                node_user=matcher.match("User", name=user).first()
                if node_user and node_computer:
                    graph.merge(node_computer | node_user)
                    graph.create(Relationship(node_computer, "HasSession", node_user,type=x["Type"]))
                    logger.info(f"Created 'HasSession' relationship between {name} and {user}.")
    else:
        json_lines = json.loads(lines)
        for x in json_lines:
            if "Name" in x:
                name = x["Name"].upper() + "." + args.domain.upper()
                node = matcher.match("Computer", name=name).first()
                if node:
                    exists = x.keys()
                    logger.info(f"[+] Updating {name}")
                    for z in exists:
                        if z != "Name":
                            node[z] = x[z]
                    graph.push(node)
                else:
                    name = x["Name"].upper()
                    node = matcher.match("Computer", name=name).first()
                    if node:
                        exists = x.keys()
                        logger.info(f"[+] Updating {name}")
                        for z in exists:
                            if z != "Name":
                                node[z] = x[z]
                        graph.push(node)
                    else:
                        logger.info(f"Node not found for {name} (Host)")
            if "GPO" in x:
                gpo = x["GPO"]
                node = matcher.match("GPO", objectid=gpo).first()
                if node:
                    exists = x.keys()
                    logger.info(f"[+] Updating {gpo}")
                    for z in exists:
                        if z != "GPO":
                            node[z] = x[z]
                    graph.push(node)
                else:
                    logger.info(f"Node not found for {gpo} (GPO)")
