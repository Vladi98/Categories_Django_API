import os;
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "categories.settings")
django.setup()

from categories_app import generate_test_data
from django.conf import settings

if __name__ == '__main__':
    # settings.configure()
    generate_test_data.main()