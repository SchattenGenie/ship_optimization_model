# ls -lthaR /root/host_directory/
set -x;
./azcopy copy "https://shipfs.file.core.windows.net/data/$4?$AZKEY" /ship/muon_input/
ls -lthaR /ship/muon_input/
time python run_simulation.py --shield_params $1 --n_events $2 --first_event $3 --file_name $4 --step_geo $5 |& tee /ship/shield_files/outputs/ship_logs.txt
rm /ship/shield_files/outputs/ship.conical.MuonBack-TGeant4.root
ls -lthaR /ship/shield_files/
ls -lthaR /ship/shield_files/outputs/
./azcopy copy "/ship/shield_files/outputs/*" "https://shipfs.file.core.windows.net/data/$6?$AZKEY" --recursive=true