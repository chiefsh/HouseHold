FROM python:3.6-alpine

ENV LIBRARY_PATH=/lib:/usr/lib
ENV PYTHONUNBUFFERED 1
ENV PYCURL_SSL_LIBRARY openssl

RUN echo "https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.5/community/"  > /etc/apk/repositories
RUN echo "https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.5/main/"  >> /etc/apk/repositories

RUN apk add --update --no-cache mariadb-client-libs\
    && apk add --no-cache --virtual .build-deps curl-dev libffi-dev libxml2-dev libxslt-dev g++ musl-dev jpeg-dev zlib-dev freetype-dev mariadb-dev \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h\
    && pip3 install pika tornado bson bcrypt pycrypto wtforms ujson pycurl sqlalchemy mysqlclient pymysql redis hiredis pycrypto pillow xmltodict wechatpy cryptography -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn\
    && find /usr/local -depth \
		\( \
			\( -type d -a -name test -o -name tests \) \
			-o \
			\( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		\) -exec rm -rf '{}' + \
    && runDeps="$( \
		scanelf --needed --nobanner --recursive /usr/local \
			| awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
			| sort -u \
			| xargs -r apk info --installed \
			| sort -u \
	)" \
	&& apk add --virtual .python-rundeps $runDeps \
	&& apk del .build-deps \
	&& rm -rf /usr/src/python ~/.cache


CMD ["python", "/server/server.py"]

ADD ./localtime /etc/localtime

