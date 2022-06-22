#!/bin/bash
for i in {30..39}
do
   python3 -m lib.generate_new_config --from_template qdiff.yaml --version $i
   screen -L -Logfile data/qmt_v$i/log_fuzzy.txt -S qmt_v$i -d -m  python3 -m lib.qmt config/qmt_v$i.yaml
done

for i in {40..49}
do
   python3 -m lib.generate_new_config --from_template morphq.yaml --version $i
   screen -L -Logfile data/qmt_v$i/log_fuzzy.txt -S qmt_v$i -d -m  python3 -m lib.qmt config/qmt_v$i.yaml
done