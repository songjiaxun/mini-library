DROP TABLE IF EXISTS `Students`;
DROP TABLE IF EXISTS `Teachers`;
DROP TABLE IF EXISTS `Books`;
DROP TABLE IF EXISTS `History`;
DROP TABLE IF EXISTS `Access_code`;

CREATE TABLE `Students` (
  `reader_id`   TEXT NOT NULL,
  `name` TEXT NOT NULL,
  `gender` TEXT,
  `unit` TEXT NOT NULL,
  `access` INTEGER NOT NULL,
  `quota` INTEGER NOT NULL,
  `due_count` INTEGER NOT NULL, 
  -- TODO: defaut 0
  PRIMARY KEY (`reader_id`)
);

CREATE TABLE `Teachers` (
  `reader_id`   TEXT NOT NULL,
  `name` TEXT NOT NULL,
  `gender` TEXT,
  `unit` TEXT NOT NULL,
  `access` INTEGER NOT NULL,
  `quota` INTEGER NOT NULL,
  `due_count` INTEGER NOT NULL,
  PRIMARY KEY (`reader_id`)
);

CREATE TABLE `Books` (
  `isbn` TEXT NOT NULL,
  `title` TEXT NOT NULL,
  `author` TEXT NOT NULL,
  `publisher` TEXT,
  `publish_date` TEXT,
  `page_number` TEXT,
  `price` TEXT,
  `subject` TEXT,
  `total_number` INTEGER NOT NULL,
  `index` TEXT,
  `summary` TEXT,
  `location` TEXT NOT NULL,
  PRIMARY KEY (`isbn`)
);

CREATE TABLE `History` (
  `datetime` TIMESTAMP NOT NULL,
  `reader_id` TEXT NOT NULL,
  `action` TEXT NOT NULL,
  `isbn` TEXT  NOT NULL
);

CREATE TABLE `Access_code` (
  `code` INTEGER NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`code`)
);

INSERT INTO `Access_code`
  (`code`, `description`)
VALUES
  ( 0, '关闭'),
  ( 1, '开通'),
  ( 2, '丢书'),
  ( 3, '过期');