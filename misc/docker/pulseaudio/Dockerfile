FROM tuxeatpi/common

ENV PULSE_SERVER /run/pulse/native

RUN apt-get update && \
    apt-get install -y --no-install-recommends pulseaudio-utils pulseaudio && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

RUN echo enable-shm=no >> /etc/pulse/client.conf

VOLUME /run/pulse
