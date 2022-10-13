#!/bin/bash
echo '#### Start Deploying... ####'
echo
echo "Prod or Dev Deployment ?"
echo
select dp in "Dev" "Prod" "Local"; do
    case $dp in
        Dev ) cfg='dev'; echo '#### Ok will copy config_dev.py as config.py ####'; break;;
        Prod ) cfg='prod'; echo '#### Ok will copy config_prody.py as in config.py ####'; break;;
        Local ) cfg='local'; echo '#### Ok will leave config.py untouched. ####'; break;;
    esac
done
git branch
echo
echo "Do you want pull the latest from this branch?"
echo
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo '#### Ok will pull ####'; git pull; break;;
        No ) echo '#### Skip pulling new code from git ####'; break;;
    esac
done
echo
if [ '$cfg' != 'local' ] 
then
  echo '#### Copy Config Files ####'
  cfgfile='config_'$cfg'.py'
  cp $cfgfile config.py
  echo
fi
echo
echo "Do you want run migrations?"
echo
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo '#### Ok will run migrations ####'; 
              source venv2/bin/activate;
              python manage.py migrate;
              deactivate ;
              break ;;
        No ) echo '#### Skip migrations ####'; break;;
    esac
done
echo
echo '#### Restart UWSGI to load the new release####'
touch reload_uwsgi.ini
