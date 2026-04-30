# using this image requires a Windows host with Docker Desktop installed
# you must also toggle to "windows containers" from the Docker Desktop tray icon
FROM winamd64/python:3.11

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

WORKDIR /usr/src/app

# system dependencies
RUN python -m pip install --no-cache-dir msvc-runtime poetry==1.8.3

# project dependencies
COPY poetry.lock pyproject.toml ./
COPY vendor ./vendor
RUN if (Test-Path .\vendor\omnitils\pyproject.toml) { \
		$lines = Get-Content pyproject.toml; \
		$vendorLine = 'omnitils = { path = ' + [char]34 + 'vendor/omnitils' + [char]34 + ' }'; \
		$lines = $lines | ForEach-Object { if ($_ -match '^omnitils = \{ git = ') { $vendorLine } else { $_ } }; \
		[System.IO.File]::WriteAllLines('pyproject.toml', $lines, [System.Text.UTF8Encoding]::new($false)); \
	}
RUN python -m poetry lock --no-interaction -vvv
RUN python -m poetry install --no-interaction -vvv

# bring over source code
COPY main.py __VERSION__.py ./
COPY src ./src

# set up dist folder
COPY fonts ./dist/fonts
COPY plugins ./dist/plugins
COPY README.md LICENSE.md pyproject.toml ./dist/

COPY src/data ./dist/src/data
COPY src/img ./dist/src/img

