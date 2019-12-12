# ship_optimization_model

To run SHiP service:

```
docker run  -v $(pwd)/:/ship_shield_optimisation -v /mnt/shipfs/temp:/root/temp/ --network host -it vbelavin/ship_web_service_k8s bin/bash -c "(nohup redis-server & ); (uwsgi --ini control/app.ini)"
```

## Running jobs

Now you should be able to run jobs with this command:

```
curl --header "Content-Type: application/json" --request POST --data '{"shape": [208.0, 207.0, 281.0, 248.0, 305.0, 242.0, 72.0, 51.0, 29.0, 46.0, 10.0, 7.0, 54.0, 38.0, 46.0, 192.0, 14.0, 9.0, 10.0, 31.0, 35.0, 31.0, 51.0, 11.0, 3.0, 32.0, 54.0, 24.0, 8.0, 8.0, 22.0, 32.0, 209.0, 35.0, 8.0, 13.0, 33.0, 77.0, 85.0, 241.0, 9.0, 26.0], "n_events": 5000}' 127.0.0.1:5433/simulate
```

Which returns uuid of your request.

## Recieving results

And recieve results with the following command with appropriate uuid:

```
curl --header "Content-Type: application/json" --request POST --data '{"uuid": "4a62f94a-ab6e-44a2-9f78-7e925dda1f2a"}' 127.0.0.1:5433/retrieve_result
```
