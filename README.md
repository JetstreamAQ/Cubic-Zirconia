# Cubic Zirconia Δ

The result of an inside joke; a Discord bot which drops randomized product links between a specified interval with the power of *Scrapy* and *Discord.py*.  Also an amalgamation of terribly executed ideas such as a per-server stock market.

## Installation

### Setting Up The Entire Bot

First, clone the repository in your desired directory:

> git clone [url]

In order for the bot to run and function as intented, you need to install the required packages -- this can be done as follows:

> pip install -r requirements.txt

If you do not want to install these packages globally, then it is recommended to create and run the bot under a virtual environment.  This can easily be done with the following commands:

```
pip install virtualenv
python venv [ENVIRONMENT NAME]
source [ENVIRONMENT NAME]/bin/activate
pip install -r requirements.txt
```

Now, you will need to create a `.env` file in the bot's root directory.  In it, place the following lines and fill in the variables with the necessary information

```
DISCORD_TOKEN=[...]
MASTER_SERVER_ID=[...]
OWNER_ID=[...]
```

Once that is done, you will need to setup a Discord bot application [here](https://discord.com/developers/applications) if you have not done so already.

Next, ensure that the bot has the following permissions and scopes:

> Permissions
> 	- Send Messages
>	- Use Slash Commands
> Scopes
>	- bot
>	- applications.commands

Finally, invite the bot into your server and run it with `python3 main.py`.

Alternatively, you can utilize the provided `run.sh` script.  However, if you have not setup a virtual environment for the bot

### Installing Only The Needed Cogs

Clone the repository:

> git clone [url]

For reference, the following cogs refer to these bot functions:

> `rec.py` -> The scraping & recommendation system

> 'stocks.py` -> the scuffed stock market simulator game

Take the relevant files and place them in them where you normally put your bot's cogs.

If you are making use of `rec.py`, then take the entire `scraper` directory and place it in your bot's root directory.  Afterwards, you will need to initalize a `.env` file if you have not done so yet.  In it place `HOME_SERVER_ID` and `OWNER_ID` variables with their respective values.

Finally, you can either reload your bot's cogs or simply reboot your entire bot -- whichever way you have setup or prefer.  Afterwards, you should now be able to use the relevant functionalities of this bot within your own.

## Usage
You can view all available commands with `+help`

### rec.py
Once the bot is running, you will need to initiate a crawl.  This is done with the following command:

> +initiateCrawl [OR] +ic

The bot will go down for a bit as it grabs the links.

Once the bot has finished, it will drop a random link the the channel which recieved the latest message (that it has read permissions for) every 10 messages by default.  The interval can be changed with the following command:

> +messageGap (num)
> +mg (num)

If you want a random product link right now, then just run the following command:

> +recommend [OR] +rec [OR] +r [OR] /recommend

### stocks.py
Everything should be good to go once the bot is running.  You can play around with the following commands

> +invest [name (in quotes if there are spaces in it)] [num]

Invest `num` stocks of `name`

> +portfolio

Request your own investment portfolio for the current server

> +sell [name (in quotes if there are spaces in it)] [num]

Sell `num` stocks of `name`

> +stockPrice

Get the prices of currently available listings

## License

Licensed under the MIT License (2021) - JetstreamAQ.  Please refer to LICENSE.md for more information.