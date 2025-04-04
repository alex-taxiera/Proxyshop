# using this image requires a Windows host with Docker Desktop installed
# you must also toggle to "windows containers" from the Docker Desktop tray icon
FROM winamd64/python:3.11

WORKDIR /usr/src/app

# system dependencies
RUN pip install msvc-runtime poetry poetry-plugin-shell

# project dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install

# bring over source code
COPY main.py __VERSION__.py ./
COPY src ./src

# set up dist folder
COPY art ./dist/art
COPY fonts ./dist/fonts
COPY out ./dist/out
COPY plugins ./dist/plugins
COPY templates ./dist/templates
COPY README.md LICENSE.md pyproject.toml ./dist/

#COPY src/data ./dist/src/data
#COPY src/img ./dist/src/img

