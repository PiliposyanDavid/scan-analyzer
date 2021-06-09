FROM python as builder
WORKDIR /var/www/picsart
COPY requirements*.txt ./
RUN pip install
FROM python

WORKDIR /var/www/picsart

COPY --from=builder /var/www/picsart/ ./
COPY . .

ARG branch
ENV BRANCH_NAME $branch
CMD ["python", "main.py"]
