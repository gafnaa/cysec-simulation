# php/Dockerfile
FROM php:8.2-apache

# Enable common Apache modules (rewrite, headers)
RUN a2enmod rewrite headers

# Copy custom apache site config
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

# Optional: install common PHP extensions if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
        unzip \
    && docker-php-ext-install pdo pdo_mysql \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/html

# Ensure uploads directory exists (this will be mounted from docker-compose)
RUN mkdir -p /var/www/html/uploads/products \
 && chown -R www-data:www-data /var/www/html/uploads

EXPOSE 80

CMD ["apache2-foreground"]
