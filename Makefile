set_up_for_linux:
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt

set_up_for_windows:
	python -m venv .venv
	.venv/Scripts/activate
	pip install -r requirements.txt

create_run_migrations:
	python manage.py makemigrations
	python manage.py migrate

fill_sample_data:
	python ./fill_data.py

run_hole_anaysis:
	python ./run_hole_analysis_script.py

run_api_server:
	python manage.py runserver