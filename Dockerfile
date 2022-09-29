FROM tensorflow/tensorflow:2.8.2-gpu
ENV DEBIAN_FRONTEND noninteractive
USER root
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y build-essential libsm6 libxext6 libturbojpeg ffmpeg libssl-dev liblua5.1-0-dev zlib1g-dev ca-certificates && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y python3.8 python3-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2 && \
    apt clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends gcc apt-utils
RUN apt-get update && apt-get install -y libc-dev libffi-dev wget
RUN apt-get install -y python3-dev python3-pip curl libaio1 libaio-dev && apt clean && rm -rf /var/lib/apt/lists/*
RUN apt-get install -y mysql-server
#ENV LANG en_US.UTF-8
#ENV LANGUAGE en_US:en
#ENV LC_ALL en_US.UTF-8
#ENV TZ=Asia/Ho_Chi_Minh
ARG WORKING_DIR=/app
WORKDIR ${WORKING_DIR}
COPY ./src ${WORKING_DIR}/src
COPY ./resources ${WORKING_DIR}/resources
COPY ./config ${WORKING_DIR}/config
COPY ./api.py ${WORKING_DIR}/api.py
COPY ./requirements.txt ${WORKING_DIR}/requirements.txt
COPY requirements.txt ${WORKING_DIR}/requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
EXPOSE 3306

CMD service mysql start && mysql -u root -e "CREATE DATABASE pod_foods;" \
&& mysql -u root pod_foods < ${WORKING_DIR}/resources/data/data.sql && python3 api.py