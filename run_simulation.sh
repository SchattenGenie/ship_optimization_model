cp /root/host_directory/magnet_params.json $FAIRSHIP/diff-model/
cat $FAIRSHIP/diff-model/magnet_params.json
mkdir /root/temp_ship
python $FAIRSHIP/macro/run_simScript.py --PG --pID 13 -n $1 --Estart 1 --Eend 10 --FastMuon -o /root/temp_ship/output_mu
python $FAIRSHIP/macro/run_simScript.py --PG --pID -13 -n $1 --Estart 1 --Eend 10 --FastMuon -o /root/temp_ship/output_antimu
python /root/host_directory/preprocess_root_file.py /root/temp_ship/output_mu/ship.conical.PG_13-TGeant4.root
python /root/host_directory/preprocess_root_file.py /root/temp_ship/output_antimu/ship.conical.PG_-13-TGeant4.root
cp -R /root/temp_ship/* /root/host_directory/