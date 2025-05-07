from contextlib import asynccontextmanager
import os
import pathlib
import sys

from fastapi import FastAPI, HTTPException



app = FastAPI()
@asynccontextmanager
async def lifespan(_: FastAPI):
    # Validate that we know where the hosts file is
    host_file_path = os.environ.get("P_AIA_HOSTS_FILE", "hosts")
    if not host_file_path:
        raise ValueError("No host file location specified! Please set P_AIA_HOSTS_FILE environment variable to the location of the host file and restart!")
    host_file: pathlib.Path = pathlib.Path(host_file_path)
    if not host_file.exists():
        raise ValueError(f"Host file {host_file_path} does not exist! Please validate the location and then restart!")
    try:
        with open(host_file, 'r'):
            pass
    except:
        print(f"Unable to open {host_file_path}!")
        raise
    yield

def read_servers_from_host_file(host_file: pathlib.Path):
    servers = []
    in_target_section = False
    
    with open(host_file, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Section header check
            if line.startswith('['):
                in_target_section = (line == '[linux_servers]')
                continue
            
            # Add non-empty lines when in our target section
            if in_target_section and line and not line.startswith('#'):
                servers.append(line)
            
            # Exit if we've reached the next section
            if in_target_section and line.startswith('['):
                break
                
    return servers

@app.get("/")
async def read_hosts():
    host_file_path = os.environ.get("P_AIA_HOSTS_FILE", "hosts")
    try:
        raw_servers = read_servers_from_host_file(pathlib.Path(host_file_path))
        servers = [server.split('.')[0] for server in raw_servers]
        servers.sort()
        return {'linux_servers': servers}
    except Exception as exception:
        print(f"Unable to read {host_file_path}", file=sys.stderr)
        print(repr(exception), file=sys.stderr)
        print(exception, file=sys.stderr)
        raise HTTPException(status_code = 500, detail = "Unable to read host file, please report issue to IDM team")

