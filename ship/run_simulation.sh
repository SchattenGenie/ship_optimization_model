ls -lthaR /root/host_directory/
python run_simulation.py --shield_params $1 --n_events $2 --first_event $3
ls -lthaR /ship/shield_files/
ls -lthaR /ship/shield_files/outputs/
ls -lthaR /root/host_directory/
cp -r /ship/shield_files/outputs/* /root/host_directory/
