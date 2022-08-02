## Create virtual environment:
```
pip3 install virtualenv
mkdir project_A
cd project_A
virtualenv my_new_venv
source my_new_venv/bin/activate
```

## Clone the project repo and install dependency packages from requirements.txt :
```
git clone https://github.com/testSSLLabs/SSLScanResults.git
pip3 install -r SSLScanResults/requirements.txt
```

## Execute the script:
### Local mode
By default, by default tool get its domain names host list by cloning Github Repo https://github.com/testSSLLabs/SSLScanResults.git 
1. If scan reports not required to be pushed to github repo then use --local option. Tool will take domains/hosts from sslscanresults/domain_names.yaml.
   --local option must be used if running the script and you do not have git auth keys.
   --re option must be used to specify the email address whree reports must be sent. By default reports are sent to manoj.cis@gmail.com.

   **python3 SSLScanResults/sslscanresults/sslscan-results.py --local --re manoj.cis@gmail.com**


2. You can also specify the domain names with your own local domain_names.yaml file

   **python3 SSLScanResults/sslscanresults/sslscan-results.py --local --re manoj.cis@gmail.com --domain_yaml /tmp/manjku/domain_names.yaml**

3. If reports need to be updated to github repo, then copy RSA key specified in key_priv to your .ssh directory and execute the tool:

   **cp key_priv ~/.ssh/id_rsa**

   **python3 SSLScanResults/sslscanresults/sslscan-results.py**


# Execute tool in a docker instance
   **git clone https://github.com/testSSLLabs/SSLScanResults.git**

   **cd SSLScanResults**

   **docker build -t ssllab_report:21.0 .**

Get the docker image ID:

   **docker images ssllab_report:21.0**

Create docker containre to execute the tool. Please use the --re option to specify the email to which reports must be sent.

   **docker run 00528c8085e4 python3 /project/SSLScanResults/sslscanresults/sslscan-results.py --re manoj.cis115@gmail.com**
