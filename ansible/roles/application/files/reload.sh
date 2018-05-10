kill -9 $(ps -ef | grep '[p]ython3 geo_analyser.py' | awk '{print $2}')

cd ~/production/app/
nohup python3 geo_analyser.py > ~/geo_analyser.log &

rsync -rtv . ../test/app/
cd ../test/app/
nohup python3 geo_analyser.py > ~/geo1.log &

rsync -rtv ../../app/ ../../test2/app/
cd ../../test2/app/
nohup python3 geo_analyser.py > ~/geo2.log &

rsync -rtv ../../app/ ../../test3/app/
cd ../../test3/app/
nohup python3 geo_analyser.py > ~/geo3.log &