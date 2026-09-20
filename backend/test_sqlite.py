import os
import django
from django.conf import settings
from django.test.utils import get_runner

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
django.setup()

# Override database to sqlite
settings.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2, interactive=False)
failures = test_runner.run_tests(["favorites", "restaurants", "users"])
import sys
sys.exit(bool(failures))
