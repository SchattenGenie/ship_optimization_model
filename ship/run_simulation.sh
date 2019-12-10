ls -lthaR /root/host_directory/
time python run_simulation.py --shield_params $1 --n_events $2 --first_event $3 --file_name $4 |& tee /ship/shield_files/outputs/ship_logs.txt
rm /ship/shield_files/outputs/ship.conical.MuonBack-TGeant4.root
ls -lthaR /ship/shield_files/
ls -lthaR /ship/shield_files/outputs/
ls -lthaR /root/host_directory/
cp -r /ship/shield_files/outputs/* /root/host_directory/
