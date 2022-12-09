# Set up sytem and install user
FROM nycticoracs/pop_os:22.04
RUN apt update -y && \
    apt install python3-pip -y && \
    useradd -ms /bin/bash botuser

# Install app
WORKDIR /opt/app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY ./app .

# Setup user
USER botuser
RUN flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

CMD cd /opt && python3 -m app