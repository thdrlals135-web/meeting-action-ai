setup:
	pip install -r requirements.txt

pipeline:
	python main.py

dashboard:
	streamlit run app/dashboard.py

run:
	python main.py
	streamlit run app/dashboard.py