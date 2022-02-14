FROM selenium/standalone-chrome

ARG customca

USER root

ADD $customca /usr/local/share/ca-certificates/customca.crt
RUN update-ca-certificates

USER seluser
