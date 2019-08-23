FROM  olantwin/ship-base:20181116
# vbelavin/ship_simple_model
RUN git clone --single-branch --branch simple_sim  https://github.com/shir994/FairShip.git
RUN aliBuild -c shipdist/ --defaults fairship build FairShip --no-local ROOT
RUN mkdir /sw/slc7_x86-64/FairRoot/latest/include/source && cp /sw/slc7_x86-64/FairRoot/latest/include/*.h /sw/slc7_x86-64/FairRoot/latest/include/source && mkdir /sw/slc7_x86-64/FairRoot/latest/include/steer && cp /sw/slc7_x86-64/FairRoot/latest/include/*.h /sw/slc7_x86-64/FairRoot/latest/include/steer && mkdir /sw/slc7_x86-64/FairRoot/latest/include/sim && cp /sw/slc7_x86-64/FairRoot/latest/include/*.h /sw/slc7_x86-64/FairRoot/latest/include/sim && mkdir /sw/slc7_x86-64/FairRoot/latest/include/field && cp /sw/slc7_x86-64/FairRoot/latest/include/*.h /sw/slc7_x86-64/FairRoot/latest/include/field && mkdir /sw/slc7_x86-64/FairRoot/latest/include/event && cp /sw/slc7_x86-64/FairRoot/latest/include/*.h /sw/slc7_x86-64/FairRoot/latest/include/event

COPY run_simulation.sh ./
RUN chmod +x run_simulation.sh

ENTRYPOINT bash /run_simulation.sh