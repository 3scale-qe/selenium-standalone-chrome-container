FROM selenium/standalone-chrome

# Retrieve certificate content from GitHub secret
ARG customca
ARG customca_dest=/usr/local/share/ca-certificates/certificate.crt

USER root

# Copy certificate to desired certificate destination file
ADD $customca $customca_dest

# Update CA certificates
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssl ca-certificates \
    && update-ca-certificates  \
    && chmod a+r $customca_dest \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER seluser

# Create NSS database directory
RUN mkdir -p $HOME/.pki/nssdb

# Add the custom CA certificate to NSS database
RUN certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n customca -i $customca_dest
