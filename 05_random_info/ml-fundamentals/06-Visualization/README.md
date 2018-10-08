# Visualization Presentation

This presentation was authored in Jupyter. See `./docker/viz/convert.sh` for an example of how
to convert a notebook to an html/[reveal.js](https://github.com/hakimel/reveal.js/) slide deck. You will need to install reveal.js into
the same directory as the `Presentation.slides.html`.

Also, since this presentation makes use of most of the PyViz toolset (including cartopy and geoviews), it's 
a bit heavy weight. Rather than include all of that into the Course docker container, it has it's own
docker container. To build and run it, please install [docker-utils](https://github.com/resero-labs/docker-utils).

Finally, running the presentation is a bit memory intensive. I use the remote docker capabilities of docker-utils to
run the notebook on an ec2 instance with more memory than my laptop. You may want to consider doing so as well.