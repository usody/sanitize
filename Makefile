tests:
	echo "Running tests..."
	cd tests
	PYTHONPATH=usody_sanitize coverage run -m pytest -v -o junit_family=xunit2 --junitxml="tests_output/junit_report.xml" tests

.PHONY: tests
