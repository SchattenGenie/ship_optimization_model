FROM  shir994/fairship:shield_opt_v3
# vbelavin/ship_simple_model
#RUN rm -r FairShip
#RUN git clone --single-branch --branch shield_opt  https://github.com/shir994/FairShip.git
RUN aliBuild -c shipdist/ --defaults fairship build FairShip --no-local ROOT

#COPY run_simulation.sh ./
#RUN chmod +x run_simulation.sh
COPY . /ship
RUN chmod +x /ship/run_simulation.sh
RUN chmod +x /ship/get_params.sh

WORKDIR /ship
RUN mkdir ./shield_files
RUN mkdir ./shield_files/geometry/
RUN mkdir ./shield_files/outputs/