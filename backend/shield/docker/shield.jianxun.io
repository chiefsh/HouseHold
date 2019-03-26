
location ~ ^/(job|user|tag) {
    root /var/www/html;
    try_files $uri $uri/ /index.html;
}

location /index.html {
    root /var/www/html;
}

location ~* \.(js|jpg|png|css){
    root /var/www/html;
}


