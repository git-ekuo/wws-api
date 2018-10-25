FROM python:3.7.0

# system libraries for netcdf + hdf5 file format
RUN apt-get update -y \
    && apt-get install -y libhdf5-serial-dev libnetcdf-dev git build-essential fuse libfuse-dev libcurl4-openssl-dev libxml2-dev mime-support automake libtool curl tar

# Install s3 over fuse package, to mount s3 directory under /s3bucket
RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git /tmp/s3fs-fuse \
    && cd /tmp/s3fs-fuse \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && mkdir /s3bucket

COPY requirements.txt /src/requirements.txt

WORKDIR /src/

RUN pip install --no-cache-dir -r requirements.txt