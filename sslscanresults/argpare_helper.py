import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--re', type=str, help="email of the receiver to which reports are sent")
parser.add_argument('--domain_yaml', type=str, help="Location of custom domain names yaml file")
parser.add_argument('--local', action='store_true', help="Use local script directory for getting domain names and saving the reports")
args = parser.parse_args()
