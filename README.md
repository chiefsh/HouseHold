# HouseHold
家居用品

账户表：
CREATE TABLE `account` (
  `user_id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(15) NOT NULL DEFAULT '',
  `password` varchar(128) NOT NULL DEFAULT '',
  `created_at` int(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

产品表：
CREATE TABLE `product` (
  `product_id` str(12) NOT NULL,
  `name` varchar(128) NOT NULL DEFAULT '',
  `category_id` int(11) NOT NULL,
  `group_price` float(15) NOT NULL DEFAULT 0,
  `market_price` float(15) NOT NULL DEFAULT 0,
  `charge_unit` varchat(15) NOT NULL DEFAULT "",
  `group_number` int(11) NOT NULL DEFAULT 0,
  `community_id` int(11) NOT NULL DEFAULT 0,
  `brief` varchar(128) NOT NULL DEFAULT '',
  `sell_point` varchar(128) NOT NULL DEFAULT '',
  `detail` varchar(1024) NOT NULL DEFAULT '',
  `transport_sale` varchar(128) NOT NULL DEFAULT '',
  `created_at` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 
