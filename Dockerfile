FROM nycticoracs/pop_os:22.04
RUN apt update -y && \
    apt install python3-pip -y

RUN useradd -ms /bin/bash botuser
USER botuser
WORKDIR /opt/app

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY ./app .

CMD cd /opt && python3 -m app