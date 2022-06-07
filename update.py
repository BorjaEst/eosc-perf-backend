import logging
import time

import requests

logging.basicConfig(level="INFO")
logger = logging.getLogger("Update")
api = "http://is.marie.hellasgrid.gr/rest"
time_steps = []


# GET sites ---------------------------------------------------------
def get_sites(params={"limit": -1}):
    url = f"{api}/sites"
    req = requests.get(url, params=params)

    logger.debug(f"GET sites requests: {req}")
    if req.status_code == 200:
        return req.json()['data']
    else:
        raise Exception(f"{req.status_code}")


# GET endpoints -----------------------------------------------------
def get_endpoints(site, params={"limit": -1}):
    url = f"{api}/sites/{site['id']}/cloud/computing/endpoints"
    req = requests.get(url, params=params)

    logger.debug(f"GET endpoints requests: {req}")
    if req.status_code == 200:
        return req.json()['data']
    else:
        raise Exception(f"{req.status_code}")


# Help functions ----------------------------------------------------
def site_name(site, endpoint):
    return f"{site['name']}: {endpoint['endpointImplementationName']}"


def time_step():
    time_steps.append(time.time())


# Main call ---------------------------------------------------------
if __name__ == "__main__":
    time_step()  # Collect all sites
    sites = get_sites()

    time_step()  # Collect site endpoints
    for site in sites:
        site['endpoints'] = get_endpoints(site)

    time_step()  # Generate site names
    names = []
    for site in sites:
        names += [site_name(site, ep) for ep in site['endpoints']]

    time_step()  # Print site names
    print(names)

    pass
