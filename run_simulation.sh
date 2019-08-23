alienv enter -w /sw FairShip/latest << 'EOF'
cp /root/host_directory/magnet_config.json $FAIRSHIP/diff-model/
python $FAIRSHIP/macro/run_simScript.py --PG --pID 13 -n 100 --Estart 1 --Eend 10 --FastMuon -o /root/host_directory/output_mu
python $FAIRSHIP/macro/run_simScript.py --PG --pID -13 -n 100 --Estart 1 --Eend 10 --FastMuon -o /root/host_directory/output_antimu
python /root/host_directory/preprocess_root_file.py /root/host_directory/output_mu/ship.conical.PG_13-TGeant4.root
python /root/host_directory/preprocess_root_file.py /root/host_directory/output_mu/ship.conical.PG_13-TGeant4.root
EOF