FROM kalilinux/kali
# Metadata params
ARG BUILD_DATE
ARG VERSION
ARG VCS_URL
ARG VCS_REF

WORKDIR /var

ADD ./requirements.txt /var

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url=$VCS_URL \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.version=$VERSION \
      org.label-schema.name='Kali Linux' \
      org.label-schema.description='Official Kali Linux docker image' \
      org.label-schema.usage='https://www.kali.org/news/official-kali-linux-docker-images/' \
      org.label-schema.url='https://www.kali.org/' \
      org.label-schema.vendor='Offensive Security' \
      org.label-schema.schema-version='1.0' \
      org.label-schema.docker.cmd='docker run --rm kalilinux/kali' \
      org.label-schema.docker.cmd.devel='docker run --rm -ti kalilinux/kali' \
      org.label-schema.docker.debug='docker logs $CONTAINER' \
      io.github.offensive-security.docker.dockerfile="Dockerfile" \
      io.github.offensive-security.license="GPLv3" \
      MAINTAINER="Steev Klimaszewski <steev@kali.org>"
RUN echo "deb http://http.kali.org/kali kali-rolling main contrib non-free" > /etc/apt/sources.list && \
    echo "deb-src http://http.kali.org/kali kali-rolling main contrib non-free" >> /etc/apt/sources.list
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONIOENCODING=utf8
RUN set -x \
    && apt-get -yqq update \
    && apt-get clean \
    && apt-get install -yqq build-essential python-dev libnetfilter-queue-dev tshark tcpdump python3-pip wireshark \
    && apt install -yqq python3-pip \
    && apt install -yqq git \
    && pip3 install -U git+https://github.com/kti/python-netfilterqueue \
    && pip3 install --process-dependency-links polymorph

RUN apt-get install -yqq linux-image; exit 0

VOLUME ["/var/develop"]

CMD ["/bin/bash"]
