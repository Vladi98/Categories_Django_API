import os;
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "categories.settings")
django.setup()

from categories_app import hole_analysis_script

if __name__ == '__main__':
    hole_analysis_script.main()