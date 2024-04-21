#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys

def read_local_envs():
    import configparser
    config = configparser.ConfigParser()
    config.optionxform=str
    my_path = os.path.abspath(os.path.dirname(__file__))
    config.read(os.path.join(my_path, ".local_envs.ini"))
    envs = dict(dict(config).get("main", {}))
    return envs


def main():
    """Run administrative tasks."""

    if not os.environ.get("COUNTER_SKIP_POETRY", None):
        import subprocess
        os.environ["COUNTER_SKIP_POETRY"] = "yes"
        subprocess.run(["poetry", "install", "--quiet"], check=True)
        os.environ.update(read_local_envs())
        os.execlp(*(["poetry", "poetry", "run"] + sys.argv))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'counterdev.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
