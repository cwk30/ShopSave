http://ec2-13-250-36-160.ap-southeast-1.compute.amazonaws.com:5000/
# ShopSave

hustle for the win

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

# github work flow

## how to get changes from james's repo

git fetch upstream

git merge upstream/main
