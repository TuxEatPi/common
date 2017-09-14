FROM python:3.6-stretch

RUN mkdir -p /workdir
RUN mkdir -p /opt/tuxeatpi_common

COPY misc/docker/common/entrypoint.sh /entrypoint.sh

COPY requirements.txt /opt/tuxeatpi_common/requirements.txt
COPY test_requirements.txt /opt/tuxeatpi_common/test_requirements.txt

RUN python --version
RUN apt-get update && \
    apt-get install -y --no-install-recommends git gcc locales && \
    apt-get clean && \
    pip install -r /opt/tuxeatpi_common/requirements.txt && \
    apt-get -y purge gcc && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "fr_FR.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen
    # TODO Add more languages

COPY setup.py /opt/tuxeatpi_common/
COPY tuxeatpi_common /opt/tuxeatpi_common/tuxeatpi_common

RUN cd /opt/tuxeatpi_common && \
    python setup.py install && \
    rm -rf /opt/tuxeatpi_common

ENTRYPOINT ["/entrypoint.sh"]
