import os
import sys
import csv
import yaml
import sys
from pathlib import Path
from datetime import datetime
from helper_modules import get_ssllab_scan_results, SUMMARY_COLUMNS
from csv_to_html_table import csv_to_html_table
from email_helper import send_email, RECEIVER_EMAIL
from git_helper import clone_report_repo, git_push
from argpare_helper import args
from logger_helper import logger

DOMAINS_SUMMARY_CSV = "/tmp/SSLLab_hosts_and_report/Reports/csv_reports/domains_summary.csv"
HTML_TABLE_LOCATION = "/tmp/SSLLab_hosts_and_report/Reports/html_reports/table.html"
DOMAIN_NAMES_FILE = "/tmp/SSLLab_hosts_and_report/domain_names.yaml"
DOMAINS_SUMMARY_CSV_LOCAL = "Reports/csv_reports/domains_summary.csv"
HTML_TABLE_LOCATION_LOCAL = "Reports/html_reports/table.html"

def main():
    script_dir = Path( __file__ ).parent.absolute()

    if args.local:
        logger.info(f"domain names would be taken from local domain_names.yml and reports will be saved in Reports directory in the package")
    if not args.local:
        logger.info("Cloning the Report Repo from Github")
        if (clone_report_repo()):
            logger.info("Exiting as Report Repo could not be cloned")
            return 1

    if args.re:
        receiver_email = args.re
        logger.info(f"SSLabs summary report Email would be sent to : [{args.re}]")
    else:
        receiver_email = RECEIVER_EMAIL
        logger.info(f"Receiver email addres not provided. SSLLabs summary email would be send to default [{RECEIVER_EMAIL}]")

    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")

    if args.local:
        domain_summary_csv_with_date = f"{os.path.join(script_dir, DOMAINS_SUMMARY_CSV_LOCAL)}_{date}"
        html_table_location_with_date = f"{os.path.join(script_dir, HTML_TABLE_LOCATION_LOCAL)}_{date}"
        if args.domain_yaml:
            domain_names_file = args.domain_yaml
        else:
            domain_names_file_local = f"{os.path.join(script_dir, 'domain_names.yaml')}"
            domain_names_file = domain_names_file_local
    else:
        domain_summary_csv_with_date = f"{DOMAINS_SUMMARY_CSV}_{date}"
        html_table_location_with_date = f"{HTML_TABLE_LOCATION}_{date}"
        if args.domain_yaml:
            domain_names_file = args.domain_yaml
        else:
            domain_names_file = DOMAIN_NAMES_FILE
  
    logger.info(f"SSLabs CSV reports of all the hosts is saved to file [{domain_summary_csv_with_date}]") 
    try:
        with open(domain_summary_csv_with_date, "w") as output_file:
            output_file.write("{}\n".format(",".join(SUMMARY_COLUMNS)))

        with open(domain_names_file) as file_data:
           domain_names_list = yaml.load(file_data, Loader=yaml.FullLoader)
    except Exception as Err:
        loger.error("Domain files could not be opened due to error: /n{Err}")

    logger.info(f"hosts are {domain_names_list}")
    
    logger.info(f"Scanning SSLLabs for all the host listed in: {str(domain_names_list)}")
    for host in domain_names_list:
        logger.info(f"Scanning for Host: [{host}]")
        data = get_ssllab_scan_results(host, domain_summary_csv_with_date)

    logger.info(f"Completed Scanning of all the hosts and summary is saved to file [{domain_summary_csv_with_date}]") 

    logger.info("Converting summary of all hosts CSV file to HTML Table")
    try:
        csv_to_html_table(domain_summary_csv_with_date, html_table_location_with_date)
    except Exception as Err:
        logger.error("CSV file could not be converted to HTML table due to error: \n{Err}")
    logger.info(f"Success: Completed converting summary of all hosts CSV file to HTML Table: [{html_table_location_with_date}]")

    logger.info(f"Sending the Email to: [{receiver_email}]")
    send_email(html_table_location_with_date, receiver_email=receiver_email)
    logger.info(f"Email sent to: [{receiver_email}]")

    if not args.local:
        logger.info("Git Pushing the new generated Reports to Github")
        if (git_push()):
            logger.info("Exiting as Report Repo could not be Pushed")
            return 1

if __name__ == "__main__":
    sys.exit(main())
