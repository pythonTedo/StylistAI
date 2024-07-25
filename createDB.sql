CREATE DATABASE chatbot;

USE chatbot;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE `message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `text` LONGTEXT DEFAULT NULL,
  `image_base64` LONGTEXT DEFAULT NULL,
  `is_bot` tinyint(1) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
);
