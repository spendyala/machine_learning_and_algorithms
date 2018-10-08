FROM continuumio/miniconda3

RUN conda update -n base conda; \
    conda install -c pyviz/label/dev pyviz scikit-learn

EXPOSE 8888
COPY docker/viz/jupyter_notebook_config.py /etc/jupyter/

# Configure environment
ENV NB_USER=jovyan \
    NB_UID=1000 \
    NB_GID=1000

RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER

USER jovyan
RUN /opt/conda/bin/python3 -c "import bokeh; bokeh.sampledata.download()"
RUN cd /home/jovyan; \
    /opt/conda/bin/pyviz fetch-data
USER root

ADD docker/viz/*.sh /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]