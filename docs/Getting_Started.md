# Getting Started

This is the implementation of the Grand Comics Database in Python
using the [Django framework](https://djangoproject.com).

For basic information, see the [README](../README.md) file in the project's
root directory.

## Quick start with containers (recommended)

Requires Docker (or Podman) with the compose plugin, plus
[`just`](https://github.com/casey/just). The container environment lives
in [gcd-django-docker](https://github.com/GrandComicsDatabase/gcd-django-docker),
checked out next to this repository:

```
git clone https://github.com/GrandComicsDatabase/gcd-django-docker ../gcd-django-docker
just fresh
```

Then open http://127.0.0.1:8000/. That one command brings up the database,
loads the schema, loads all fixtures (including the development user
accounts from `apps/indexer/fixtures/users.yaml` — an admin, an approver
and an indexer; usernames and passwords are in that file) plus a little
sample data, and starts the server.

`just fresh` migrates an empty database and loads everything, which takes
a few minutes. `just seed` does the same without starting the server.

With the committed schema snapshot the same happens in seconds:

```
just fresh-fast     # snapshot + fixtures + sample data + serve
just seed-fast      # snapshot + fixtures only (no serve)
```

Run the test suite the same way:

```
just test
```

A Django shell and a database shell work the same way:

```
just shell
just dbshell
```

Elasticsearch (only needed for the search pages) is optional:

```
just search
```

(the web server needs `USE_ELASTICSEARCH=1` in its environment to use it).

### Without `just`

`just` is a thin wrapper over the compose commands; run them directly if
you prefer. The compose project lives in the sibling checkout and mounts
this one as the code, so each command names both. The full-replay path
(equivalent to `just fresh-full`) is:

```
export GCD_CODE=$PWD
docker compose --project-directory ../gcd-django-docker up -d --wait db memcached
docker compose --project-directory ../gcd-django-docker run --rm -w /code/gcd-django web python manage.py seed_dev
docker compose --project-directory ../gcd-django-docker up web
```

`seed_dev` runs the migrations and loads all fixtures; `--no-migrate` loads
fixtures only. See the `justfile` for the exact commands each recipe runs.

### Keeping the snapshot current

The snapshot is a plain `mysqldump` of a freshly-migrated database and must
be regenerated whenever migrations change:

```
just snapshot        # regenerate db/schema-snapshot.sql (after adding migrations)
just snapshot-check  # fail if the snapshot is missing any migration
```

`snapshot`/`snapshot-check` build in a throwaway `test_snapshot` database
(the app DB user is granted rights on `test_%` names), so they never touch
your dev data. A stale snapshot fails `just snapshot-check`, so regenerate and commit it
together with new migrations.

The web container is configured by the `settings_local.py` that
gcd-django-docker mounts into it; there is nothing to set up in this
repository. For running against a locally installed MySQL instead, copy
`settings_local.example.py` to `settings_local.py` and adjust. Note that a
`settings_local.py` on your host is picked up inside the container too,
since the source tree is mounted -- keep it deleted or container-compatible
if you mix both workflows.

## Manual setup

If you prefer a virtualenv on your host, see
[Getting Started on MacOS or Linux](Getting_Started_on_MacOS_or_Linux.md) or
[Getting Started on Windows](Getting_Started_on_Windows.md) for the system
packages, then follow the steps below. You need a Python version supported
by the pinned Django release (currently Django 5.2: Python 3.10 to 3.13).

### 1. `settings.py` and `settings_local.py`

Do not modify `settings.py` itself; create a `settings_local.py` next to it
and override there. Start from the committed example:

```
cp settings_local.example.py settings_local.py
```

The example enables `DEBUG`, allows `localhost` in `ALLOWED_HOSTS`
(required -- the default list only contains comics.org hosts, so without
this override the dev server answers every request with a `DisallowedHost`
error), points the database at the compose MySQL, and uses a local-memory
cache so no memcached is needed.

Alternatively, most settings can be overridden through `GCD_*` environment
variables, see the top of `settings.py`. With `DEBUG` off, a
`GCD_SECRET_KEY` (or `SECRET_KEY` override) is required.

### 2. Creating your test database

The database must be MySQL 8.x. Create the schema and user yourself,
Django creates the tables. From the MySQL command line client:

```
create schema gcdonline;
create user gcdonline;
grant all on gcdonline.* to gcdonline;
grant all on `test\_%`.* to gcdonline;
```

(The second grant lets pytest create its test database.)

### 3. Schema and fixture data

```
python manage.py seed_dev
```

runs all migrations and loads every fixture in one go. To only load
fixtures on an already-migrated database, use `--no-migrate`.

If you get system check errors for `models.E025`, add
`SILENCED_SYSTEM_CHECKS = ['models.E025']` to your `settings_local.py`
(the example file already contains it).

### 4. Populating your database with the GCD data

If you want real data, and know that the current development branch
matches the production schema, log in to comics.org and download a
dump from http://www.comics.org/download/ . With the compose setup:

```
docker compose exec -T db mysql -ugcdonline -pgcdonline gcdonline < dump.sql
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py setup_initial_changesets
docker compose run --rm web python manage.py shell -c "from scripts.reset_stats import main; main()"
```

(or `mysql -ugcdonline gcdonline < dump.sql` for a local MySQL).
`just dump-import dump.sql` runs the same steps.

The dump does not contain the change history, and without it existing
objects cannot be edited through the OI. `setup_initial_changesets`
creates an auto-generated approved changeset per object to make them
editable; by default it covers the first 500 objects per type, see
`--limit`. The last step rebuilds the cached statistics; OI approvals
and the displayed object counts rely on them.

Contact the GCD tech team to find out if the development and production
schemas currently match. Cover images and other uploads are not
distributed.

### 5. Search backend (optional)

Haystack search needs Elasticsearch **7.x** (the pinned client does not
work with ES 8 or newer); 7.17 is the version to use. Run it locally or
via the compose `search` profile, then populate the index:

```
python manage.py rebuild_index
```

### 6. Launching your test web server

Read-write mode is the default. For read-only mode, set
`READ_ONLY = True` and `NO_OI = True` in `settings_local.py`. Then:

```
python manage.py runserver
```

and take a look at http://127.0.0.1:8000/

# Proposing your first change for review

When you start making changes, go to the wiki at http://docs.comics.org/
for instructions on how to get code reviewed before checkin.  You'll need
to set up an account with our Review Board instance so that we can review
your first pull request before deciding whether to accept it.  If you develop
a good record of contributions, you will be granted direct access to the project.

Submissions to the project-owned repository that do not first go through
code review will be reverted without notice.
