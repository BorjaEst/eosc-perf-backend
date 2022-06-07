import requests
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger("Update")
api = "http://is.marie.hellasgrid.gr/rest"


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


# Composed sites ----------------------------------------------------
def site_name(site, endpoint):
    return f"{site['name']}: {endpoint['endpointImplementationName']}"


# Main call ---------------------------------------------------------
if __name__ == "__main__":
    sites = get_sites()
    for site in sites:
        site['endpoints'] = get_endpoints(site)

    names = []
    for site in sites:
        names += [site_name(site, ep) for ep in site['endpoints']]

    print(names)

    pass
