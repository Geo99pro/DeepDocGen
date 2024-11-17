# Change the version of cuda and cudnn according to user cuda and cudnn version
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/root
ENV PATH=${HOME}/miniconda3/bin:$PATH

# Install libraries and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    curl \
    unzip \
    wget \
    tar \
    build-essential \
    libopenmpi-dev \
    pkg-config \
    cmake \
    libpoppler-cpp-dev \
    poppler-utils \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends python3.9 python3.9-distutils python3.9-dev python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade setuptools

# Update Python symlink to point to Python 3.9
RUN ln -sf /usr/bin/python3.9 /usr/bin/python \
    && ln -sf /usr/bin/python3.9 /usr/bin/python3

# Verify Python and pip versions
RUN python3 --version && pip --version

# Copy the requirements.txt file to the container
COPY ./requirements.txt ${HOME}/requirements.txt

# Install pytorch, torchvision and torchaudio, change the version according to your requirements 
RUN pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu118

# Install requirements
RUN pip install --no-cache-dir -r ${HOME}/requirements.txt

WORKDIR ${HOME}

CMD [ "bash" ]

#Usage
#As the docker file is in the docker folder, you can build the image by running the following command:
#docker build -f docker/Dockerfile -t <<desired_name:desired_tag_name>> .
#For example, to build the image with the name pipeline_image and tag v1, you can run the following command:
#docker build -f docker/Dockerfile -t pipeline_image:v1 .
