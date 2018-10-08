FROM rappdw/docker-ds

RUN apt-get update && apt-get install build-essential -y && pip install Cython
RUN pip install py-heat-magic numba
RUN pip install tensorflow
RUN pip install flask
RUN pip install aiohttp
RUN pip install nltk
RUN pip install langdetect
ADD docker/jupyter_notebook_config.py /home/jovyan/.jupyter/jupyter_notebook_config.py
RUN chown -R jovyan /home/jovyan/.jupyter; \
    usermod -u 2005 node; \
    groupmod -g 2005 node; \
    usermod -u 1000 jovyan

RUN mkdir -p /home/jovyan/mnist; \
    cd /home/jovyan/mnist; \
    wget -q https://s3-us-west-2.amazonaws.com/resero2/datasets/tsne-perf-test/data.2500.mnist.dat.gz; \
    gunzip *.gz

RUN pip install \
        umap-learn \
        tsne-mp

RUN apt-get install libgomp1


