#!/bin/bash
# Run Lastpass Authenticator export with active OTP
# Login info
read -p "Lastpass account (email): " uservar
read -p "Current OTP: " otpvar

# Run actual export
python3 lastpass-authenticator-export.py -u $uservar -o $otpvar
echo .
echo .
echo Export done, see result http://localhost:8080/export/export.html
echo .
echo .
exit