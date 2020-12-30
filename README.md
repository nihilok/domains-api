# ipChecker
To facilitate running a home web server behind a router, this program checks to see if external IP has changed, alerts user via email, and updates dynamic DNS rules via the domains.google API.

### Update:
I have now updated `ipchecker-win.pyw` to work with the domains.google API instead of Selenium, which reduces the time/workload significantly (despite being less fun!). I have also added `ipchecker-linux.py` to be compatible with unix-based systems. I have left the selenium modules (`ipchanger.py` and `ipchanger-linux.py`) in the repository for reference.

### Installation:
Currently set up with my own Gmail address:- change `GMAIL_USER` constant in `ipchecker-win.pyw` or `ipchecker-linux.py` and allow less secure apps on your Google account to use.)

Install requirements:

`pip install -r requirements.txt`

(now without Selenium requirements - see `requirements-selenium.txt` for diff and if you want to use this you will also need to download `geckodriver.exe` web driver for Firefox from **[here](https://github.com/mozilla/geckodriver/releases)** and add location to PATH.)

On **Windows**, use the `start.bat` file to start the program. A script is then automatically added to startup folder and the program will run on user login, checking the IP every 6 hours.

On **Linux/Mac**, simply add the ipchecker-linux.py script to your crontab and you can choose the frequency of the checks.

On first run, you will be asked to input your password which will then be encoded with base64 before being saved. On windows, the initial console window that ran the program can be closed and the program will continue to run in the background (as a pythonw.exe process). It checks the IP every 6 hours while running. On Linux/Mac, the script will close after running once and will only run again if added to crontab. 

Both versions log to `ipchecker.log` in the same directory. Check this file if the program does not run as expected, or to see when the IP was last checked.

### Upcoming changes:
I am planning to implement a better setup/installation process which takes in the user's email address and Dynamic DNS credentials, as, at the moment, the program is really only set up for my own personal use.