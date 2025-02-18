FROM python
WORKDIR /app
COPY jira_consumer /app
RUN pip3 install -r ./requirements.txt
CMD ["gunicorn", "--bind","0.0.0.0:5002", "jira_notify:run()"]