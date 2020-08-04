Odpalenie pierwszy raz:
- stworzenie projektu jako źródło podając sklonowany folder.
- dodanie Django do projektu (`pip install Django` lub zależne od IDE)

 ```
 cd Fleet_mng
 cp fleetmanagement/settings_dev.py fleetmanagement/settings.py
 python manage.py migrate
 python manage.py createsuperuser
 python manage.py runserver
 ```

Do testów:

Zamiast createsuperuser:
```
python manage.py loaddata 01_perms_data.json
python manage.py loaddata 02_groups_data.json
python manage.py loaddata 03_vehicle_data.json
python manage.py loaddata 04_renter_data.json
python manage.py loaddata 05_rent_data.json
```

Dla bootstrap'a w forms'ach
```
pip install django-crispy-forms
```
