# lastpass-authenticator-export

Based on the original author's investigation at `https://blog.unauthorizedaccess.nl/2021/03/07/export-totps-from-lastpass-authenticator.html`

You can install & run this on your machine or inside a docker container. When you are familiar with Docker that's the easy option since it doesn't alter your machine setup

## Compatible (don't know minimums)

- python 3.10
- pip 22.2.2

## Steps

1. Place the script somewhere on a filesystem that is _not_ backed up (for example: avoid google drive or apple time machine protected drives)
2. Install dependencies. Ex:
   - `pip install -r requirements.txt` (default python3 installations with pip on command interpreter path)
   - `pip3 install -r requirements.txt` (non-default python3 installations with pip on command interpreter path)
   - `python -m pip install -r requirements.txt` (python3 installation with pip not on command interpreter path)
3. Execute the script. Ex:
   - `python lastpass-authenticator-export.py -u <lastpass_account>` (default python3 installation without lastpass OTP configured)
   - `python lastpass-authenticator-export.py -u <lastpass_account> -o <######>` (default python3 installation with lastpass OTP configured)
   - `python3 lastpass-authenticator-export.py -u <lastpass_account>` (non-default python3 installation without lastpass OTP configured)
4. The python script will request password and proceed once authenticated.
5. The script will create an `export` subdirectory of the invocation directory, with an `export.html` that goes through all qr codes along with a name for each.
6. Once you've enrolled all the codes to your new authenticator, _securely_ delete the `export` directory with all of its contents. This may require a data shredder application. At a minimum avoid any trash can/recycle bin options.

## Docker instructions

Presuming you have Docker installed and are somehow familiar with it. Look at the shell scripts, there's no rocket science involved.

The script presumes OTP is active.

1. run `./makecontainer.sh` it will create the container with python and an nginx http server
2. run `./runcontainer.sh` which starts the container in interactive mode and the webserver on port 8080
3. Open a new terminal shell and run `./goinside.sh` this will open the commandline inside the container
4. There run `./export.sh` which will start the python script
5. Look at the result at http://localhost:8080/export/export.html
6. Stop the container (`CTRL+C` will do). No files will be retained

YMMV
