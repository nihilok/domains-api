# ipChecker
To facilitate running a home web server behind a router, this script checks to see if external IP has changed, alerts user via email, and updates dynamic DNS rules via the domains.google API.

### Update:
Now universally compatible/accessible. Windows/Mac/Linux it will ask for your credentials on first run. I also added command line options/arguments (see `./ipchecker.py --help`) for loading/deleting a user and changing credentials/settings.

### Installation:

Install requirements (assumes installation of Python 3 and pip):

`pip install -r requirements.txt`

Run the script with `python ipchecker.py` (or on unix-based systems, you can mark `ipchecker.py` as executable with 

`chmod +x ipchecker.py`

and simply execute the script with `./ipchecker.py`).

On first run, you will need your Dynamic DNS autogenerated username and password as described in [this documentation.](https://support.google.com/domains/answer/6147083?hl=en-CA) If you choose to receive email notifications, you will be asked to input your gmail email address and password which will then be encoded before being saved. (The notification is sent from the user's own email address via the gmail smtp server, you will need to allow less secure apps on your Google account to use.). For more info on how to set up Dynamic DNS and the process I went through writing this script check [this blog post.](https://mjfullstack.medium.com/running-a-home-web-server-without-a-static-ip-using-google-domains-python-saves-the-day-246570b26d88)

After initial setup, the script takes care of everything: if your IP has changed since you last ran it, it will update your Dynamic DNS rule on domains.google.com.

On **Windows** you can use Task Scheduler; on **Linux/Mac**, simply add a line to your crontab and you can choose the frequency of the checks. My hourly cron job looks like this:

`0 * * * * /home/me/ipChecker/ipchecker.py >> ~/cron.log 2>&1`

if reducing downtime is essential, you could increase the frequency of checks to every 5 minutes, or even less, like this:

`*/5 * * * * ...etc`

On Google Domains the default TTL for Dynamic DNS is 1 min, but unless you expect your external IP to change very frequently, more regular checks might be a slight waste of resources; even so, the script is very light weight.

The logs are written to both `ipchecker.log` in the script's own directory, and stdout, so that the logs also appear in the cron log & terminal. Check `~/cron.log` if the script does not run as expected, or to see when the IP was last checked.

If you forget your IP or need to check it for any reason, running `ipchecker.py` without options will log your current IP to the terminal. 

As well as the command line options, to change your user details or delete them, you can also just delete the `/.user` file.

    ipChecker.py help manual (command line options):
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ipchecker.py                        || -run the script normally without arguments
    ipchecker.py -h --help              || -show this help manual
    ipchecker.py -c --credentials       || -change API credentials
    ipchecker.py -e --email             || -email set up wizard > use to delete email credentials (choose 'n')
    ipchecker.py -n --notifications     || -toggle email notification settings > will not delete email address
    ipchecker.py -d --delete_user       || -delete current user profile
    ipchecker.py -u path/to/user.pickle || -(or `--user_load path/to/user.pickle`) load user from file**
                                        || **this will overwrite any current user profile without warning!
                                        || **Backup "/.user" file to store multiple profiles.

