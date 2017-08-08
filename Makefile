#######################################
### Dev targets
#######################################
dev-dep:
	sudo apt-get install python3-virtualenv python3-pil.imagetk python3-tk libspeex-dev swig libpulse-dev libspeexdsp-dev portaudio19-dev

dev-pyenv:
	virtualenv -p /usr/bin/python3 env
	env/bin/pip3 install -r requirements.txt --upgrade --force-reinstall
	env/bin/python setup.py develop


#######################################
### Documentation
#######################################
doc-update-refs:
	rm -rf doc/source/refs/
	sphinx-apidoc -M -f -e -o doc/source/refs/ tuxeatpi/

doc-generate:
	cd doc && make html
	touch doc/build/html/.nojekyll

#######################################
### Localization
#######################################
lang-scan:
	pygettext3.5 --output-dir=tuxeatpi/locale/  -k gtt -va -x tuxeatpi/libs/lang.py tuxeatpi/*.py tuxeatpi/*/*.py tuxeatpi/*/*/*.py
	cd tuxeatpi/locale && msgmerge --update --no-fuzzy-matching --backup=off en/LC_MESSAGES/tuxeatpi.po messages.pot
	cd tuxeatpi/locale && msgmerge --update --no-fuzzy-matching --backup=off fr/LC_MESSAGES/tuxeatpi.po messages.pot

lang-gen:
	cd tuxeatpi/locale/fr/LC_MESSAGES/ && msgfmt tuxeatpi.po -o tuxeatpi.mo
	cd tuxeatpi/locale/en/LC_MESSAGES/ && msgfmt tuxeatpi.po -o tuxeatpi.mo

set-locales:
	sudo sed -i 's/# \(en_US.UTF-8 .*\)/\1/g' /etc/locale.gen
	sudo sed -i 's/# \(en_CA.UTF-8 .*\)/\1/g' /etc/locale.gen
	sudo sed -i 's/# \(fr_FR.UTF-8 .*\)/\1/g' /etc/locale.gen
	sudo sed -i 's/# \(fr_CA.UTF-8 .*\)/\1/g' /etc/locale.gen
	sudo locale-gen

#######################################
### Test targets
#######################################

test-run: test-syntax test-pytest

test-syntax:
	pycodestyle --max-line-length=100 tuxeatpi_base
	pylint --rcfile=.pylintrc -r no tuxeatpi_base

test-pytest:
	rm -rf .coverage nosetest.xml nosetests.html htmlcov
	pytest --html=pytest/report.html --self-contained-html --junit-xml=pytest/junit.xml --cov=tuxeatpi_base/ --cov-report=term --cov-report=html:pytest/coverage/html --cov-report=xml:pytest/coverage/coverage.xml tests 
	coverage combine || true
	coverage report --include='*/tuxeatpi_base/*'
	# CODECLIMATE_REPO_TOKEN=${CODECLIMATE_REPO_TOKEN} codeclimate-test-reporter

