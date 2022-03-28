# opensea-api-nft-sales
Python script to retrieve nft trasactions event from OpenSea API.
To start making requests you will need the OpenSea API Key, which can be obtained from here https://docs.opensea.io/reference/request-an-api-key

Command execution example:
``` 
> python script.py -s "2022-03-25" -e "2022-03-26"
``` 
Help for all options:
``` 
> python script.py -h
options:
  -h, --help            show this help message and exit
  -s STARTDATE, --startdate STARTDATE
                        The Start Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)
  -e ENDDATE, --enddate ENDDATE
                        The End Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)
  -p PAUSE, --pause PAUSE
                        Seconds to wait between http requests. Default: 1
  -o OUTFILE, --outfile OUTFILE
                        Output file path for saving nft sales record in csv format
```
