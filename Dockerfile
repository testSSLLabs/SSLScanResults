# Pull base image.
FROM ubuntu:18.04
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y python3.6
RUN apt install -y python3-pip
RUN apt install -y openssh-client
RUN mkdir ~/.ssh
WORKDIR /project
RUN git config --global user.email manoj.cis114@gmail.com
RUN git clone https://github.com/testSSLLabs/SSLScanResults.git 
RUN cp /project/SSLScanResults/key_priv ~/.ssh/id_rsa
RUN cp /project/SSLScanResults/key_pub ~/.ssh/id_rsa.pub
RUN chmod 600 ~/.ssh/id_rsa
RUN chmod 600 ~/.ssh/id_rsa.pub
RUN echo "Host *" > ~/.ssh/config
RUN echo " StrictHostKeyChecking no" >> ~/.ssh/config
RUN echo " PreferredAuthentications publickey" >> ~/.ssh/config
RUN echo " IdentitiesOnly yes" >> ~/.ssh/config
RUN rm -rf /project/SSLScanResults
RUN git clone https://github.com/testSSLLabs/SSLScanResults.git
RUN pip3 install -r SSLScanResults/requirements.txt
CMD python3 /project/SSLScanResults/sslscanresults/sslscan-results.py
