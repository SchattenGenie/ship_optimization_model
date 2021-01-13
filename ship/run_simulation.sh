# ls -lthaR /root/host_directory/
set -x;
./azcopy copy "https://shipfs.file.core.windows.net/data/$4?$AZKEY" /ship/muon_input/
ls -lthaR /ship/muon_input/

python get_params.py --shield_params $1
if [ $6 == "--step_geo" ]; then
    python $FAIRSHIP/macro/create_field_perturbation.py --muShieldDesign 8 -g "./shield_files/geometry/magnet_geo.root" --stepMuonShield
else
    python $FAIRSHIP/macro/create_field_perturbation.py --muShieldDesign 8 -g "./shield_files/geometry/magnet_geo.root"
fi
python $FAIRSHIP/field/add_noise_to_field.py && python $FAIRSHIP/field/convertNoisyMap.py

time python run_simulation.py --shield_params $1 --n_events $2 --first_event $3 --file_name $4 $6 $7 |& tee /ship/shield_files/outputs/ship_logs.txt
rm /ship/shield_files/outputs/ship.conical.MuonBack-TGeant4.root
ls -lthaR /ship/shield_files/
ls -lthaR /ship/shield_files/outputs/
./azcopy copy "/ship/shield_files/outputs/*" "https://shipfs.file.core.windows.net/data/$5?$AZKEY" --recursive=true