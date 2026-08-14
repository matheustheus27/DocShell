FROM php:8.3-cli-alpine

WORKDIR /app
COPY . /app

EXPOSE 8000

CMD ["php", "-S", "0.0.0.0:8000", "scripts/generators/php/router.php"]
