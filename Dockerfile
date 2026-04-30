# using this image requires a Windows host with Docker Desktop installed
# you must also toggle to "windows containers" from the Docker Desktop tray icon
FROM winamd64/python:3.11

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

WORKDIR /usr/src/app

ENV GIT_VERSION=2.49.0
ENV PATH=C:\git\cmd;${PATH}

# system dependencies
RUN Invoke-WebRequest "https://github.com/git-for-windows/git/releases/download/v$env:GIT_VERSION.windows.1/MinGit-$env:GIT_VERSION-64-bit.zip" -OutFile mingit.zip; \
	Expand-Archive mingit.zip -DestinationPath C:\git; \
	Remove-Item mingit.zip; \
	python -m pip install --no-cache-dir msvc-runtime poetry==1.8.3 poetry-plugin-shell; \
	git config --global http.sslBackend schannel; \
	poetry config experimental.system-git-client true; \
	git --version; \
	poetry --version

# project dependencies
COPY poetry.lock pyproject.toml ./
COPY vendor ./vendor
RUN if (Test-Path .\vendor\omnitils\pyproject.toml) { \
		$content = Get-Content pyproject.toml -Raw; \
		$content = $content -replace 'omnitils = \{ git = "https://github.com/pappnu/omnitils.git", rev = "[^"]+" \}', 'omnitils = { path = "vendor/omnitils" }'; \
		[System.IO.File]::WriteAllText('pyproject.toml', $content, [System.Text.UTF8Encoding]::new($false)); \
		poetry lock --no-interaction; \
	}; \
	poetry install --no-interaction

# bring over source code
COPY main.py __VERSION__.py ./
COPY src ./src

# set up dist folder
COPY fonts ./dist/fonts
COPY plugins ./dist/plugins
COPY README.md LICENSE.md pyproject.toml ./dist/

COPY src/data ./dist/src/data
COPY src/img ./dist/src/img

