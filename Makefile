.PHONY: rs-status rs-verify-table tests

rs-status: 
	aws redshift-serverless get-workgroup \
		--workgroup-name aq-melbourne-wg \
		--query 'workgroup.status'

rs-verify-table:
	python -c "from ingestion.redshift_utils import run_query; \
		rows = run_query('SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = \'staging\''); \
		[print(r) for r in rows]"

tests:
	python -m pytest -v