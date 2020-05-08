FROM  shir994/fairship:shield_opt_v3
RUN rm -r FairShip && git clone --single-branch --branch shield_opt  https://github.com/shir994/FairShip.git &&\
    aliBuild -c shipdist/ --defaults fairship build FairShip --no-local ROOT

RUN apt-get -y update && apt-get install wget && apt-get clean -y && rm -rf /var/lib/apt/lists/*

COPY . /ship
RUN chmod +x /ship/run_simulation.sh /ship/get_params.sh

WORKDIR /ship
RUN mkdir ./shield_files ./shield_files/geometry/ ./shield_files/outputs/ ./muon_input

RUN wget -O azcopy_v10.tar.gz https://aka.ms/downloadazcopy-v10-linux && tar -xf azcopy_v10.tar.gz --strip-components=1