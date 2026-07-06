# GCD development tasks. Run `just` to list them.
#
# Everything runs in the gcd-django-docker compose environment, expected
# as a sibling checkout (override with COMPOSE_DIR). This checkout is
# mounted as the code the containers run.

compose_dir := env_var_or_default("COMPOSE_DIR", justfile_directory() / ".." / "gcd-django-docker")
export GCD_CODE := justfile_directory()

dc := "docker compose --project-directory " + compose_dir
web := dc + " run --rm -w /code/gcd-django web"
mysql := dc + " exec -T db mysql -ugcd-django -pdb-gcd"

# Show available recipes
default:
    @just --list

# Build the web image from this checkout's requirements
build:
    mkdir -p {{compose_dir}}/gcd-django
    cp requirements.txt {{compose_dir}}/gcd-django/requirements.txt
    {{dc}} build web

# Start the database and cache (detached), waiting until the DB is healthy
db:
    {{dc}} up -d --wait db memcached

# Migrate an empty database and load all fixtures (full replay).
seed: db
    {{web}} python manage.py seed_dev

# Add a small sample of publishers/series/issues for a populated site
sample: db
    {{web}} python manage.py sample_data

# One command from a clean clone to a populated, running site
fresh: build seed sample up

# Start the web server (http://127.0.0.1:8000)
up: db
    {{dc}} up web

# Stop everything
down:
    {{dc}} down

# Stop and delete the database volume (destructive, full reset)
reset:
    {{dc}} down -v




# Run the test suite, reusing the test database (fast)
test *ARGS: db
    {{web}} pytest --reuse-db {{ARGS}}

# Run the test suite building a fresh test database
test-fresh *ARGS: db
    {{web}} pytest --create-db {{ARGS}}

# Lint with ruff
lint:
    {{dc}} run --rm --no-deps -w /code/gcd-django web python -m ruff check .

# Open a Django shell
shell:
    {{web}} python manage.py shell

# Open a database shell
dbshell:
    {{web}} python manage.py dbshell

# Rebuild the cached statistics, needed after importing a dump
dump-stats:
    {{web}} python manage.py shell -c "from scripts.reset_stats import main; main()"

# Import a comics.org dump, then make its objects editable
dump-import FILE: db
    {{mysql}} my-gcd-db < {{FILE}}
    {{web}} python manage.py migrate
    {{web}} python manage.py setup_initial_changesets
    just dump-stats





# Start Elasticsearch (search pages) and build the index
search:
    {{dc}} --profile search up -d es
    {{dc}} run --rm -w /code/gcd-django -e USE_ELASTICSEARCH=1 web python manage.py rebuild_index
