alias rs="cd ~/traceroute && git pull && source venv/bin/activate && sudo supervisorctl signal HUP gunicorn"
alias cs='cd ~/traceroute && git pull && source venv/bin/activate && python manage.py collectstatic --noinput'
alias mg='cd ~/traceroute && git pull && source venv/bin/activate && python manage.py migrate'
alias st='tail -n 100 /var/log/gunicorn/gunicorn.out.log'
export BORG_PASSPHRASE="ACTUALPASSPHRASE"
export BORG_RSH="ssh -oBatchMode=yes -i ~/.ssh/borg_nopass"
alias blist="borg list backup:/var/backups/borg/primary"