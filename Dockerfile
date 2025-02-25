FROM python:3.10
WORKDIR /app
ADD ./jira_consumer/requirements.txt /app/requirements.txt
RUN pip3 install -r ./requirements.txt
COPY jira_consumer /app
EXPOSE 5002
CMD ["gunicorn", "--bind","0.0.0.0:5002", "jira_notify:run()"]