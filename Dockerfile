FROM selenium/standalone-chrome

ARG customca

USER root

ADD $customca /usr/local/share/ca-certificates/customca.crt
RUN update-ca-certificates
RUN apt update && apt install libnss3-tools && rm -Rf /var/lib/apt/lists/*

USER seluser

RUN certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n customca -i /usr/local/share/ca-certificates/customca.crt
