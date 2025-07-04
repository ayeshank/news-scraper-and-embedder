#!/bin/bash
echo "Running for SFMTA";
python aggregator.py -s "SFMTA_Spider" -w "https://www.sfmta.com/news-blog/"

echo "Running for SFWeekly";
python aggregator.py -s "SFWeekly_Spider" -w "https://www.sfweekly.com/"

echo "Running for National Weather Service";
python aggregator.py -s "NWS_Spider" -w "https://www.weather.gov/news/"

echo "Running for SFCurbed";
python aggregator.py -s "SFCurbed_Spider" -w "https://sf.curbed.com/"

echo "Running for SFExaminer";
python aggregator.py -s "SFExaminer_Spider" -w "https://sfexaminer.com/"

echo "Running for Mission Local Blog";
python aggregator.py -s "MissionLocal_Spider" -w "https://missionlocal.org/"

echo "Running for Socket Site Blog";
python aggregator.py -s "SocketSite_Spider" -w "https://socketsite.com/"

echo "Running for Table Hopper Blog";
python aggregator.py -s "TableHopper_Spider" -w "https://www.tablehopper.com/"

echo "Running for Broke-Ass Stuart Blog";
python aggregator.py -s "BrokeAssStuart_Spider" -w "https://brokeassstuart.com/news/"

echo "Running for SFist Weather";
python aggregator.py -s "SFistWeather_Spider" -w "https://sfist.com/weather/"
