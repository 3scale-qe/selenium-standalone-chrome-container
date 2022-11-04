FROM selenium/standalone-chrome

ARG customca
ARG customca_dest=/usr/local/share/ca-certificates/customca.crt

USER root

ADD $customca $customca_dest
RUN update-ca-certificates \
	&& chmod a+r $customca_dest \
	&& apt update && apt install libnss3-tools && rm -Rf /var/lib/apt/lists/*

USER seluser

RUN mkdir -p $HOME/.pki/nssdb
RUN certutil -N -d sql:$HOME/.pki/nssdb -A -t "C,," -n customca -i $customca_dest
