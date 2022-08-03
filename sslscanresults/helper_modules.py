import sys
import os
import json
import time
import requests
from typing import Dict
from datetime import datetime
from pathlib import Path
from argpare_helper import args
from logger_helper import logger

HOST_AND_REPORT_DIR = "/tmp/SSLLab_hosts_and_report/Reports/"

SSLAB_API_URL = "https://api.ssllabs.com/api/v3/analyze"

SECURITY_PROTOCOLS = [
    "SSL 2.0 INSECURE", "SSL 3.0 INSECURE", "TLS 1.0", "TLS 1.1", "TLS 1.2", "TLS 1.3",       
]

SUMMARY_COLUMNS = [
    "Host", "Server Name", "IP Address", "HasWarnings", "Grade", "Cert Expiry", "Chain Status", "Forward Secrecy", "Heartbeat ext",
    "Support RC4", "RC4 Only", "RC4 with modern protocols", "Vuln Drown", "Vuln openSsl Ccs", "Vuln openSSL LuckyMinus20",
 ] + SECURITY_PROTOCOLS

SSLLAB_CHAIN_ISSUES = {
    "0": "none",
    "1": "unused",
    "2": "incomplete chain (set only when we were able to build a chain by adding missing intermediate certificates from external sources)",
    "4": "chain contains unrelated or duplicate certificates (i.e., certificates that are not part of the same chain)",
    "8": "the certificates form a chain (trusted or not), but the order is incorrect",
    "16": "contains a self-signed root certificate (not set for self-signed leafs)",
    "32": "the certificates form a chain that we could not validate",
}

SSLLAB_FORWARD_SECRECY = {
    "0": "Not Found",
    "1": "at least one browser from our simulations negotiated a Forward Secrecy suite",
    "2": "FS is achieved with modern clients",
    "4": "all simulated clients achieved FS",
}

def get_ssllab_scan_results(host: str, csv_summary_file: str, number_of_attempts: int=20):
    """
    Request SSLLabs API json data for a host and appends the formatted json data into CSV row
    Returns SSLLabs API json data for a host
    """
    ssllab_request_params = get_ssllab_request_params(host)
    sslab_scan_results = execute_api_url(ssllab_request_params, number_of_attempts) 
    # ssllab_request_params.pop("startNew")

    while sslab_scan_results["status"] != "READY" and sslab_scan_results["status"] != "ERROR":
        logger.info(f"Scanning for {host} is still in Progress....")
        time.sleep(10)
        sslab_scan_results = execute_api_url(ssllab_request_params, number_of_attempts)

    logger.info(f"Scanning for [{host}] Completed. Saving the report to CSV ")
    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

    if args.local:
        script_dir = Path( __file__ ).parent.absolute()
        json_output_file = os.path.join(script_dir, f"Reports/json_reports/{host}.json_{date}")
    else:
        json_output_file = os.path.join(os.path.dirname(HOST_AND_REPORT_DIR),"json_reports",f"{host}.json_{date}")

    logger.info(f"SSLLab json data for host [{host}] is stored at: [{json_output_file}]")
    try:
        with open(json_output_file, "w") as outputfile:
            json.dump(sslab_scan_results, outputfile, indent=2)
    except Exception as Err:
        logger.error("json file could not be opened due to error: \n{Err}")     
        sys.exit(1)

    summary_csv_append(host, sslab_scan_results, csv_summary_file)
    logger.info(f"SSLabs report host [{host}] saved to CSV file")   
 
    return sslab_scan_results

def get_ssllab_request_params(host: str):
    """
    Gets the parameters when request is sent to "https://api.ssllabs.com/api/v3/analyze"
    """
    params = {
        "host": host,
        "ignoreMismatch":"on",
        "all":"done",
        "publish":"off",
        "fromCache": "on"
    }
    return params
    
def execute_api_url(ssllab_request_params, number_of_attempts):
    """
    Prepares SSLLabs API call with parameters and return the json data
    """
    api_response = requests.get(SSLAB_API_URL, params=ssllab_request_params)
    attempts = 0 
    
    try:
        while api_response.status_code != 200 and attempts < number_of_attempts:
            attempts += 1
            time.sleep(10)
            api_response = requests.get(SSLAB_API_URL, params=ssllab_request_params)
    except Exception as Err:
        logger.error("SSLab api request failed due to error: \n{Err}")
        sys.exit(1)
    return api_response.json()

def summary_csv_append(host, sslab_data, csv_summary_file):
    """
    Parse the SSLLabs API json data for all host endpoints and sets the columns fields defined in SUMMARY_COLUMNS
    Each host endpoint row is added to the CSV file
    """
    try:
        with open(csv_summary_file, "a") as output_file:
            summary_csv = [] 
            if sslab_data["certs"]:
                not_after = sslab_data["certs"][0]["notAfter"]
                not_after = float(str(not_after)[:10])
                not_after_date = datetime.utcfromtimestamp(not_after).strftime("%Y-%m-%d")
            else:
                not_after_date = "Not Found"     

            for endpoint in sslab_data["endpoints"]:
               # Ignore endpoints that could not be scanned
               if "Unable" in endpoint["statusMessage"] or "fail" in endpoint["statusMessage"]:
                   logger.critical(f"Ignoring Host [{host}] endpoint[{endpoint['ipAddress']}] as it recieved unexpected statusMessage [{endpoint['statusMessage']}]")
                   logger.critical(f"Please check the Host [{host}] json data")
                   continue

               summary_csv = [
                   host,
                   endpoint.get("serverName"),
                   endpoint.get("ipAddress"),
                   endpoint.get("hasWarnings", "Not Found"),
                   endpoint.get("grade", "Not Found"),
                   not_after_date,
                   SSLLAB_CHAIN_ISSUES[str(endpoint["details"]["certChains"][0]["issues"])],
                   SSLLAB_FORWARD_SECRECY[str(endpoint["details"].get("forwardSecrecy", "0"))],
                   endpoint["details"]["heartbeat"],
                   endpoint["details"]["supportsRc4"],
                   endpoint["details"]["rc4Only"],
                   endpoint["details"]["rc4WithModern"],
                   endpoint["details"]["drownVulnerable"],
                   False if endpoint["details"]["openSslCcs"] == 1 else True,
                   False if endpoint["details"]["openSSLLuckyMinus20"] == 1 else True,
               ]

               for protocol in SECURITY_PROTOCOLS:
                   found = False
                   for endpoint_protocol in endpoint["details"]["protocols"]:
                       endpoint_protocol_name = f"{endpoint_protocol['name']} {endpoint_protocol['version']}"
                       if protocol == endpoint_protocol_name:
                           found = True
                           break
                   if found:
                       summary_csv += ["Yes"]
                   else:
                       summary_csv += ["No"]
               if summary_csv:
                   output_file.write(",".join(str(s) for s in summary_csv) + "\n")
    except Exception as err:
       logger.error(f"SSLLabs report for domain {host} could not be added to csv due to Error:\n {err}")
       logger.info(f"Continuing with the next domain")
