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



