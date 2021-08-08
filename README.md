View the final product here on your mobile device. https://shopsave.tech



# ShopSave

ShopSave was submitted as a hack in Citi HackOverflow 2021. 

This app was created to allow merchants to sell e-vouchers to users, as well as to provide a QR scanning solution to claim said vouchers.

# Features

Merchants

Registration/Login Portal

Profile page to Update their profiles

Ability to Create/Read/Update/Delete their shop vouchers

Analytics on Sales Figures

Always on QR code scanner to scan store vouchers, ready to be deployed at checkout counter



Users

Shop through the list of stores, and purchase vouchers from said store

Voucher wallet to browse owned vouchers

Generate QR code when claiming vouchers


For intent and purposes, all features are working, except the payment portal. Feel free to create an account to test the features, or use the following test account:

Merchant (Cashier) Account

KFC

kfc123


User Account

user

password


Technology

The project was created using HTML5/CSS/JS + Flask/SQLite.

Server is a AWS EC2 instance + NGINX + Gunicorn.

HTTPS secured domain bought on domain.com + AWS Route 53 + CertBot


# quick installation start

git remote add upstream git@github.com:cwk30/ShopSave.git

python3 -m venv ShopSaveEnv

ShopSaveEnv\Scripts\activate

pip install -r requirements.txt

flask run

# commands to write for setting up

python3 -m venv ShopSaveEnv

# start the virtual environment

ShopSaveEnv\Scripts\activate

# to deactivate the virual environment

deactivate

# command to update the dependency used

python -m pip freeze > requirements.txt
