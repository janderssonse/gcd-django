
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=735 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can view permission',1,'view_permission'),(5,'Can add group',2,'add_group'),(6,'Can change group',2,'change_group'),(7,'Can delete group',2,'delete_group'),(8,'Can view group',2,'view_group'),(9,'Can add user',3,'add_user'),(10,'Can change user',3,'change_user'),(11,'Can delete user',3,'delete_user'),(12,'Can view user',3,'view_user'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add log entry',6,'add_logentry'),(22,'Can change log entry',6,'change_logentry'),(23,'Can delete log entry',6,'delete_logentry'),(24,'Can view log entry',6,'view_logentry'),(25,'Can add site',7,'add_site'),(26,'Can change site',7,'change_site'),(27,'Can delete site',7,'delete_site'),(28,'Can view site',7,'view_site'),(29,'Can add error',8,'add_error'),(30,'Can change error',8,'change_error'),(31,'Can delete error',8,'delete_error'),(32,'Can view error',8,'view_error'),(33,'Can add imp grant',9,'add_impgrant'),(34,'Can change imp grant',9,'change_impgrant'),(35,'Can delete imp grant',9,'delete_impgrant'),(36,'Can view imp grant',9,'view_impgrant'),(37,'Can add indexer',10,'add_indexer'),(38,'Can change indexer',10,'change_indexer'),(39,'Can delete indexer',10,'delete_indexer'),(40,'Can view indexer',10,'view_indexer'),(41,'Can upload covers',10,'can_upload_cover'),(42,'Can reserve a record for add, edit or delete',10,'can_reserve'),(43,'Can approve a change to a record',10,'can_approve'),(44,'Can cancel a pending change they did not open',10,'can_cancel'),(45,'Can mentor new indexers',10,'can_mentor'),(46,'Can vote in GCD elections',10,'can_vote'),(47,'Can publish non-database content on the web site',10,'can_publish'),(48,'Can see list of users who have opted-in',10,'can_contact'),(49,'Is on the Board of Directors',10,'on_board'),(50,'Can add brand',11,'add_brand'),(51,'Can change brand',11,'change_brand'),(52,'Can delete brand',11,'delete_brand'),(53,'Can view brand',11,'view_brand'),(54,'Can add brand group',12,'add_brandgroup'),(55,'Can change brand group',12,'change_brandgroup'),(56,'Can delete brand group',12,'delete_brandgroup'),(57,'Can view brand group',12,'view_brandgroup'),(58,'Can add brand use',13,'add_branduse'),(59,'Can change brand use',13,'change_branduse'),(60,'Can delete brand use',13,'delete_branduse'),(61,'Can view brand use',13,'view_branduse'),(62,'Can add cover',14,'add_cover'),(63,'Can change cover',14,'change_cover'),(64,'Can delete cover',14,'delete_cover'),(65,'Can view cover',14,'view_cover'),(66,'can upload cover',14,'can_upload_cover'),(67,'Can add image',15,'add_image'),(68,'Can change image',15,'change_image'),(69,'Can delete image',15,'delete_image'),(70,'Can view image',15,'view_image'),(71,'Can add image type',16,'add_imagetype'),(72,'Can change image type',16,'change_imagetype'),(73,'Can delete image type',16,'delete_imagetype'),(74,'Can view image type',16,'view_imagetype'),(75,'Can add indicia publisher',17,'add_indiciapublisher'),(76,'Can change indicia publisher',17,'change_indiciapublisher'),(77,'Can delete indicia publisher',17,'delete_indiciapublisher'),(78,'Can view indicia publisher',17,'view_indiciapublisher'),(79,'Can add issue',18,'add_issue'),(80,'Can change issue',18,'change_issue'),(81,'Can delete issue',18,'delete_issue'),(82,'Can view issue',18,'view_issue'),(83,'Can add publisher',19,'add_publisher'),(84,'Can change publisher',19,'change_publisher'),(85,'Can delete publisher',19,'delete_publisher'),(86,'Can view publisher',19,'view_publisher'),(87,'Can add reprint',20,'add_reprint'),(88,'Can change reprint',20,'change_reprint'),(89,'Can delete reprint',20,'delete_reprint'),(90,'Can view reprint',20,'view_reprint'),(91,'Can add series',21,'add_series'),(92,'Can change series',21,'change_series'),(93,'Can delete series',21,'delete_series'),(94,'Can view series',21,'view_series'),(95,'Can add series bond',22,'add_seriesbond'),(96,'Can change series bond',22,'change_seriesbond'),(97,'Can delete series bond',22,'delete_seriesbond'),(98,'Can view series bond',22,'view_seriesbond'),(99,'Can add series bond type',23,'add_seriesbondtype'),(100,'Can change series bond type',23,'change_seriesbondtype'),(101,'Can delete series bond type',23,'delete_seriesbondtype'),(102,'Can view series bond type',23,'view_seriesbondtype'),(103,'Can add series publication type',24,'add_seriespublicationtype'),(104,'Can change series publication type',24,'change_seriespublicationtype'),(105,'Can delete series publication type',24,'delete_seriespublicationtype'),(106,'Can view series publication type',24,'view_seriespublicationtype'),(107,'Can add story',25,'add_story'),(108,'Can change story',25,'change_story'),(109,'Can delete story',25,'delete_story'),(110,'Can view story',25,'view_story'),(111,'Can add story type',26,'add_storytype'),(112,'Can change story type',26,'change_storytype'),(113,'Can delete story type',26,'delete_storytype'),(114,'Can view story type',26,'view_storytype'),(115,'Can add award',27,'add_award'),(116,'Can change award',27,'change_award'),(117,'Can delete award',27,'delete_award'),(118,'Can view award',27,'view_award'),(119,'Can add creator',28,'add_creator'),(120,'Can change creator',28,'change_creator'),(121,'Can delete creator',28,'delete_creator'),(122,'Can view creator',28,'view_creator'),(123,'Can add creator art influence',29,'add_creatorartinfluence'),(124,'Can change creator art influence',29,'change_creatorartinfluence'),(125,'Can delete creator art influence',29,'delete_creatorartinfluence'),(126,'Can view creator art influence',29,'view_creatorartinfluence'),(127,'Can add creator degree',30,'add_creatordegree'),(128,'Can change creator degree',30,'change_creatordegree'),(129,'Can delete creator degree',30,'delete_creatordegree'),(130,'Can view creator degree',30,'view_creatordegree'),(131,'Can add creator membership',31,'add_creatormembership'),(132,'Can change creator membership',31,'change_creatormembership'),(133,'Can delete creator membership',31,'delete_creatormembership'),(134,'Can view creator membership',31,'view_creatormembership'),(135,'Can add creator name detail',32,'add_creatornamedetail'),(136,'Can change creator name detail',32,'change_creatornamedetail'),(137,'Can delete creator name detail',32,'delete_creatornamedetail'),(138,'Can view creator name detail',32,'view_creatornamedetail'),(139,'Can add creator non comic work',33,'add_creatornoncomicwork'),(140,'Can change creator non comic work',33,'change_creatornoncomicwork'),(141,'Can delete creator non comic work',33,'delete_creatornoncomicwork'),(142,'Can view creator non comic work',33,'view_creatornoncomicwork'),(143,'Can add creator relation',34,'add_creatorrelation'),(144,'Can change creator relation',34,'change_creatorrelation'),(145,'Can delete creator relation',34,'delete_creatorrelation'),(146,'Can view creator relation',34,'view_creatorrelation'),(147,'Can add creator school',35,'add_creatorschool'),(148,'Can change creator school',35,'change_creatorschool'),(149,'Can delete creator school',35,'delete_creatorschool'),(150,'Can view creator school',35,'view_creatorschool'),(151,'Can add data source',36,'add_datasource'),(152,'Can change data source',36,'change_datasource'),(153,'Can delete data source',36,'delete_datasource'),(154,'Can view data source',36,'view_datasource'),(155,'Can add degree',37,'add_degree'),(156,'Can change degree',37,'change_degree'),(157,'Can delete degree',37,'delete_degree'),(158,'Can view degree',37,'view_degree'),(159,'Can add membership type',38,'add_membershiptype'),(160,'Can change membership type',38,'change_membershiptype'),(161,'Can delete membership type',38,'delete_membershiptype'),(162,'Can view membership type',38,'view_membershiptype'),(163,'Can add name type',39,'add_nametype'),(164,'Can change name type',39,'change_nametype'),(165,'Can delete name type',39,'delete_nametype'),(166,'Can view name type',39,'view_nametype'),(167,'Can add non comic work role',40,'add_noncomicworkrole'),(168,'Can change non comic work role',40,'change_noncomicworkrole'),(169,'Can delete non comic work role',40,'delete_noncomicworkrole'),(170,'Can view non comic work role',40,'view_noncomicworkrole'),(171,'Can add non comic work type',41,'add_noncomicworktype'),(172,'Can change non comic work type',41,'change_noncomicworktype'),(173,'Can delete non comic work type',41,'delete_noncomicworktype'),(174,'Can view non comic work type',41,'view_noncomicworktype'),(175,'Can add non comic work year',42,'add_noncomicworkyear'),(176,'Can change non comic work year',42,'change_noncomicworkyear'),(177,'Can delete non comic work year',42,'delete_noncomicworkyear'),(178,'Can view non comic work year',42,'view_noncomicworkyear'),(179,'Can add relation type',43,'add_relationtype'),(180,'Can change relation type',43,'change_relationtype'),(181,'Can delete relation type',43,'delete_relationtype'),(182,'Can view relation type',43,'view_relationtype'),(183,'Can add school',44,'add_school'),(184,'Can change school',44,'change_school'),(185,'Can delete school',44,'delete_school'),(186,'Can view school',44,'view_school'),(187,'Can add source type',45,'add_sourcetype'),(188,'Can change source type',45,'change_sourcetype'),(189,'Can delete source type',45,'delete_sourcetype'),(190,'Can view source type',45,'view_sourcetype'),(191,'Can add biblio entry',46,'add_biblioentry'),(192,'Can change biblio entry',46,'change_biblioentry'),(193,'Can delete biblio entry',46,'delete_biblioentry'),(194,'Can view biblio entry',46,'view_biblioentry'),(195,'Can add received award',47,'add_receivedaward'),(196,'Can change received award',47,'change_receivedaward'),(197,'Can delete received award',47,'delete_receivedaward'),(198,'Can view received award',47,'view_receivedaward'),(199,'Can add feature',48,'add_feature'),(200,'Can change feature',48,'change_feature'),(201,'Can delete feature',48,'delete_feature'),(202,'Can view feature',48,'view_feature'),(203,'Can add feature logo',49,'add_featurelogo'),(204,'Can change feature logo',49,'change_featurelogo'),(205,'Can delete feature logo',49,'delete_featurelogo'),(206,'Can view feature logo',49,'view_featurelogo'),(207,'Can add feature type',50,'add_featuretype'),(208,'Can change feature type',50,'change_featuretype'),(209,'Can delete feature type',50,'delete_featuretype'),(210,'Can view feature type',50,'view_featuretype'),(211,'Can add feature relation',51,'add_featurerelation'),(212,'Can change feature relation',51,'change_featurerelation'),(213,'Can delete feature relation',51,'delete_featurerelation'),(214,'Can view feature relation',51,'view_featurerelation'),(215,'Can add feature relation type',52,'add_featurerelationtype'),(216,'Can change feature relation type',52,'change_featurerelationtype'),(217,'Can delete feature relation type',52,'delete_featurerelationtype'),(218,'Can view feature relation type',52,'view_featurerelationtype'),(219,'Can add credit type',53,'add_credittype'),(220,'Can change credit type',53,'change_credittype'),(221,'Can delete credit type',53,'delete_credittype'),(222,'Can view credit type',53,'view_credittype'),(223,'Can add story credit',54,'add_storycredit'),(224,'Can change story credit',54,'change_storycredit'),(225,'Can delete story credit',54,'delete_storycredit'),(226,'Can view story credit',54,'view_storycredit'),(227,'Can add issue credit',55,'add_issuecredit'),(228,'Can change issue credit',55,'change_issuecredit'),(229,'Can delete issue credit',55,'delete_issuecredit'),(230,'Can view issue credit',55,'view_issuecredit'),(231,'Can add printer',56,'add_printer'),(232,'Can change printer',56,'change_printer'),(233,'Can delete printer',56,'delete_printer'),(234,'Can view printer',56,'view_printer'),(235,'Can add indicia printer',57,'add_indiciaprinter'),(236,'Can change indicia printer',57,'change_indiciaprinter'),(237,'Can delete indicia printer',57,'delete_indiciaprinter'),(238,'Can view indicia printer',57,'view_indiciaprinter'),(239,'Can add creator signature',58,'add_creatorsignature'),(240,'Can change creator signature',58,'change_creatorsignature'),(241,'Can delete creator signature',58,'delete_creatorsignature'),(242,'Can view creator signature',58,'view_creatorsignature'),(243,'Can add character',59,'add_character'),(244,'Can change character',59,'change_character'),(245,'Can delete character',59,'delete_character'),(246,'Can view character',59,'view_character'),(247,'Can add character relation type',60,'add_characterrelationtype'),(248,'Can change character relation type',60,'change_characterrelationtype'),(249,'Can delete character relation type',60,'delete_characterrelationtype'),(250,'Can view character relation type',60,'view_characterrelationtype'),(251,'Can add group',61,'add_group'),(252,'Can change group',61,'change_group'),(253,'Can delete group',61,'delete_group'),(254,'Can view group',61,'view_group'),(255,'Can add group membership type',62,'add_groupmembershiptype'),(256,'Can change group membership type',62,'change_groupmembershiptype'),(257,'Can delete group membership type',62,'delete_groupmembershiptype'),(258,'Can view group membership type',62,'view_groupmembershiptype'),(259,'Can add group relation type',63,'add_grouprelationtype'),(260,'Can change group relation type',63,'change_grouprelationtype'),(261,'Can delete group relation type',63,'delete_grouprelationtype'),(262,'Can view group relation type',63,'view_grouprelationtype'),(263,'Can add group relation',64,'add_grouprelation'),(264,'Can change group relation',64,'change_grouprelation'),(265,'Can delete group relation',64,'delete_grouprelation'),(266,'Can view group relation',64,'view_grouprelation'),(267,'Can add group membership',65,'add_groupmembership'),(268,'Can change group membership',65,'change_groupmembership'),(269,'Can delete group membership',65,'delete_groupmembership'),(270,'Can view group membership',65,'view_groupmembership'),(271,'Can add character relation',66,'add_characterrelation'),(272,'Can change character relation',66,'change_characterrelation'),(273,'Can delete character relation',66,'delete_characterrelation'),(274,'Can view character relation',66,'view_characterrelation'),(275,'Can add character name detail',67,'add_characternamedetail'),(276,'Can change character name detail',67,'change_characternamedetail'),(277,'Can delete character name detail',67,'delete_characternamedetail'),(278,'Can view character name detail',67,'view_characternamedetail'),(279,'Can add code number type',68,'add_codenumbertype'),(280,'Can change code number type',68,'change_codenumbertype'),(281,'Can delete code number type',68,'delete_codenumbertype'),(282,'Can view code number type',68,'view_codenumbertype'),(283,'Can add publisher code number',69,'add_publishercodenumber'),(284,'Can change publisher code number',69,'change_publishercodenumber'),(285,'Can delete publisher code number',69,'delete_publishercodenumber'),(286,'Can view publisher code number',69,'view_publishercodenumber'),(287,'Can add character role',70,'add_characterrole'),(288,'Can change character role',70,'change_characterrole'),(289,'Can delete character role',70,'delete_characterrole'),(290,'Can view character role',70,'view_characterrole'),(291,'Can add story character',71,'add_storycharacter'),(292,'Can change story character',71,'change_storycharacter'),(293,'Can delete story character',71,'delete_storycharacter'),(294,'Can view story character',71,'view_storycharacter'),(295,'Can add external site',72,'add_externalsite'),(296,'Can change external site',72,'change_externalsite'),(297,'Can delete external site',72,'delete_externalsite'),(298,'Can view external site',72,'view_externalsite'),(299,'Can add external link',73,'add_externallink'),(300,'Can change external link',73,'change_externallink'),(301,'Can delete external link',73,'delete_externallink'),(302,'Can view external link',73,'view_externallink'),(303,'Can add universe',74,'add_universe'),(304,'Can change universe',74,'change_universe'),(305,'Can delete universe',74,'delete_universe'),(306,'Can view universe',74,'view_universe'),(307,'Can add story group',75,'add_storygroup'),(308,'Can change story group',75,'change_storygroup'),(309,'Can delete story group',75,'delete_storygroup'),(310,'Can view story group',75,'view_storygroup'),(311,'Can add multiverse',76,'add_multiverse'),(312,'Can change multiverse',76,'change_multiverse'),(313,'Can delete multiverse',76,'delete_multiverse'),(314,'Can view multiverse',76,'view_multiverse'),(315,'Can add group name detail',77,'add_groupnamedetail'),(316,'Can change group name detail',77,'change_groupnamedetail'),(317,'Can delete group name detail',77,'delete_groupnamedetail'),(318,'Can view group name detail',77,'view_groupnamedetail'),(319,'Can add story arc',78,'add_storyarc'),(320,'Can change story arc',78,'change_storyarc'),(321,'Can delete story arc',78,'delete_storyarc'),(322,'Can view story arc',78,'view_storyarc'),(323,'Can add story arc relation type',79,'add_storyarcrelationtype'),(324,'Can change story arc relation type',79,'change_storyarcrelationtype'),(325,'Can delete story arc relation type',79,'delete_storyarcrelationtype'),(326,'Can view story arc relation type',79,'view_storyarcrelationtype'),(327,'Can add story arc relation',80,'add_storyarcrelation'),(328,'Can change story arc relation',80,'change_storyarcrelation'),(329,'Can delete story arc relation',80,'delete_storyarcrelation'),(330,'Can view story arc relation',80,'view_storyarcrelation'),(331,'Can add character order type',81,'add_characterordertype'),(332,'Can change character order type',81,'change_characterordertype'),(333,'Can delete character order type',81,'delete_characterordertype'),(334,'Can view character order type',81,'view_characterordertype'),(335,'Can add character order',82,'add_characterorder'),(336,'Can change character order',82,'change_characterorder'),(337,'Can delete character order',82,'delete_characterorder'),(338,'Can view character order',82,'view_characterorder'),(339,'Can add character through order',83,'add_characterthroughorder'),(340,'Can change character through order',83,'change_characterthroughorder'),(341,'Can delete character through order',83,'delete_characterthroughorder'),(342,'Can view character through order',83,'view_characterthroughorder'),(343,'Can add count stats',84,'add_countstats'),(344,'Can change count stats',84,'change_countstats'),(345,'Can delete count stats',84,'delete_countstats'),(346,'Can view count stats',84,'view_countstats'),(347,'Can add download',85,'add_download'),(348,'Can change download',85,'change_download'),(349,'Can delete download',85,'delete_download'),(350,'Can view download',85,'view_download'),(351,'Can add recent indexed issue',86,'add_recentindexedissue'),(352,'Can change recent indexed issue',86,'change_recentindexedissue'),(353,'Can delete recent indexed issue',86,'delete_recentindexedissue'),(354,'Can view recent indexed issue',86,'view_recentindexedissue'),(355,'Can add index credit',87,'add_indexcredit'),(356,'Can change index credit',87,'change_indexcredit'),(357,'Can delete index credit',87,'delete_indexcredit'),(358,'Can view index credit',87,'view_indexcredit'),(359,'Can add migration story status',88,'add_migrationstorystatus'),(360,'Can change migration story status',88,'change_migrationstorystatus'),(361,'Can delete migration story status',88,'delete_migrationstorystatus'),(362,'Can view migration story status',88,'view_migrationstorystatus'),(363,'Can add reservation',89,'add_reservation'),(364,'Can change reservation',89,'change_reservation'),(365,'Can delete reservation',89,'delete_reservation'),(366,'Can view reservation',89,'view_reservation'),(367,'Can add brand group revision',90,'add_brandgrouprevision'),(368,'Can change brand group revision',90,'change_brandgrouprevision'),(369,'Can delete brand group revision',90,'delete_brandgrouprevision'),(370,'Can view brand group revision',90,'view_brandgrouprevision'),(371,'Can add brand revision',91,'add_brandrevision'),(372,'Can change brand revision',91,'change_brandrevision'),(373,'Can delete brand revision',91,'delete_brandrevision'),(374,'Can view brand revision',91,'view_brandrevision'),(375,'Can add brand use revision',92,'add_branduserevision'),(376,'Can change brand use revision',92,'change_branduserevision'),(377,'Can delete brand use revision',92,'delete_branduserevision'),(378,'Can view brand use revision',92,'view_branduserevision'),(379,'Can add changeset',93,'add_changeset'),(380,'Can change changeset',93,'change_changeset'),(381,'Can delete changeset',93,'delete_changeset'),(382,'Can view changeset',93,'view_changeset'),(383,'Can add changeset comment',94,'add_changesetcomment'),(384,'Can change changeset comment',94,'change_changesetcomment'),(385,'Can delete changeset comment',94,'delete_changesetcomment'),(386,'Can view changeset comment',94,'view_changesetcomment'),(387,'Can add cover revision',95,'add_coverrevision'),(388,'Can change cover revision',95,'change_coverrevision'),(389,'Can delete cover revision',95,'delete_coverrevision'),(390,'Can view cover revision',95,'view_coverrevision'),(391,'Can add image revision',96,'add_imagerevision'),(392,'Can change image revision',96,'change_imagerevision'),(393,'Can delete image revision',96,'delete_imagerevision'),(394,'Can view image revision',96,'view_imagerevision'),(395,'Can add indicia publisher revision',97,'add_indiciapublisherrevision'),(396,'Can change indicia publisher revision',97,'change_indiciapublisherrevision'),(397,'Can delete indicia publisher revision',97,'delete_indiciapublisherrevision'),(398,'Can view indicia publisher revision',97,'view_indiciapublisherrevision'),(399,'Can add issue revision',98,'add_issuerevision'),(400,'Can change issue revision',98,'change_issuerevision'),(401,'Can delete issue revision',98,'delete_issuerevision'),(402,'Can view issue revision',98,'view_issuerevision'),(403,'Can add ongoing reservation',99,'add_ongoingreservation'),(404,'Can change ongoing reservation',99,'change_ongoingreservation'),(405,'Can delete ongoing reservation',99,'delete_ongoingreservation'),(406,'Can view ongoing reservation',99,'view_ongoingreservation'),(407,'Can add publisher revision',100,'add_publisherrevision'),(408,'Can change publisher revision',100,'change_publisherrevision'),(409,'Can delete publisher revision',100,'delete_publisherrevision'),(410,'Can view publisher revision',100,'view_publisherrevision'),(411,'Can add reprint revision',101,'add_reprintrevision'),(412,'Can change reprint revision',101,'change_reprintrevision'),(413,'Can delete reprint revision',101,'delete_reprintrevision'),(414,'Can view reprint revision',101,'view_reprintrevision'),(415,'Can add series bond revision',102,'add_seriesbondrevision'),(416,'Can change series bond revision',102,'change_seriesbondrevision'),(417,'Can delete series bond revision',102,'delete_seriesbondrevision'),(418,'Can view series bond revision',102,'view_seriesbondrevision'),(419,'Can add series revision',103,'add_seriesrevision'),(420,'Can change series revision',103,'change_seriesrevision'),(421,'Can delete series revision',103,'delete_seriesrevision'),(422,'Can view series revision',103,'view_seriesrevision'),(423,'Can add story revision',104,'add_storyrevision'),(424,'Can change story revision',104,'change_storyrevision'),(425,'Can delete story revision',104,'delete_storyrevision'),(426,'Can view story revision',104,'view_storyrevision'),(427,'Can add revision lock',105,'add_revisionlock'),(428,'Can change revision lock',105,'change_revisionlock'),(429,'Can delete revision lock',105,'delete_revisionlock'),(430,'Can view revision lock',105,'view_revisionlock'),(431,'Can add creator art influence revision',106,'add_creatorartinfluencerevision'),(432,'Can change creator art influence revision',106,'change_creatorartinfluencerevision'),(433,'Can delete creator art influence revision',106,'delete_creatorartinfluencerevision'),(434,'Can view creator art influence revision',106,'view_creatorartinfluencerevision'),(435,'Can add creator degree revision',107,'add_creatordegreerevision'),(436,'Can change creator degree revision',107,'change_creatordegreerevision'),(437,'Can delete creator degree revision',107,'delete_creatordegreerevision'),(438,'Can view creator degree revision',107,'view_creatordegreerevision'),(439,'Can add creator membership revision',108,'add_creatormembershiprevision'),(440,'Can change creator membership revision',108,'change_creatormembershiprevision'),(441,'Can delete creator membership revision',108,'delete_creatormembershiprevision'),(442,'Can view creator membership revision',108,'view_creatormembershiprevision'),(443,'Can add creator name detail revision',109,'add_creatornamedetailrevision'),(444,'Can change creator name detail revision',109,'change_creatornamedetailrevision'),(445,'Can delete creator name detail revision',109,'delete_creatornamedetailrevision'),(446,'Can view creator name detail revision',109,'view_creatornamedetailrevision'),(447,'Can add creator non comic work revision',110,'add_creatornoncomicworkrevision'),(448,'Can change creator non comic work revision',110,'change_creatornoncomicworkrevision'),(449,'Can delete creator non comic work revision',110,'delete_creatornoncomicworkrevision'),(450,'Can view creator non comic work revision',110,'view_creatornoncomicworkrevision'),(451,'Can add creator relation revision',111,'add_creatorrelationrevision'),(452,'Can change creator relation revision',111,'change_creatorrelationrevision'),(453,'Can delete creator relation revision',111,'delete_creatorrelationrevision'),(454,'Can view creator relation revision',111,'view_creatorrelationrevision'),(455,'Can add creator revision',112,'add_creatorrevision'),(456,'Can change creator revision',112,'change_creatorrevision'),(457,'Can delete creator revision',112,'delete_creatorrevision'),(458,'Can view creator revision',112,'view_creatorrevision'),(459,'Can add creator school revision',113,'add_creatorschoolrevision'),(460,'Can change creator school revision',113,'change_creatorschoolrevision'),(461,'Can delete creator school revision',113,'delete_creatorschoolrevision'),(462,'Can view creator school revision',113,'view_creatorschoolrevision'),(463,'Can add data source revision',114,'add_datasourcerevision'),(464,'Can change data source revision',114,'change_datasourcerevision'),(465,'Can delete data source revision',114,'delete_datasourcerevision'),(466,'Can view data source revision',114,'view_datasourcerevision'),(467,'Can add award revision',115,'add_awardrevision'),(468,'Can change award revision',115,'change_awardrevision'),(469,'Can delete award revision',115,'delete_awardrevision'),(470,'Can view award revision',115,'view_awardrevision'),(471,'Can add preview brand',116,'add_previewbrand'),(472,'Can change preview brand',116,'change_previewbrand'),(473,'Can delete preview brand',116,'delete_previewbrand'),(474,'Can view preview brand',116,'view_previewbrand'),(475,'Can add preview creator',117,'add_previewcreator'),(476,'Can change preview creator',117,'change_previewcreator'),(477,'Can delete preview creator',117,'delete_previewcreator'),(478,'Can view preview creator',117,'view_previewcreator'),(479,'Can add preview creator art influence',118,'add_previewcreatorartinfluence'),(480,'Can change preview creator art influence',118,'change_previewcreatorartinfluence'),(481,'Can delete preview creator art influence',118,'delete_previewcreatorartinfluence'),(482,'Can view preview creator art influence',118,'view_previewcreatorartinfluence'),(483,'Can add preview creator degree',119,'add_previewcreatordegree'),(484,'Can change preview creator degree',119,'change_previewcreatordegree'),(485,'Can delete preview creator degree',119,'delete_previewcreatordegree'),(486,'Can view preview creator degree',119,'view_previewcreatordegree'),(487,'Can add preview creator membership',120,'add_previewcreatormembership'),(488,'Can change preview creator membership',120,'change_previewcreatormembership'),(489,'Can delete preview creator membership',120,'delete_previewcreatormembership'),(490,'Can view preview creator membership',120,'view_previewcreatormembership'),(491,'Can add preview creator non comic work',121,'add_previewcreatornoncomicwork'),(492,'Can change preview creator non comic work',121,'change_previewcreatornoncomicwork'),(493,'Can delete preview creator non comic work',121,'delete_previewcreatornoncomicwork'),(494,'Can view preview creator non comic work',121,'view_previewcreatornoncomicwork'),(495,'Can add preview creator school',122,'add_previewcreatorschool'),(496,'Can change preview creator school',122,'change_previewcreatorschool'),(497,'Can delete preview creator school',122,'delete_previewcreatorschool'),(498,'Can view preview creator school',122,'view_previewcreatorschool'),(499,'Can add preview issue',123,'add_previewissue'),(500,'Can change preview issue',123,'change_previewissue'),(501,'Can delete preview issue',123,'delete_previewissue'),(502,'Can view preview issue',123,'view_previewissue'),(503,'Can add preview story',124,'add_previewstory'),(504,'Can change preview story',124,'change_previewstory'),(505,'Can delete preview story',124,'delete_previewstory'),(506,'Can view preview story',124,'view_previewstory'),(507,'Can add biblio entry revision',125,'add_biblioentryrevision'),(508,'Can change biblio entry revision',125,'change_biblioentryrevision'),(509,'Can delete biblio entry revision',125,'delete_biblioentryrevision'),(510,'Can view biblio entry revision',125,'view_biblioentryrevision'),(511,'Can add received award revision',126,'add_receivedawardrevision'),(512,'Can change received award revision',126,'change_receivedawardrevision'),(513,'Can delete received award revision',126,'delete_receivedawardrevision'),(514,'Can view received award revision',126,'view_receivedawardrevision'),(515,'Can add preview received award',127,'add_previewreceivedaward'),(516,'Can change preview received award',127,'change_previewreceivedaward'),(517,'Can delete preview received award',127,'delete_previewreceivedaward'),(518,'Can view preview received award',127,'view_previewreceivedaward'),(519,'Can add feature logo revision',128,'add_featurelogorevision'),(520,'Can change feature logo revision',128,'change_featurelogorevision'),(521,'Can delete feature logo revision',128,'delete_featurelogorevision'),(522,'Can view feature logo revision',128,'view_featurelogorevision'),(523,'Can add feature revision',129,'add_featurerevision'),(524,'Can change feature revision',129,'change_featurerevision'),(525,'Can delete feature revision',129,'delete_featurerevision'),(526,'Can view feature revision',129,'view_featurerevision'),(527,'Can add feature relation revision',130,'add_featurerelationrevision'),(528,'Can change feature relation revision',130,'change_featurerelationrevision'),(529,'Can delete feature relation revision',130,'delete_featurerelationrevision'),(530,'Can view feature relation revision',130,'view_featurerelationrevision'),(531,'Can add story credit revision',131,'add_storycreditrevision'),(532,'Can change story credit revision',131,'change_storycreditrevision'),(533,'Can delete story credit revision',131,'delete_storycreditrevision'),(534,'Can view story credit revision',131,'view_storycreditrevision'),(535,'Can add issue credit revision',132,'add_issuecreditrevision'),(536,'Can change issue credit revision',132,'change_issuecreditrevision'),(537,'Can delete issue credit revision',132,'delete_issuecreditrevision'),(538,'Can view issue credit revision',132,'view_issuecreditrevision'),(539,'Can add printer revision',133,'add_printerrevision'),(540,'Can change printer revision',133,'change_printerrevision'),(541,'Can delete printer revision',133,'delete_printerrevision'),(542,'Can view printer revision',133,'view_printerrevision'),(543,'Can add indicia printer revision',134,'add_indiciaprinterrevision'),(544,'Can change indicia printer revision',134,'change_indiciaprinterrevision'),(545,'Can delete indicia printer revision',134,'delete_indiciaprinterrevision'),(546,'Can view indicia printer revision',134,'view_indiciaprinterrevision'),(547,'Can add creator signature revision',135,'add_creatorsignaturerevision'),(548,'Can change creator signature revision',135,'change_creatorsignaturerevision'),(549,'Can delete creator signature revision',135,'delete_creatorsignaturerevision'),(550,'Can view creator signature revision',135,'view_creatorsignaturerevision'),(551,'Can add group revision',136,'add_grouprevision'),(552,'Can change group revision',136,'change_grouprevision'),(553,'Can delete group revision',136,'delete_grouprevision'),(554,'Can view group revision',136,'view_grouprevision'),(555,'Can add group relation revision',137,'add_grouprelationrevision'),(556,'Can change group relation revision',137,'change_grouprelationrevision'),(557,'Can delete group relation revision',137,'delete_grouprelationrevision'),(558,'Can view group relation revision',137,'view_grouprelationrevision'),(559,'Can add group membership revision',138,'add_groupmembershiprevision'),(560,'Can change group membership revision',138,'change_groupmembershiprevision'),(561,'Can delete group membership revision',138,'delete_groupmembershiprevision'),(562,'Can view group membership revision',138,'view_groupmembershiprevision'),(563,'Can add character revision',139,'add_characterrevision'),(564,'Can change character revision',139,'change_characterrevision'),(565,'Can delete character revision',139,'delete_characterrevision'),(566,'Can view character revision',139,'view_characterrevision'),(567,'Can add character relation revision',140,'add_characterrelationrevision'),(568,'Can change character relation revision',140,'change_characterrelationrevision'),(569,'Can delete character relation revision',140,'delete_characterrelationrevision'),(570,'Can view character relation revision',140,'view_characterrelationrevision'),(571,'Can add character name detail revision',141,'add_characternamedetailrevision'),(572,'Can change character name detail revision',141,'change_characternamedetailrevision'),(573,'Can delete character name detail revision',141,'delete_characternamedetailrevision'),(574,'Can view character name detail revision',141,'view_characternamedetailrevision'),(575,'Can add publisher code number revision',142,'add_publishercodenumberrevision'),(576,'Can change publisher code number revision',142,'change_publishercodenumberrevision'),(577,'Can delete publisher code number revision',142,'delete_publishercodenumberrevision'),(578,'Can view publisher code number revision',142,'view_publishercodenumberrevision'),(579,'Can add story character revision',143,'add_storycharacterrevision'),(580,'Can change story character revision',143,'change_storycharacterrevision'),(581,'Can delete story character revision',143,'delete_storycharacterrevision'),(582,'Can view story character revision',143,'view_storycharacterrevision'),(583,'Can add external link revision',144,'add_externallinkrevision'),(584,'Can change external link revision',144,'change_externallinkrevision'),(585,'Can delete external link revision',144,'delete_externallinkrevision'),(586,'Can view external link revision',144,'view_externallinkrevision'),(587,'Can add preview character',145,'add_previewcharacter'),(588,'Can change preview character',145,'change_previewcharacter'),(589,'Can delete preview character',145,'delete_previewcharacter'),(590,'Can view preview character',145,'view_previewcharacter'),(591,'Can add preview universe',146,'add_previewuniverse'),(592,'Can change preview universe',146,'change_previewuniverse'),(593,'Can delete preview universe',146,'delete_previewuniverse'),(594,'Can view preview universe',146,'view_previewuniverse'),(595,'Can add universe revision',147,'add_universerevision'),(596,'Can change universe revision',147,'change_universerevision'),(597,'Can delete universe revision',147,'delete_universerevision'),(598,'Can view universe revision',147,'view_universerevision'),(599,'Can add story group revision',148,'add_storygrouprevision'),(600,'Can change story group revision',148,'change_storygrouprevision'),(601,'Can delete story group revision',148,'delete_storygrouprevision'),(602,'Can view story group revision',148,'view_storygrouprevision'),(603,'Can add group name detail revision',149,'add_groupnamedetailrevision'),(604,'Can change group name detail revision',149,'change_groupnamedetailrevision'),(605,'Can delete group name detail revision',149,'delete_groupnamedetailrevision'),(606,'Can view group name detail revision',149,'view_groupnamedetailrevision'),(607,'Can add story arc revision',150,'add_storyarcrevision'),(608,'Can change story arc revision',150,'change_storyarcrevision'),(609,'Can delete story arc revision',150,'delete_storyarcrevision'),(610,'Can view story arc revision',150,'view_storyarcrevision'),(611,'Can add story arc relation revision',151,'add_storyarcrelationrevision'),(612,'Can change story arc relation revision',151,'change_storyarcrelationrevision'),(613,'Can delete story arc relation revision',151,'delete_storyarcrelationrevision'),(614,'Can view story arc relation revision',151,'view_storyarcrelationrevision'),(615,'Can add character order revision',152,'add_characterorderrevision'),(616,'Can change character order revision',152,'change_characterorderrevision'),(617,'Can delete character order revision',152,'delete_characterorderrevision'),(618,'Can view character order revision',152,'view_characterorderrevision'),(619,'Can add character through order revision',153,'add_characterthroughorderrevision'),(620,'Can change character through order revision',153,'change_characterthroughorderrevision'),(621,'Can delete character through order revision',153,'delete_characterthroughorderrevision'),(622,'Can view character through order revision',153,'view_characterthroughorderrevision'),(623,'Can add agenda',154,'add_agenda'),(624,'Can change agenda',154,'change_agenda'),(625,'Can delete agenda',154,'delete_agenda'),(626,'Can view agenda',154,'view_agenda'),(627,'Can add agenda item',155,'add_agendaitem'),(628,'Can change agenda item',155,'change_agendaitem'),(629,'Can delete agenda item',155,'delete_agendaitem'),(630,'Can view agenda item',155,'view_agendaitem'),(631,'Can add agenda mailing list',156,'add_agendamailinglist'),(632,'Can change agenda mailing list',156,'change_agendamailinglist'),(633,'Can delete agenda mailing list',156,'delete_agendamailinglist'),(634,'Can view agenda mailing list',156,'view_agendamailinglist'),(635,'Can add expected voter',157,'add_expectedvoter'),(636,'Can change expected voter',157,'change_expectedvoter'),(637,'Can delete expected voter',157,'delete_expectedvoter'),(638,'Can view expected voter',157,'view_expectedvoter'),(639,'Can add mailing list',158,'add_mailinglist'),(640,'Can change mailing list',158,'change_mailinglist'),(641,'Can delete mailing list',158,'delete_mailinglist'),(642,'Can view mailing list',158,'view_mailinglist'),(643,'Can add option',159,'add_option'),(644,'Can change option',159,'change_option'),(645,'Can delete option',159,'delete_option'),(646,'Can view option',159,'view_option'),(647,'Can add receipt',160,'add_receipt'),(648,'Can change receipt',160,'change_receipt'),(649,'Can delete receipt',160,'delete_receipt'),(650,'Can view receipt',160,'view_receipt'),(651,'Can add topic',161,'add_topic'),(652,'Can change topic',161,'change_topic'),(653,'Can delete topic',161,'delete_topic'),(654,'Can view topic',161,'view_topic'),(655,'Can add vote',162,'add_vote'),(656,'Can change vote',162,'change_vote'),(657,'Can delete vote',162,'delete_vote'),(658,'Can view vote',162,'view_vote'),(659,'Can add vote type',163,'add_votetype'),(660,'Can change vote type',163,'change_votetype'),(661,'Can delete vote type',163,'delete_votetype'),(662,'Can view vote type',163,'view_votetype'),(663,'Can add country',164,'add_country'),(664,'Can change country',164,'change_country'),(665,'Can delete country',164,'delete_country'),(666,'Can view country',164,'view_country'),(667,'Can add currency',165,'add_currency'),(668,'Can change currency',165,'change_currency'),(669,'Can delete currency',165,'delete_currency'),(670,'Can view currency',165,'view_currency'),(671,'Can add date',166,'add_date'),(672,'Can change date',166,'change_date'),(673,'Can delete date',166,'delete_date'),(674,'Can view date',166,'view_date'),(675,'Can add language',167,'add_language'),(676,'Can change language',167,'change_language'),(677,'Can delete language',167,'delete_language'),(678,'Can view language',167,'view_language'),(679,'Can add script',168,'add_script'),(680,'Can change script',168,'change_script'),(681,'Can delete script',168,'delete_script'),(682,'Can view script',168,'view_script'),(683,'Can add collection',169,'add_collection'),(684,'Can change collection',169,'change_collection'),(685,'Can delete collection',169,'delete_collection'),(686,'Can view collection',169,'view_collection'),(687,'Can add collection item',170,'add_collectionitem'),(688,'Can change collection item',170,'change_collectionitem'),(689,'Can delete collection item',170,'delete_collectionitem'),(690,'Can view collection item',170,'view_collectionitem'),(691,'Can add collector',171,'add_collector'),(692,'Can change collector',171,'change_collector'),(693,'Can delete collector',171,'delete_collector'),(694,'Can view collector',171,'view_collector'),(695,'Can add condition grade',172,'add_conditiongrade'),(696,'Can change condition grade',172,'change_conditiongrade'),(697,'Can delete condition grade',172,'delete_conditiongrade'),(698,'Can view condition grade',172,'view_conditiongrade'),(699,'Can add condition grade scale',173,'add_conditiongradescale'),(700,'Can change condition grade scale',173,'change_conditiongradescale'),(701,'Can delete condition grade scale',173,'delete_conditiongradescale'),(702,'Can view condition grade scale',173,'view_conditiongradescale'),(703,'Can add location',174,'add_location'),(704,'Can change location',174,'change_location'),(705,'Can delete location',174,'delete_location'),(706,'Can view location',174,'view_location'),(707,'Can add purchase location',175,'add_purchaselocation'),(708,'Can change purchase location',175,'change_purchaselocation'),(709,'Can delete purchase location',175,'delete_purchaselocation'),(710,'Can view purchase location',175,'view_purchaselocation'),(711,'Can add subscription',176,'add_subscription'),(712,'Can change subscription',176,'change_subscription'),(713,'Can delete subscription',176,'delete_subscription'),(714,'Can view subscription',176,'view_subscription'),(715,'Can add reading order',177,'add_readingorder'),(716,'Can change reading order',177,'change_readingorder'),(717,'Can delete reading order',177,'delete_readingorder'),(718,'Can view reading order',177,'view_readingorder'),(719,'Can add reading order item',178,'add_readingorderitem'),(720,'Can change reading order item',178,'change_readingorderitem'),(721,'Can delete reading order item',178,'delete_readingorderitem'),(722,'Can view reading order item',178,'view_readingorderitem'),(723,'Can add Template',179,'add_ftemplate'),(724,'Can change Template',179,'change_ftemplate'),(725,'Can delete Template',179,'delete_ftemplate'),(726,'Can view Template',179,'view_ftemplate'),(727,'Can add tag',180,'add_tag'),(728,'Can change tag',180,'change_tag'),(729,'Can delete tag',180,'delete_tag'),(730,'Can view tag',180,'view_tag'),(731,'Can add tagged item',181,'add_taggeditem'),(732,'Can change tagged item',181,'change_taggeditem'),(733,'Can delete tagged item',181,'delete_taggeditem'),(734,'Can view tagged item',181,'view_taggeditem');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=182 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'admin','logentry'),(2,'auth','group'),(1,'auth','permission'),(3,'auth','user'),(4,'contenttypes','contenttype'),(27,'gcd','award'),(46,'gcd','biblioentry'),(11,'gcd','brand'),(12,'gcd','brandgroup'),(13,'gcd','branduse'),(59,'gcd','character'),(67,'gcd','characternamedetail'),(82,'gcd','characterorder'),(81,'gcd','characterordertype'),(66,'gcd','characterrelation'),(60,'gcd','characterrelationtype'),(70,'gcd','characterrole'),(83,'gcd','characterthroughorder'),(68,'gcd','codenumbertype'),(14,'gcd','cover'),(28,'gcd','creator'),(29,'gcd','creatorartinfluence'),(30,'gcd','creatordegree'),(31,'gcd','creatormembership'),(32,'gcd','creatornamedetail'),(33,'gcd','creatornoncomicwork'),(34,'gcd','creatorrelation'),(35,'gcd','creatorschool'),(58,'gcd','creatorsignature'),(53,'gcd','credittype'),(36,'gcd','datasource'),(37,'gcd','degree'),(73,'gcd','externallink'),(72,'gcd','externalsite'),(48,'gcd','feature'),(49,'gcd','featurelogo'),(51,'gcd','featurerelation'),(52,'gcd','featurerelationtype'),(50,'gcd','featuretype'),(61,'gcd','group'),(65,'gcd','groupmembership'),(62,'gcd','groupmembershiptype'),(77,'gcd','groupnamedetail'),(64,'gcd','grouprelation'),(63,'gcd','grouprelationtype'),(15,'gcd','image'),(16,'gcd','imagetype'),(57,'gcd','indiciaprinter'),(17,'gcd','indiciapublisher'),(18,'gcd','issue'),(55,'gcd','issuecredit'),(38,'gcd','membershiptype'),(76,'gcd','multiverse'),(39,'gcd','nametype'),(40,'gcd','noncomicworkrole'),(41,'gcd','noncomicworktype'),(42,'gcd','noncomicworkyear'),(56,'gcd','printer'),(19,'gcd','publisher'),(69,'gcd','publishercodenumber'),(47,'gcd','receivedaward'),(43,'gcd','relationtype'),(20,'gcd','reprint'),(44,'gcd','school'),(21,'gcd','series'),(22,'gcd','seriesbond'),(23,'gcd','seriesbondtype'),(24,'gcd','seriespublicationtype'),(45,'gcd','sourcetype'),(25,'gcd','story'),(78,'gcd','storyarc'),(80,'gcd','storyarcrelation'),(79,'gcd','storyarcrelationtype'),(71,'gcd','storycharacter'),(54,'gcd','storycredit'),(75,'gcd','storygroup'),(26,'gcd','storytype'),(74,'gcd','universe'),(8,'indexer','error'),(9,'indexer','impgrant'),(10,'indexer','indexer'),(87,'legacy','indexcredit'),(88,'legacy','migrationstorystatus'),(89,'legacy','reservation'),(169,'mycomics','collection'),(170,'mycomics','collectionitem'),(171,'mycomics','collector'),(172,'mycomics','conditiongrade'),(173,'mycomics','conditiongradescale'),(174,'mycomics','location'),(175,'mycomics','purchaselocation'),(177,'mycomics','readingorder'),(178,'mycomics','readingorderitem'),(176,'mycomics','subscription'),(115,'oi','awardrevision'),(125,'oi','biblioentryrevision'),(90,'oi','brandgrouprevision'),(91,'oi','brandrevision'),(92,'oi','branduserevision'),(93,'oi','changeset'),(94,'oi','changesetcomment'),(141,'oi','characternamedetailrevision'),(152,'oi','characterorderrevision'),(140,'oi','characterrelationrevision'),(139,'oi','characterrevision'),(153,'oi','characterthroughorderrevision'),(95,'oi','coverrevision'),(106,'oi','creatorartinfluencerevision'),(107,'oi','creatordegreerevision'),(108,'oi','creatormembershiprevision'),(109,'oi','creatornamedetailrevision'),(110,'oi','creatornoncomicworkrevision'),(111,'oi','creatorrelationrevision'),(112,'oi','creatorrevision'),(113,'oi','creatorschoolrevision'),(135,'oi','creatorsignaturerevision'),(114,'oi','datasourcerevision'),(144,'oi','externallinkrevision'),(128,'oi','featurelogorevision'),(130,'oi','featurerelationrevision'),(129,'oi','featurerevision'),(138,'oi','groupmembershiprevision'),(149,'oi','groupnamedetailrevision'),(137,'oi','grouprelationrevision'),(136,'oi','grouprevision'),(96,'oi','imagerevision'),(134,'oi','indiciaprinterrevision'),(97,'oi','indiciapublisherrevision'),(132,'oi','issuecreditrevision'),(98,'oi','issuerevision'),(99,'oi','ongoingreservation'),(116,'oi','previewbrand'),(145,'oi','previewcharacter'),(117,'oi','previewcreator'),(118,'oi','previewcreatorartinfluence'),(119,'oi','previewcreatordegree'),(120,'oi','previewcreatormembership'),(121,'oi','previewcreatornoncomicwork'),(122,'oi','previewcreatorschool'),(123,'oi','previewissue'),(127,'oi','previewreceivedaward'),(124,'oi','previewstory'),(146,'oi','previewuniverse'),(133,'oi','printerrevision'),(142,'oi','publishercodenumberrevision'),(100,'oi','publisherrevision'),(126,'oi','receivedawardrevision'),(101,'oi','reprintrevision'),(105,'oi','revisionlock'),(102,'oi','seriesbondrevision'),(103,'oi','seriesrevision'),(151,'oi','storyarcrelationrevision'),(150,'oi','storyarcrevision'),(143,'oi','storycharacterrevision'),(131,'oi','storycreditrevision'),(148,'oi','storygrouprevision'),(104,'oi','storyrevision'),(147,'oi','universerevision'),(5,'sessions','session'),(7,'sites','site'),(84,'stats','countstats'),(85,'stats','download'),(86,'stats','recentindexedissue'),(164,'stddata','country'),(165,'stddata','currency'),(166,'stddata','date'),(167,'stddata','language'),(168,'stddata','script'),(180,'taggit','tag'),(181,'taggit','taggeditem'),(179,'templatesadmin','ftemplate'),(154,'voting','agenda'),(155,'voting','agendaitem'),(156,'voting','agendamailinglist'),(157,'voting','expectedvoter'),(158,'voting','mailinglist'),(159,'voting','option'),(160,'voting','receipt'),(161,'voting','topic'),(162,'voting','vote'),(163,'voting','votetype');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=193 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-07-10 06:28:21.081657'),(2,'auth','0001_initial','2026-07-10 06:28:21.621241'),(3,'admin','0001_initial','2026-07-10 06:28:21.752108'),(4,'admin','0002_logentry_remove_auto_add','2026-07-10 06:28:21.760757'),(5,'admin','0003_logentry_add_action_flag_choices','2026-07-10 06:28:21.768761'),(6,'contenttypes','0002_remove_content_type_name','2026-07-10 06:28:21.854944'),(7,'auth','0002_alter_permission_name_max_length','2026-07-10 06:28:21.914791'),(8,'auth','0003_alter_user_email_max_length','2026-07-10 06:28:21.934562'),(9,'auth','0004_alter_user_username_opts','2026-07-10 06:28:21.942509'),(10,'auth','0005_alter_user_last_login_null','2026-07-10 06:28:21.989387'),(11,'auth','0006_require_contenttypes_0002','2026-07-10 06:28:21.992247'),(12,'auth','0007_alter_validators_add_error_messages','2026-07-10 06:28:22.001746'),(13,'auth','0008_alter_user_username_max_length','2026-07-10 06:28:22.060992'),(14,'auth','0009_alter_user_last_name_max_length','2026-07-10 06:28:22.116810'),(15,'auth','0010_alter_group_name_max_length','2026-07-10 06:28:22.134636'),(16,'auth','0011_update_proxy_permissions','2026-07-10 06:28:22.143794'),(17,'auth','0012_alter_user_first_name_max_length','2026-07-10 06:28:22.200909'),(18,'stddata','0001_initial','2026-07-10 06:28:22.365407'),(19,'stddata','0003_language_native_name','2026-07-10 06:28:22.412186'),(20,'stddata','0002_initial_data','2026-07-10 06:28:22.772799'),(21,'stddata','0003_script','2026-07-10 06:28:22.797126'),(22,'taggit','0001_initial','2026-07-10 06:28:22.957790'),(23,'taggit','0002_auto_20150616_2121','2026-07-10 06:28:22.981037'),(24,'gcd','0001_initial','2026-07-10 06:28:28.268327'),(25,'oi','0001_initial','2026-07-10 06:28:36.439043'),(26,'oi','0002_revision_lock','2026-07-10 06:28:36.731076'),(27,'sites','0001_initial','2026-07-10 06:28:36.751235'),(28,'gcd','0002_initial_data','2026-07-10 06:28:36.946575'),(29,'oi','0003_migrate_reservations_to_locks','2026-07-10 06:28:37.050598'),(30,'gcd','0003_creators','2026-07-10 06:28:42.675907'),(31,'oi','0004_creators','2026-07-10 06:28:47.744817'),(32,'oi','0005_issuerevision_volume_not_printed','2026-07-10 06:28:47.894548'),(33,'gcd','0004_initial_creator_data','2026-07-10 06:28:48.437568'),(34,'gcd','0005_issue_volume_not_printed','2026-07-10 06:28:48.673313'),(35,'gcd','0006_award_editable','2026-07-10 06:28:48.923784'),(36,'oi','0006_award_editable','2026-07-10 06:28:49.229244'),(37,'oi','0006_previous_revision_for_all','2026-07-10 06:28:57.071956'),(38,'gcd','0006_add_GcdData_and_model_cleanup','2026-07-10 06:29:01.795894'),(39,'oi','0007_populate_previous_revision','2026-07-10 06:29:01.992625'),(40,'oi','0008_populate_previous_revision_story','2026-07-10 06:29:02.095453'),(41,'oi','0009_storyrevision_first_line','2026-07-10 06:29:02.280584'),(42,'oi','0010_remove_creatorrevision_data_source','2026-07-10 06:29:02.453266'),(43,'gcd','0007_story_first_line','2026-07-10 06:29:02.600251'),(44,'gcd','0008_move_first_line_from_title','2026-07-10 06:29:02.735030'),(45,'gcd','0009_cleanup_creator','2026-07-10 06:29:02.968838'),(46,'gcd','0010_brand_use_gcdlink','2026-07-10 06:29:03.553885'),(47,'oi','0011_reorg_creatornamedetailrevision','2026-07-10 06:29:04.245399'),(48,'gcd','0011_add_sort_name_to_creatornamedetail','2026-07-10 06:29:04.734739'),(49,'oi','0012_use_creator_and_sort_name_in_creatornamedetailrevision','2026-07-10 06:29:05.319173'),(50,'gcd','0012_add_bibliography','2026-07-10 06:29:05.647511'),(51,'oi','0013_add_bibliography','2026-07-10 06:29:05.968783'),(52,'gcd','0013_receivedaward','2026-07-10 06:29:06.347007'),(53,'oi','0014_receivedawardrevision','2026-07-10 06:29:06.843525'),(54,'gcd','0015_cleanup_award_migration','2026-07-10 06:29:07.331499'),(55,'oi','0016_cleanup_award_migration','2026-07-10 06:29:08.276301'),(56,'gcd','0016_delete_creatoraward','2026-07-10 06:29:08.292473'),(57,'gcd','0017_feature','2026-07-10 06:29:08.957581'),(58,'oi','0017_feature','2026-07-10 06:29:09.999790'),(59,'gcd','0018_add_feature_relation','2026-07-10 06:29:10.534603'),(60,'oi','0018_add_feature_relation','2026-07-10 06:29:11.108892'),(61,'gcd','0019_creator_story_credit','2026-07-10 06:29:11.518814'),(62,'oi','0019_creator_story_credit','2026-07-10 06:29:12.246024'),(63,'oi','0020_add_name_language','2026-07-10 06:29:12.743443'),(64,'oi','0021_given_family_name','2026-07-10 06:29:13.456439'),(65,'gcd','0020_add_name_language','2026-07-10 06:29:13.969517'),(66,'gcd','0021_given_family_name','2026-07-10 06:29:14.299953'),(67,'gcd','0022_relation_creator_name','2026-07-10 06:29:14.573127'),(68,'oi','0022_relation_creator_name','2026-07-10 06:29:14.826704'),(69,'oi','0023_migrate_gcd_official_name','2026-07-10 06:29:14.938715'),(70,'gcd','0023_migrate_gcd_official_name','2026-07-10 06:29:15.066234'),(71,'gcd','0024_use_feature_in_story','2026-07-10 06:29:15.641950'),(72,'oi','0024_use_feature_in_story','2026-07-10 06:29:16.148100'),(73,'gcd','0025_name_type_description','2026-07-10 06:29:16.252008'),(74,'gcd','0026_creator_issue_credit','2026-07-10 06:29:17.263156'),(75,'oi','0025_creator_issue_credit','2026-07-10 06:29:18.174495'),(76,'oi','0026_add_publisher_second_date','2026-07-10 06:29:20.917147'),(77,'gcd','0027_add_publisher_second_date','2026-07-10 06:29:23.326733'),(78,'gcd','0028_add_printer','2026-07-10 06:29:24.141718'),(79,'oi','0027_add_printer','2026-07-10 06:29:25.204189'),(80,'gcd','0029_creatorsignature','2026-07-10 06:29:25.558538'),(81,'oi','0028_creatorsignaturerevision','2026-07-10 06:29:26.047770'),(82,'gcd','0030_indicia_printer_per_issue','2026-07-10 06:29:27.109135'),(83,'oi','0029_indicia_printer_per_issue','2026-07-10 06:29:27.868094'),(84,'gcd','0031_storycredit_signature','2026-07-10 06:29:28.089325'),(85,'oi','0030_storycreditrevision_signature','2026-07-10 06:29:28.352676'),(86,'oi','0031_housekeeping','2026-07-10 06:29:28.658256'),(87,'gcd','0032_housekeeping','2026-07-10 06:29:28.815508'),(88,'gcd','0033_add_characters','2026-07-10 06:29:31.008468'),(89,'oi','0032_add_characters','2026-07-10 06:29:34.429241'),(90,'gcd','0034_publisher_code_number','2026-07-10 06:29:34.817983'),(91,'oi','0033_publisher_code_number','2026-07-10 06:29:35.425286'),(92,'oi','0034_series_has_publisher_code_number','2026-07-10 06:29:36.578853'),(93,'oi','0035_creator_disambiguation','2026-07-10 06:29:36.793278'),(94,'oi','0036_generic_feature_brand_emblem','2026-07-10 06:29:37.308328'),(95,'gcd','0035_series_has_publisher_code_number','2026-07-10 06:29:37.640489'),(96,'gcd','0036_creator_disambiguation','2026-07-10 06:29:37.887183'),(97,'gcd','0037_generic_feature_brand_emblem','2026-07-10 06:29:38.129286'),(98,'gcd','0038_character_appearance','2026-07-10 06:29:38.803627'),(99,'oi','0037_character_appearance','2026-07-10 06:29:39.679098'),(100,'oi','0038_sourced_credits','2026-07-10 06:29:40.799526'),(101,'gcd','0039_sourced_credits','2026-07-10 06:29:41.308447'),(102,'gcd','0040_expand_reprint_table','2026-07-10 06:29:42.770464'),(103,'gcd','0041_consolidate_reprints','2026-07-10 06:29:42.773877'),(104,'oi','0039_one_reprint_data_table','2026-07-10 06:29:45.200523'),(105,'gcd','0042_delete_other_reprint_tables','2026-07-10 06:29:47.299717'),(106,'gcd','0043_external_link','2026-07-10 06:29:48.937276'),(107,'gcd','0044_universe','2026-07-10 06:29:49.046902'),(108,'gcd','0045_alter_externallink_options','2026-07-10 06:29:49.068093'),(109,'gcd','0046_issue_variant_cover_status','2026-07-10 06:29:49.407324'),(110,'gcd','0047_feature_disambiguation','2026-07-10 06:29:49.687277'),(111,'gcd','0048_universe_story','2026-07-10 06:29:50.202485'),(112,'gcd','0049_character_universe','2026-07-10 06:29:50.463708'),(113,'gcd','0050_storygroup','2026-07-10 06:29:50.790561'),(114,'gcd','0051_add_multiverse','2026-07-10 06:29:51.831308'),(115,'gcd','0052_add_universe_for_group','2026-07-10 06:29:52.933670'),(116,'gcd','0053_group_name','2026-07-10 06:29:53.628722'),(117,'gcd','0054_use_group_name_in_sequence','2026-07-10 06:29:54.191418'),(118,'gcd','0055_switch_group_null','2026-07-10 06:29:55.234604'),(119,'gcd','0056_alter_storygroup_options','2026-07-10 06:29:55.282657'),(120,'gcd','0057_external_link_feature','2026-07-10 06:29:55.640640'),(121,'gcd','0058_publisher_external_link','2026-07-10 06:29:55.966886'),(122,'gcd','0059_series_external_link','2026-07-10 06:29:56.347810'),(123,'gcd','0060_remove_storygroup_group','2026-07-10 06:29:56.585126'),(124,'gcd','0061_rename_year_created_feature_year_first_published_and_more','2026-07-10 06:29:57.055658'),(125,'gcd','0062_add_story_arc','2026-07-10 06:29:58.081038'),(126,'gcd','0063_add_year_to_story_arc','2026-07-10 06:29:58.263724'),(127,'gcd','0064_add_story_arc_relation','2026-07-10 06:29:58.680361'),(128,'gcd','0065_brand_emblem_m2m','2026-07-10 06:29:59.174056'),(129,'gcd','0066_indicia_printer_not_printed','2026-07-10 06:29:59.662836'),(130,'gcd','0067_add_character_order','2026-07-10 06:30:00.559953'),(131,'gcd','0068_alter_issue_is_indexed','2026-07-10 06:30:00.654862'),(132,'gcd','0069_remove_issue_brand_state','2026-07-10 06:30:00.934694'),(133,'gcd','0070_alter_issue_series_alter_series_publisher_and_more','2026-07-10 06:30:01.950346'),(134,'gcd','0071_alter_cover_options_alter_issue_options','2026-07-10 06:30:02.055886'),(135,'indexer','0001_initial','2026-07-10 06:30:03.068101'),(136,'indexer','0002_indexer_seen_privacy_policy','2026-07-10 06:30:03.239964'),(137,'indexer','0003_contacting_for_pr','2026-07-10 06:30:03.300650'),(138,'indexer','0004_indexer_no_show_sequences','2026-07-10 06:30:03.614370'),(139,'indexer','0005_indexer_cover_letterer_creator_only','2026-07-10 06:30:03.834123'),(140,'indexer','0006_indexer_use_tabs','2026-07-10 06:30:04.021095'),(141,'indexer','0007_summary_thresholds','2026-07-10 06:30:04.368669'),(142,'indexer','0008_indexer_cache_size','2026-07-10 06:30:04.548857'),(143,'indexer','0009_indexer_items_per_page','2026-07-10 06:30:04.713685'),(144,'legacy','0001_initial','2026-07-10 06:30:06.086527'),(145,'mycomics','0001_initial','2026-07-10 06:30:13.083003'),(146,'mycomics','0002_initial_data','2026-07-10 06:30:13.445091'),(147,'mycomics','0003_add_digital','2026-07-10 06:30:14.001124'),(148,'mycomics','0004_housekeeping','2026-07-10 06:30:14.082873'),(149,'mycomics','0005_typo','2026-07-10 06:30:14.265045'),(150,'mycomics','0006_NullBooleanField_is_deprecated','2026-07-10 06:30:14.934365'),(151,'mycomics','0007_collection_for_sale_default','2026-07-10 06:30:15.032193'),(152,'mycomics','0008_collection_location_defaults','2026-07-10 06:30:15.535076'),(153,'mycomics','0009_reading_order','2026-07-10 06:30:16.206833'),(154,'mycomics','0010_alter_readingorder_options','2026-07-10 06:30:16.223964'),(155,'mycomics','0011_alter_readingorder_public','2026-07-10 06:30:16.243983'),(156,'oi','0040_external_link','2026-07-10 06:30:16.969278'),(157,'oi','0041_universe','2026-07-10 06:30:17.516889'),(158,'oi','0042_NullBooleanField_is_deprecated','2026-07-10 06:30:22.943698'),(159,'oi','0043_issuerevision_variant_cover_status','2026-07-10 06:30:23.197567'),(160,'oi','0044_feature_disambiguation','2026-07-10 06:30:23.499909'),(161,'oi','0045_minor_variant_cover_status','2026-07-10 06:30:23.909748'),(162,'oi','0046_universe_story','2026-07-10 06:30:24.849078'),(163,'oi','0047_characterrevision_universe','2026-07-10 06:30:25.820214'),(164,'oi','0048_storygrouprevision','2026-07-10 06:30:26.529512'),(165,'oi','0049_add_multiverse','2026-07-10 06:30:26.870633'),(166,'oi','0050_add_universe_for_group','2026-07-10 06:30:28.203009'),(167,'oi','0051_group_name','2026-07-10 06:30:28.960110'),(168,'oi','0052_use_group_name_in_sequence','2026-07-10 06:30:30.181012'),(169,'oi','0053_alter_related_names_from_changeset','2026-07-10 06:30:41.853921'),(170,'oi','0054_featurelogorevision_image_revision','2026-07-10 06:30:42.147473'),(171,'oi','0055_brandrevision_image_revision','2026-07-10 06:30:42.414841'),(172,'oi','0056_rename_year_created_featurerevision_year_first_published_and_more','2026-07-10 06:30:42.653584'),(173,'oi','0057_add_story_arc','2026-07-10 06:30:44.063818'),(174,'oi','0058_add_year_to_story_arc','2026-07-10 06:30:44.483874'),(175,'oi','0059_add_story_arc_relation','2026-07-10 06:30:45.204397'),(176,'oi','0060_brand_emblem_m2m','2026-07-10 06:30:45.722155'),(177,'oi','0061_indicia_printer_not_printed','2026-07-10 06:30:46.093816'),(178,'oi','0062_add_character_order','2026-07-10 06:30:47.809428'),(179,'oi','0063_alter_changeset_state_change_type','2026-07-10 06:30:48.006144'),(180,'oi','0064_remove_issuerevision_brand_state','2026-07-10 06:30:48.242353'),(181,'sessions','0001_initial','2026-07-10 06:30:48.346678'),(182,'sites','0002_alter_domain_unique','2026-07-10 06:30:48.385158'),(183,'stats','0001_initial','2026-07-10 06:30:49.516847'),(184,'taggit','0003_taggeditem_add_unique_index','2026-07-10 06:30:49.603750'),(185,'taggit','0004_alter_taggeditem_content_type_alter_taggeditem_tag','2026-07-10 06:30:50.170791'),(186,'taggit','0005_auto_20220424_2025','2026-07-10 06:30:50.393588'),(187,'taggit','0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx','2026-07-10 06:30:50.503772'),(188,'voting','0001_initial','2026-07-10 06:30:56.581315'),(189,'voting','0002_initial_data','2026-07-10 06:30:56.796727'),(190,'voting','0003_length_email_field','2026-07-10 06:30:56.817108'),(191,'voting','0004_housekeeping','2026-07-10 06:30:57.195753'),(192,'voting','0005_NullBooleanField_is_deprecated','2026-07-10 06:30:57.603525');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_site` (
  `id` int NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'localhost:8000','Grand Comics Database [test site]');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_award`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_award` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_award_deleted_579efb71` (`deleted`),
  KEY `gcd_award_modified_aad5aa08` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_award` WRITE;
/*!40000 ALTER TABLE `gcd_award` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_award` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_biblio_entry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_biblio_entry` (
  `story_ptr_id` int NOT NULL,
  `page_began` int DEFAULT NULL,
  `page_ended` int DEFAULT NULL,
  `abstract` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `doi` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`story_ptr_id`),
  CONSTRAINT `gcd_biblio_entry_story_ptr_id_d8f3d929_fk_gcd_story_id` FOREIGN KEY (`story_ptr_id`) REFERENCES `gcd_story` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_biblio_entry` WRITE;
/*!40000 ALTER TABLE `gcd_biblio_entry` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_biblio_entry` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_brand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_brand` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `issue_count` int NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  `generic` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_brand_name_001b6c69` (`name`),
  KEY `gcd_brand_year_began_3289ffce` (`year_began`),
  KEY `gcd_brand_year_began_uncertain_6d7d5d79` (`year_began_uncertain`),
  KEY `gcd_brand_year_ended_uncertain_f5866468` (`year_ended_uncertain`),
  KEY `gcd_brand_deleted_7e6dd18f` (`deleted`),
  KEY `gcd_brand_modified_261ed9bd` (`modified`),
  KEY `gcd_brand_year_overall_began_ddc19cc8` (`year_overall_began`),
  KEY `gcd_brand_year_overall_began_uncertain_31ef576d` (`year_overall_began_uncertain`),
  KEY `gcd_brand_year_overall_ended_uncertain_e0e3902a` (`year_overall_ended_uncertain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_brand` WRITE;
/*!40000 ALTER TABLE `gcd_brand` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_brand` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_brand_emblem_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_brand_emblem_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `brand_id` int NOT NULL,
  `brandgroup_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_brand_emblem_group_brand_id_brandgroup_id_a1a2b7a1_uniq` (`brand_id`,`brandgroup_id`),
  KEY `gcd_brand_emblem_gro_brandgroup_id_b74db487_fk_gcd_brand` (`brandgroup_id`),
  CONSTRAINT `gcd_brand_emblem_gro_brandgroup_id_b74db487_fk_gcd_brand` FOREIGN KEY (`brandgroup_id`) REFERENCES `gcd_brand_group` (`id`),
  CONSTRAINT `gcd_brand_emblem_group_brand_id_fbf909be_fk_gcd_brand_id` FOREIGN KEY (`brand_id`) REFERENCES `gcd_brand` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_brand_emblem_group` WRITE;
/*!40000 ALTER TABLE `gcd_brand_emblem_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_brand_emblem_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_brand_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_brand_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `issue_count` int NOT NULL,
  `parent_id` int NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_brand_group_parent_id_97236a04_fk_gcd_publisher_id` (`parent_id`),
  KEY `gcd_brand_group_name_bae378a7` (`name`),
  KEY `gcd_brand_group_year_began_8ae62b5d` (`year_began`),
  KEY `gcd_brand_group_year_began_uncertain_5b9e998f` (`year_began_uncertain`),
  KEY `gcd_brand_group_year_ended_uncertain_5d2ea479` (`year_ended_uncertain`),
  KEY `gcd_brand_group_deleted_45ea9773` (`deleted`),
  KEY `gcd_brand_group_modified_bd8e7033` (`modified`),
  KEY `gcd_brand_group_year_overall_began_146c13e6` (`year_overall_began`),
  KEY `gcd_brand_group_year_overall_began_uncertain_04003dcc` (`year_overall_began_uncertain`),
  KEY `gcd_brand_group_year_overall_ended_uncertain_099d9624` (`year_overall_ended_uncertain`),
  CONSTRAINT `gcd_brand_group_parent_id_97236a04_fk_gcd_publisher_id` FOREIGN KEY (`parent_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_brand_group` WRITE;
/*!40000 ALTER TABLE `gcd_brand_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_brand_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_brand_use`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_brand_use` (
  `id` int NOT NULL AUTO_INCREMENT,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `emblem_id` int NOT NULL,
  `publisher_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_brand_use_publisher_id_aa08dbf8_fk_gcd_publisher_id` (`publisher_id`),
  KEY `gcd_brand_use_emblem_id_62d42813_fk_gcd_brand_id` (`emblem_id`),
  KEY `gcd_brand_use_year_began_e48f857e` (`year_began`),
  KEY `gcd_brand_use_year_began_uncertain_0aec990a` (`year_began_uncertain`),
  KEY `gcd_brand_use_year_ended_uncertain_48244aec` (`year_ended_uncertain`),
  KEY `gcd_brand_use_modified_2f953692` (`modified`),
  CONSTRAINT `gcd_brand_use_emblem_id_62d42813_fk_gcd_brand_id` FOREIGN KEY (`emblem_id`) REFERENCES `gcd_brand` (`id`),
  CONSTRAINT `gcd_brand_use_publisher_id_aa08dbf8_fk_gcd_publisher_id` FOREIGN KEY (`publisher_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_brand_use` WRITE;
/*!40000 ALTER TABLE `gcd_brand_use` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_brand_use` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `language_id` int NOT NULL,
  `universe_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_character_language_id_a766f96d_fk_stddata_language_id` (`language_id`),
  KEY `gcd_character_modified_0364bb9a` (`modified`),
  KEY `gcd_character_deleted_cf8504b7` (`deleted`),
  KEY `gcd_character_name_018c558c` (`name`),
  KEY `gcd_character_sort_name_b009e2bf` (`sort_name`),
  KEY `gcd_character_disambiguation_6a99e15f` (`disambiguation`),
  KEY `gcd_character_year_first_published_381260d2` (`year_first_published`),
  KEY `gcd_character_universe_id_1058453c_fk_gcd_universe_id` (`universe_id`),
  CONSTRAINT `gcd_character_language_id_a766f96d_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `gcd_character_universe_id_1058453c_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character` WRITE;
/*!40000 ALTER TABLE `gcd_character` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `character_id` int NOT NULL,
  `externallink_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_character_external_l_character_id_externallin_51a5789c_uniq` (`character_id`,`externallink_id`),
  KEY `gcd_character_extern_externallink_id_4bcf7c82_fk_gcd_exter` (`externallink_id`),
  CONSTRAINT `gcd_character_extern_character_id_1c1e27a7_fk_gcd_chara` FOREIGN KEY (`character_id`) REFERENCES `gcd_character` (`id`),
  CONSTRAINT `gcd_character_extern_externallink_id_4bcf7c82_fk_gcd_exter` FOREIGN KEY (`externallink_id`) REFERENCES `gcd_external_link` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_external_link` WRITE;
/*!40000 ALTER TABLE `gcd_character_external_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_external_link` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_name_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_name_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `character_id` int NOT NULL,
  `is_official_name` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_character_name_d_character_id_a0aa1b65_fk_gcd_chara` (`character_id`),
  KEY `gcd_character_name_detail_modified_d02579b5` (`modified`),
  KEY `gcd_character_name_detail_deleted_cc14821d` (`deleted`),
  KEY `gcd_character_name_detail_name_fb316b3f` (`name`),
  KEY `gcd_character_name_detail_sort_name_c86acd29` (`sort_name`),
  CONSTRAINT `gcd_character_name_d_character_id_a0aa1b65_fk_gcd_chara` FOREIGN KEY (`character_id`) REFERENCES `gcd_character` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_name_detail` WRITE;
/*!40000 ALTER TABLE `gcd_character_name_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_name_detail` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `story_id` int NOT NULL,
  `type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_character_order_story_id_9140b08d_fk_gcd_story_id` (`story_id`),
  KEY `gcd_character_order_type_id_5f79445a_fk_gcd_chara` (`type_id`),
  KEY `gcd_character_order_modified_540ba853` (`modified`),
  CONSTRAINT `gcd_character_order_story_id_9140b08d_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `gcd_character_order_type_id_5f79445a_fk_gcd_chara` FOREIGN KEY (`type_id`) REFERENCES `gcd_character_order_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_order` WRITE;
/*!40000 ALTER TABLE `gcd_character_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_order` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_order_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_order_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_order_type` WRITE;
/*!40000 ALTER TABLE `gcd_character_order_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_order_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_relation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_character_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `to_character_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_character_relati_from_character_id_f632780f_fk_gcd_chara` (`from_character_id`),
  KEY `gcd_character_relati_relation_type_id_4cfe6f07_fk_gcd_chara` (`relation_type_id`),
  KEY `gcd_character_relati_to_character_id_e08d735a_fk_gcd_chara` (`to_character_id`),
  KEY `gcd_character_relation_modified_ac98c3e4` (`modified`),
  CONSTRAINT `gcd_character_relati_from_character_id_f632780f_fk_gcd_chara` FOREIGN KEY (`from_character_id`) REFERENCES `gcd_character` (`id`),
  CONSTRAINT `gcd_character_relati_relation_type_id_4cfe6f07_fk_gcd_chara` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_character_relation_type` (`id`),
  CONSTRAINT `gcd_character_relati_to_character_id_e08d735a_fk_gcd_chara` FOREIGN KEY (`to_character_id`) REFERENCES `gcd_character` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_relation` WRITE;
/*!40000 ALTER TABLE `gcd_character_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_relation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_relation_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_relation_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reverse_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_relation_type` WRITE;
/*!40000 ALTER TABLE `gcd_character_relation_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_relation_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_code` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `sort_code` (`sort_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_role` WRITE;
/*!40000 ALTER TABLE `gcd_character_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_role` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_character_through_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_character_through_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_code` int NOT NULL,
  `order_id` int NOT NULL,
  `story_character_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_character_throug_order_id_4f90896e_fk_gcd_chara` (`order_id`),
  KEY `gcd_character_throug_story_character_id_8e21273e_fk_gcd_story` (`story_character_id`),
  KEY `gcd_character_through_order_order_code_36778a6f` (`order_code`),
  CONSTRAINT `gcd_character_throug_order_id_4f90896e_fk_gcd_chara` FOREIGN KEY (`order_id`) REFERENCES `gcd_character_order` (`id`),
  CONSTRAINT `gcd_character_throug_story_character_id_8e21273e_fk_gcd_story` FOREIGN KEY (`story_character_id`) REFERENCES `gcd_story_character` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_character_through_order` WRITE;
/*!40000 ALTER TABLE `gcd_character_through_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_character_through_order` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_code_number_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_code_number_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_code_number_type` WRITE;
/*!40000 ALTER TABLE `gcd_code_number_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_code_number_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_cover`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_cover` (
  `id` int NOT NULL AUTO_INCREMENT,
  `marked` tinyint(1) NOT NULL,
  `limit_display` tinyint(1) NOT NULL,
  `is_wraparound` tinyint(1) NOT NULL,
  `front_left` int DEFAULT NULL,
  `front_right` int DEFAULT NULL,
  `front_bottom` int DEFAULT NULL,
  `front_top` int DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `last_upload` datetime(6) DEFAULT NULL,
  `reserved` tinyint(1) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `issue_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_cover_issue_id_c3f6a1ea_fk_gcd_issue_id` (`issue_id`),
  KEY `gcd_cover_modified_9ff98104` (`modified`),
  KEY `gcd_cover_last_upload_a0770ce8` (`last_upload`),
  KEY `gcd_cover_reserved_98b31a14` (`reserved`),
  KEY `gcd_cover_deleted_d8c23cae` (`deleted`),
  CONSTRAINT `gcd_cover_issue_id_c3f6a1ea_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_cover` WRITE;
/*!40000 ALTER TABLE `gcd_cover` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_cover` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gcd_official_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `whos_who` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birth_country_uncertain` tinyint(1) NOT NULL,
  `birth_province` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_province_uncertain` tinyint(1) NOT NULL,
  `birth_city` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_city_uncertain` tinyint(1) NOT NULL,
  `death_country_uncertain` tinyint(1) NOT NULL,
  `death_province` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `death_province_uncertain` tinyint(1) NOT NULL,
  `death_city` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `death_city_uncertain` tinyint(1) NOT NULL,
  `bio` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `birth_country_id` int DEFAULT NULL,
  `birth_date_id` int DEFAULT NULL,
  `death_country_id` int DEFAULT NULL,
  `death_date_id` int DEFAULT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_death_country_id_7b61a9d4_fk_stddata_country_id` (`death_country_id`),
  KEY `gcd_creator_death_date_id_f95cb653_fk_stddata_date_id` (`death_date_id`),
  KEY `gcd_creator_birth_country_id_d8dd90b4_fk_stddata_country_id` (`birth_country_id`),
  KEY `gcd_creator_birth_date_id_b87a721e_fk_stddata_date_id` (`birth_date_id`),
  KEY `gcd_creator_gcd_official_name_f03b4c93` (`gcd_official_name`),
  KEY `gcd_creator_deleted_14d3a3f2` (`deleted`),
  KEY `gcd_creator_modified_be9618df` (`modified`),
  KEY `gcd_creator_sort_name_80a1e4ff` (`sort_name`),
  KEY `gcd_creator_disambiguation_21a5e71c` (`disambiguation`),
  CONSTRAINT `gcd_creator_birth_country_id_d8dd90b4_fk_stddata_country_id` FOREIGN KEY (`birth_country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `gcd_creator_birth_date_id_b87a721e_fk_stddata_date_id` FOREIGN KEY (`birth_date_id`) REFERENCES `stddata_date` (`id`),
  CONSTRAINT `gcd_creator_death_country_id_7b61a9d4_fk_stddata_country_id` FOREIGN KEY (`death_country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `gcd_creator_death_date_id_f95cb653_fk_stddata_date_id` FOREIGN KEY (`death_date_id`) REFERENCES `stddata_date` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator` WRITE;
/*!40000 ALTER TABLE `gcd_creator` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_art_influence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_art_influence` (
  `id` int NOT NULL AUTO_INCREMENT,
  `influence_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `creator_id` int NOT NULL,
  `influence_link_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_art_infl_influence_link_id_7ffc0a72_fk_gcd_creat` (`influence_link_id`),
  KEY `gcd_creator_art_influence_creator_id_af97901f_fk_gcd_creator_id` (`creator_id`),
  KEY `gcd_creator_art_influence_deleted_b1ff3128` (`deleted`),
  KEY `gcd_creator_art_influence_modified_6b2257ba` (`modified`),
  CONSTRAINT `gcd_creator_art_infl_influence_link_id_7ffc0a72_fk_gcd_creat` FOREIGN KEY (`influence_link_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `gcd_creator_art_influence_creator_id_af97901f_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_art_influence` WRITE;
/*!40000 ALTER TABLE `gcd_creator_art_influence` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_art_influence` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_art_influence_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_art_influence_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatorartinfluence_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_art_influenc_creatorartinfluence_id_d_3b7d4e29_uniq` (`creatorartinfluence_id`,`datasource_id`),
  KEY `gcd_creator_art_infl_datasource_id_f4bd1b04_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_art_infl_creatorartinfluence__0422e238_fk_gcd_creat` FOREIGN KEY (`creatorartinfluence_id`) REFERENCES `gcd_creator_art_influence` (`id`),
  CONSTRAINT `gcd_creator_art_infl_datasource_id_f4bd1b04_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_art_influence_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_art_influence_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_art_influence_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creator_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_data_source_creator_id_datasource_id_251ef686_uniq` (`creator_id`,`datasource_id`),
  KEY `gcd_creator_data_sou_datasource_id_cb47db66_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_data_sou_datasource_id_cb47db66_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`),
  CONSTRAINT `gcd_creator_data_source_creator_id_7719730c_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_degree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_degree` (
  `id` int NOT NULL AUTO_INCREMENT,
  `degree_year` smallint unsigned DEFAULT NULL,
  `degree_year_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `creator_id` int NOT NULL,
  `degree_id` int NOT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_degree_degree_id_fd2e2492_fk_gcd_degree_id` (`degree_id`),
  KEY `gcd_creator_degree_school_id_d476df8a_fk_gcd_school_id` (`school_id`),
  KEY `gcd_creator_degree_creator_id_e5ecb8cc_fk_gcd_creator_id` (`creator_id`),
  KEY `gcd_creator_degree_deleted_4f487cd9` (`deleted`),
  KEY `gcd_creator_degree_modified_118ff74c` (`modified`),
  CONSTRAINT `gcd_creator_degree_creator_id_e5ecb8cc_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `gcd_creator_degree_degree_id_fd2e2492_fk_gcd_degree_id` FOREIGN KEY (`degree_id`) REFERENCES `gcd_degree` (`id`),
  CONSTRAINT `gcd_creator_degree_school_id_d476df8a_fk_gcd_school_id` FOREIGN KEY (`school_id`) REFERENCES `gcd_school` (`id`),
  CONSTRAINT `gcd_creator_degree_chk_1` CHECK ((`degree_year` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_degree` WRITE;
/*!40000 ALTER TABLE `gcd_creator_degree` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_degree` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_degree_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_degree_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatordegree_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_degree_data__creatordegree_id_datasou_9fdd65b7_uniq` (`creatordegree_id`,`datasource_id`),
  KEY `gcd_creator_degree_d_datasource_id_4f0f92b1_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_degree_d_creatordegree_id_385f0872_fk_gcd_creat` FOREIGN KEY (`creatordegree_id`) REFERENCES `gcd_creator_degree` (`id`),
  CONSTRAINT `gcd_creator_degree_d_datasource_id_4f0f92b1_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_degree_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_degree_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_degree_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creator_id` int NOT NULL,
  `externallink_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_external_lin_creator_id_externallink__783fb759_uniq` (`creator_id`,`externallink_id`),
  KEY `gcd_creator_external_externallink_id_2bcc54c0_fk_gcd_exter` (`externallink_id`),
  CONSTRAINT `gcd_creator_external_externallink_id_2bcc54c0_fk_gcd_exter` FOREIGN KEY (`externallink_id`) REFERENCES `gcd_external_link` (`id`),
  CONSTRAINT `gcd_creator_external_link_creator_id_d120f40d_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_external_link` WRITE;
/*!40000 ALTER TABLE `gcd_creator_external_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_external_link` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_membership` (
  `id` int NOT NULL AUTO_INCREMENT,
  `organization_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `membership_year_began` smallint unsigned DEFAULT NULL,
  `membership_year_began_uncertain` tinyint(1) NOT NULL,
  `membership_year_ended` smallint unsigned DEFAULT NULL,
  `membership_year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `creator_id` int NOT NULL,
  `membership_type_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_membersh_membership_type_id_c80f80ac_fk_gcd_membe` (`membership_type_id`),
  KEY `gcd_creator_membership_creator_id_a7a0e101_fk_gcd_creator_id` (`creator_id`),
  KEY `gcd_creator_membership_deleted_bff3b942` (`deleted`),
  KEY `gcd_creator_membership_modified_96cb0f38` (`modified`),
  CONSTRAINT `gcd_creator_membersh_membership_type_id_c80f80ac_fk_gcd_membe` FOREIGN KEY (`membership_type_id`) REFERENCES `gcd_membership_type` (`id`),
  CONSTRAINT `gcd_creator_membership_creator_id_a7a0e101_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `gcd_creator_membership_chk_1` CHECK ((`membership_year_began` >= 0)),
  CONSTRAINT `gcd_creator_membership_chk_2` CHECK ((`membership_year_ended` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_membership` WRITE;
/*!40000 ALTER TABLE `gcd_creator_membership` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_membership` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_membership_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_membership_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatormembership_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_membership_d_creatormembership_id_dat_d0e75600_uniq` (`creatormembership_id`,`datasource_id`),
  KEY `gcd_creator_membersh_datasource_id_a685e33c_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_membersh_creatormembership_id_e696b161_fk_gcd_creat` FOREIGN KEY (`creatormembership_id`) REFERENCES `gcd_creator_membership` (`id`),
  CONSTRAINT `gcd_creator_membersh_datasource_id_a685e33c_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_membership_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_membership_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_membership_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_name_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_name_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `creator_id` int NOT NULL,
  `type_id` int DEFAULT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_official_name` tinyint(1) NOT NULL,
  `in_script_id` int NOT NULL,
  `family_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `given_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_name_detail_type_id_cce05647_fk_gcd_name_type_id` (`type_id`),
  KEY `gcd_creator_name_detail_creator_id_7888b806_fk_gcd_creator_id` (`creator_id`),
  KEY `gcd_creator_name_detail_name_77fb8dbd` (`name`),
  KEY `gcd_creator_name_detail_deleted_33827058` (`deleted`),
  KEY `gcd_creator_name_detail_modified_fdfe243a` (`modified`),
  KEY `gcd_creator_name_detail_sort_name_f7d3caa6` (`sort_name`),
  KEY `gcd_creator_name_det_in_script_id_b7560492_fk_stddata_s` (`in_script_id`),
  KEY `gcd_creator_name_detail_family_name_e81f34f4` (`family_name`),
  KEY `gcd_creator_name_detail_given_name_6706c242` (`given_name`),
  CONSTRAINT `gcd_creator_name_det_in_script_id_b7560492_fk_stddata_s` FOREIGN KEY (`in_script_id`) REFERENCES `stddata_script` (`id`),
  CONSTRAINT `gcd_creator_name_detail_creator_id_7888b806_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `gcd_creator_name_detail_type_id_cce05647_fk_gcd_name_type_id` FOREIGN KEY (`type_id`) REFERENCES `gcd_name_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_name_detail` WRITE;
/*!40000 ALTER TABLE `gcd_creator_name_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_name_detail` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_non_comic_work`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_non_comic_work` (
  `id` int NOT NULL AUTO_INCREMENT,
  `publication_title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employer_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `work_title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `work_urls` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `creator_id` int NOT NULL,
  `work_role_id` int DEFAULT NULL,
  `work_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_non_comi_work_role_id_dd0f7022_fk_gcd_non_c` (`work_role_id`),
  KEY `gcd_creator_non_comi_work_type_id_87772f2c_fk_gcd_non_c` (`work_type_id`),
  KEY `gcd_creator_non_comic_work_creator_id_73c2c70c_fk_gcd_creator_id` (`creator_id`),
  KEY `gcd_creator_non_comic_work_deleted_43184e8a` (`deleted`),
  KEY `gcd_creator_non_comic_work_modified_054c60c6` (`modified`),
  CONSTRAINT `gcd_creator_non_comi_work_role_id_dd0f7022_fk_gcd_non_c` FOREIGN KEY (`work_role_id`) REFERENCES `gcd_non_comic_work_role` (`id`),
  CONSTRAINT `gcd_creator_non_comi_work_type_id_87772f2c_fk_gcd_non_c` FOREIGN KEY (`work_type_id`) REFERENCES `gcd_non_comic_work_type` (`id`),
  CONSTRAINT `gcd_creator_non_comic_work_creator_id_73c2c70c_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_non_comic_work` WRITE;
/*!40000 ALTER TABLE `gcd_creator_non_comic_work` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_non_comic_work` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_non_comic_work_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_non_comic_work_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatornoncomicwork_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_non_comic_wo_creatornoncomicwork_id_d_e5e39bf5_uniq` (`creatornoncomicwork_id`,`datasource_id`),
  KEY `gcd_creator_non_comi_datasource_id_f3ccec7a_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_non_comi_creatornoncomicwork__b919b35b_fk_gcd_creat` FOREIGN KEY (`creatornoncomicwork_id`) REFERENCES `gcd_creator_non_comic_work` (`id`),
  CONSTRAINT `gcd_creator_non_comi_datasource_id_f3ccec7a_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_non_comic_work_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_non_comic_work_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_non_comic_work_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_relation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `from_creator_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `to_creator_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_relation_from_creator_id_3d793ded_fk_gcd_creator_id` (`from_creator_id`),
  KEY `gcd_creator_relation_relation_type_id_98aa1020_fk_gcd_relat` (`relation_type_id`),
  KEY `gcd_creator_relation_to_creator_id_d858350c_fk_gcd_creator_id` (`to_creator_id`),
  KEY `gcd_creator_relation_deleted_df5253fd` (`deleted`),
  KEY `gcd_creator_relation_modified_5995b3ff` (`modified`),
  CONSTRAINT `gcd_creator_relation_from_creator_id_3d793ded_fk_gcd_creator_id` FOREIGN KEY (`from_creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `gcd_creator_relation_relation_type_id_98aa1020_fk_gcd_relat` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_relation_type` (`id`),
  CONSTRAINT `gcd_creator_relation_to_creator_id_d858350c_fk_gcd_creator_id` FOREIGN KEY (`to_creator_id`) REFERENCES `gcd_creator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_relation` WRITE;
/*!40000 ALTER TABLE `gcd_creator_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_relation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_relation_creator_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_relation_creator_name` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatorrelation_id` int NOT NULL,
  `creatornamedetail_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_relation_cre_creatorrelation_id_creat_953af27b_uniq` (`creatorrelation_id`,`creatornamedetail_id`),
  KEY `gcd_creator_relation_creatornamedetail_id_4675e7fc_fk_gcd_creat` (`creatornamedetail_id`),
  CONSTRAINT `gcd_creator_relation_creatornamedetail_id_4675e7fc_fk_gcd_creat` FOREIGN KEY (`creatornamedetail_id`) REFERENCES `gcd_creator_name_detail` (`id`),
  CONSTRAINT `gcd_creator_relation_creatorrelation_id_d48c32dc_fk_gcd_creat` FOREIGN KEY (`creatorrelation_id`) REFERENCES `gcd_creator_relation` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_relation_creator_name` WRITE;
/*!40000 ALTER TABLE `gcd_creator_relation_creator_name` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_relation_creator_name` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_relation_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_relation_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatorrelation_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_relation_dat_creatorrelation_id_datas_2e4c7e6a_uniq` (`creatorrelation_id`,`datasource_id`),
  KEY `gcd_creator_relation_datasource_id_08e3a67a_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_relation_creatorrelation_id_579a5662_fk_gcd_creat` FOREIGN KEY (`creatorrelation_id`) REFERENCES `gcd_creator_relation` (`id`),
  CONSTRAINT `gcd_creator_relation_datasource_id_08e3a67a_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_relation_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_relation_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_relation_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_school`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_school` (
  `id` int NOT NULL AUTO_INCREMENT,
  `school_year_began` smallint unsigned DEFAULT NULL,
  `school_year_began_uncertain` tinyint(1) NOT NULL,
  `school_year_ended` smallint unsigned DEFAULT NULL,
  `school_year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `creator_id` int NOT NULL,
  `school_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_school_school_id_cc3bf337_fk_gcd_school_id` (`school_id`),
  KEY `gcd_creator_school_creator_id_04d76c83_fk_gcd_creator_id` (`creator_id`),
  KEY `gcd_creator_school_deleted_4c8499f6` (`deleted`),
  KEY `gcd_creator_school_modified_aaa984cf` (`modified`),
  CONSTRAINT `gcd_creator_school_creator_id_04d76c83_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `gcd_creator_school_school_id_cc3bf337_fk_gcd_school_id` FOREIGN KEY (`school_id`) REFERENCES `gcd_school` (`id`),
  CONSTRAINT `gcd_creator_school_chk_1` CHECK ((`school_year_began` >= 0)),
  CONSTRAINT `gcd_creator_school_chk_2` CHECK ((`school_year_ended` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_school` WRITE;
/*!40000 ALTER TABLE `gcd_creator_school` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_school` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_school_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_school_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatorschool_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_school_data__creatorschool_id_datasou_f3662947_uniq` (`creatorschool_id`,`datasource_id`),
  KEY `gcd_creator_school_d_datasource_id_ee0d546a_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_school_d_creatorschool_id_a7ffaee3_fk_gcd_creat` FOREIGN KEY (`creatorschool_id`) REFERENCES `gcd_creator_school` (`id`),
  CONSTRAINT `gcd_creator_school_d_datasource_id_ee0d546a_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_school_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_school_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_school_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_signature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_signature` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `generic` tinyint(1) NOT NULL,
  `creator_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_creator_signature_creator_id_063b6789_fk_gcd_creator_id` (`creator_id`),
  KEY `gcd_creator_signature_modified_064658ce` (`modified`),
  KEY `gcd_creator_signature_deleted_2e7249b9` (`deleted`),
  KEY `gcd_creator_signature_name_91dfd0cc` (`name`),
  CONSTRAINT `gcd_creator_signature_creator_id_063b6789_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_signature` WRITE;
/*!40000 ALTER TABLE `gcd_creator_signature` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_signature` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_creator_signature_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_creator_signature_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatorsignature_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_creator_signature_da_creatorsignature_id_data_8d610b9f_uniq` (`creatorsignature_id`,`datasource_id`),
  KEY `gcd_creator_signatur_datasource_id_36eac066_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_creator_signatur_creatorsignature_id_731a7b20_fk_gcd_creat` FOREIGN KEY (`creatorsignature_id`) REFERENCES `gcd_creator_signature` (`id`),
  CONSTRAINT `gcd_creator_signatur_datasource_id_36eac066_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_creator_signature_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_creator_signature_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_creator_signature_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_credit_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_credit_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_code` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `sort_code` (`sort_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_credit_type` WRITE;
/*!40000 ALTER TABLE `gcd_credit_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_credit_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `source_description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `field` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `source_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_data_source_source_type_id_374f848c_fk_gcd_source_type_id` (`source_type_id`),
  KEY `gcd_data_source_deleted_1a88a0ca` (`deleted`),
  KEY `gcd_data_source_modified_0e44f3c8` (`modified`),
  CONSTRAINT `gcd_data_source_source_type_id_374f848c_fk_gcd_source_type_id` FOREIGN KEY (`source_type_id`) REFERENCES `gcd_source_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_degree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_degree` (
  `id` int NOT NULL AUTO_INCREMENT,
  `degree_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_degree` WRITE;
/*!40000 ALTER TABLE `gcd_degree` DISABLE KEYS */;
INSERT INTO `gcd_degree` VALUES (1,'B.A'),(2,'B.Com'),(3,'BE'),(4,'Dr'),(5,'M.B.A'),(6,'M.E'),(7,'M.S'),(8,'P.h.d');
/*!40000 ALTER TABLE `gcd_degree` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `link` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `site_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_external_link_site_id_d4171e83_fk_gcd_external_site_id` (`site_id`),
  KEY `gcd_external_link_modified_0058645b` (`modified`),
  CONSTRAINT `gcd_external_link_site_id_d4171e83_fk_gcd_external_site_id` FOREIGN KEY (`site_id`) REFERENCES `gcd_external_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_external_link` WRITE;
/*!40000 ALTER TABLE `gcd_external_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_external_link` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_external_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_external_site` (
  `id` int NOT NULL AUTO_INCREMENT,
  `site` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `matching` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_external_site` WRITE;
/*!40000 ALTER TABLE `gcd_external_site` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_external_site` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_feature` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `genre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `feature_type_id` int NOT NULL,
  `language_id` int NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_feature_feature_type_id_0bd38e4d_fk_gcd_feature_type_id` (`feature_type_id`),
  KEY `gcd_feature_language_id_f6ca9801_fk_stddata_language_id` (`language_id`),
  KEY `gcd_feature_modified_dc767107` (`modified`),
  KEY `gcd_feature_deleted_d2842928` (`deleted`),
  KEY `gcd_feature_name_1b482a02` (`name`),
  KEY `gcd_feature_sort_name_aa22b333` (`sort_name`),
  KEY `gcd_feature_year_created_d3f06615` (`year_first_published`),
  KEY `gcd_feature_disambiguation_fe7ce1a9` (`disambiguation`),
  CONSTRAINT `gcd_feature_feature_type_id_0bd38e4d_fk_gcd_feature_type_id` FOREIGN KEY (`feature_type_id`) REFERENCES `gcd_feature_type` (`id`),
  CONSTRAINT `gcd_feature_language_id_f6ca9801_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_feature` WRITE;
/*!40000 ALTER TABLE `gcd_feature` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_feature` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_feature_external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_feature_external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `feature_id` int NOT NULL,
  `externallink_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_feature_external_lin_feature_id_externallink__a1b2d840_uniq` (`feature_id`,`externallink_id`),
  KEY `gcd_feature_external_externallink_id_c5d553f3_fk_gcd_exter` (`externallink_id`),
  CONSTRAINT `gcd_feature_external_externallink_id_c5d553f3_fk_gcd_exter` FOREIGN KEY (`externallink_id`) REFERENCES `gcd_external_link` (`id`),
  CONSTRAINT `gcd_feature_external_link_feature_id_7bf7db2b_fk_gcd_feature_id` FOREIGN KEY (`feature_id`) REFERENCES `gcd_feature` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_feature_external_link` WRITE;
/*!40000 ALTER TABLE `gcd_feature_external_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_feature_external_link` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_feature_logo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_feature_logo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `generic` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_feature_logo_modified_a01588f8` (`modified`),
  KEY `gcd_feature_logo_deleted_7fc639e5` (`deleted`),
  KEY `gcd_feature_logo_name_fca0238c` (`name`),
  KEY `gcd_feature_logo_sort_name_fc35812c` (`sort_name`),
  KEY `gcd_feature_logo_year_began_e62b6676` (`year_began`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_feature_logo` WRITE;
/*!40000 ALTER TABLE `gcd_feature_logo` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_feature_logo` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_feature_logo_2_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_feature_logo_2_feature` (
  `id` int NOT NULL AUTO_INCREMENT,
  `featurelogo_id` int NOT NULL,
  `feature_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_feature_logo_2_featu_featurelogo_id_feature_i_26489bce_uniq` (`featurelogo_id`,`feature_id`),
  KEY `gcd_feature_logo_2_feature_feature_id_8ec96fc1_fk_gcd_feature_id` (`feature_id`),
  CONSTRAINT `gcd_feature_logo_2_f_featurelogo_id_3e696cd6_fk_gcd_featu` FOREIGN KEY (`featurelogo_id`) REFERENCES `gcd_feature_logo` (`id`),
  CONSTRAINT `gcd_feature_logo_2_feature_feature_id_8ec96fc1_fk_gcd_feature_id` FOREIGN KEY (`feature_id`) REFERENCES `gcd_feature` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_feature_logo_2_feature` WRITE;
/*!40000 ALTER TABLE `gcd_feature_logo_2_feature` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_feature_logo_2_feature` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_feature_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_feature_relation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_feature_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `to_feature_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_feature_relation_relation_type_id_09ba4ac7_fk_gcd_featu` (`relation_type_id`),
  KEY `gcd_feature_relation_to_feature_id_e5a20bdf_fk_gcd_feature_id` (`to_feature_id`),
  KEY `gcd_feature_relation_from_feature_id_25e36fdf_fk_gcd_feature_id` (`from_feature_id`),
  KEY `gcd_feature_relation_modified_896fb6c6` (`modified`),
  CONSTRAINT `gcd_feature_relation_from_feature_id_25e36fdf_fk_gcd_feature_id` FOREIGN KEY (`from_feature_id`) REFERENCES `gcd_feature` (`id`),
  CONSTRAINT `gcd_feature_relation_relation_type_id_09ba4ac7_fk_gcd_featu` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_feature_relation_type` (`id`),
  CONSTRAINT `gcd_feature_relation_to_feature_id_e5a20bdf_fk_gcd_feature_id` FOREIGN KEY (`to_feature_id`) REFERENCES `gcd_feature` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_feature_relation` WRITE;
/*!40000 ALTER TABLE `gcd_feature_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_feature_relation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_feature_relation_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_feature_relation_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reverse_description` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_feature_relation_type_name_5eb55141` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_feature_relation_type` WRITE;
/*!40000 ALTER TABLE `gcd_feature_relation_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_feature_relation_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_feature_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_feature_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_feature_type_name_af6c2592` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_feature_type` WRITE;
/*!40000 ALTER TABLE `gcd_feature_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_feature_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `language_id` int NOT NULL,
  `universe_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_group_language_id_e0935a36_fk_stddata_language_id` (`language_id`),
  KEY `gcd_group_modified_316b6f0c` (`modified`),
  KEY `gcd_group_deleted_eb8063e4` (`deleted`),
  KEY `gcd_group_name_0358904e` (`name`),
  KEY `gcd_group_sort_name_1922a716` (`sort_name`),
  KEY `gcd_group_disambiguation_4e03cb92` (`disambiguation`),
  KEY `gcd_group_year_first_published_65064aae` (`year_first_published`),
  KEY `gcd_group_universe_id_e32b55ff_fk_gcd_universe_id` (`universe_id`),
  CONSTRAINT `gcd_group_language_id_e0935a36_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `gcd_group_universe_id_e32b55ff_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_group` WRITE;
/*!40000 ALTER TABLE `gcd_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_group_character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_group_character` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `story_id` int NOT NULL,
  `universe_id` int DEFAULT NULL,
  `group_name_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_group_character_story_id_4aedac36_fk_gcd_story_id` (`story_id`),
  KEY `gcd_group_character_modified_2e1743fd` (`modified`),
  KEY `gcd_group_character_deleted_da9fb253` (`deleted`),
  KEY `gcd_group_character_universe_id_34fdd9e7_fk_gcd_universe_id` (`universe_id`),
  KEY `gcd_group_character_group_name_id_a01b83b2_fk_gcd_group` (`group_name_id`),
  CONSTRAINT `gcd_group_character_group_name_id_a01b83b2_fk_gcd_group` FOREIGN KEY (`group_name_id`) REFERENCES `gcd_group_name_detail` (`id`),
  CONSTRAINT `gcd_group_character_story_id_4aedac36_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `gcd_group_character_universe_id_34fdd9e7_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_group_character` WRITE;
/*!40000 ALTER TABLE `gcd_group_character` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_group_character` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_group_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_group_membership` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `year_joined` smallint unsigned DEFAULT NULL,
  `year_joined_uncertain` tinyint(1) NOT NULL,
  `year_left` smallint unsigned DEFAULT NULL,
  `year_left_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `character_id` int NOT NULL,
  `group_id` int NOT NULL,
  `membership_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_group_membership_character_id_ce34b6e6_fk_gcd_character_id` (`character_id`),
  KEY `gcd_group_membership_group_id_ee6c8c22_fk_gcd_group_id` (`group_id`),
  KEY `gcd_group_membership_membership_type_id_32854b66_fk_gcd_group` (`membership_type_id`),
  KEY `gcd_group_membership_modified_1b391fa5` (`modified`),
  CONSTRAINT `gcd_group_membership_character_id_ce34b6e6_fk_gcd_character_id` FOREIGN KEY (`character_id`) REFERENCES `gcd_character` (`id`),
  CONSTRAINT `gcd_group_membership_group_id_ee6c8c22_fk_gcd_group_id` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`),
  CONSTRAINT `gcd_group_membership_membership_type_id_32854b66_fk_gcd_group` FOREIGN KEY (`membership_type_id`) REFERENCES `gcd_group_membership_type` (`id`),
  CONSTRAINT `gcd_group_membership_chk_1` CHECK ((`year_joined` >= 0)),
  CONSTRAINT `gcd_group_membership_chk_2` CHECK ((`year_left` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_group_membership` WRITE;
/*!40000 ALTER TABLE `gcd_group_membership` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_group_membership` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_group_membership_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_group_membership_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reverse_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_group_membership_type` WRITE;
/*!40000 ALTER TABLE `gcd_group_membership_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_group_membership_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_group_name_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_group_name_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_official_name` tinyint(1) NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_group_name_detail_group_id_f6a401d7_fk_gcd_group_id` (`group_id`),
  KEY `gcd_group_name_detail_modified_de08b22d` (`modified`),
  KEY `gcd_group_name_detail_deleted_ca292280` (`deleted`),
  KEY `gcd_group_name_detail_name_d1ffc28a` (`name`),
  KEY `gcd_group_name_detail_sort_name_2a643b29` (`sort_name`),
  CONSTRAINT `gcd_group_name_detail_group_id_f6a401d7_fk_gcd_group_id` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_group_name_detail` WRITE;
/*!40000 ALTER TABLE `gcd_group_name_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_group_name_detail` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_group_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_group_relation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_group_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `to_group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_group_relation_from_group_id_e865b8f6_fk_gcd_group_id` (`from_group_id`),
  KEY `gcd_group_relation_relation_type_id_ab30bd40_fk_gcd_group` (`relation_type_id`),
  KEY `gcd_group_relation_to_group_id_454ce47f_fk_gcd_group_id` (`to_group_id`),
  KEY `gcd_group_relation_modified_19f4c52a` (`modified`),
  CONSTRAINT `gcd_group_relation_from_group_id_e865b8f6_fk_gcd_group_id` FOREIGN KEY (`from_group_id`) REFERENCES `gcd_group` (`id`),
  CONSTRAINT `gcd_group_relation_relation_type_id_ab30bd40_fk_gcd_group` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_group_relation_type` (`id`),
  CONSTRAINT `gcd_group_relation_to_group_id_454ce47f_fk_gcd_group_id` FOREIGN KEY (`to_group_id`) REFERENCES `gcd_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_group_relation` WRITE;
/*!40000 ALTER TABLE `gcd_group_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_group_relation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_group_relation_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_group_relation_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reverse_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_group_relation_type` WRITE;
/*!40000 ALTER TABLE `gcd_group_relation_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_group_relation_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_image` (
  `id` int NOT NULL AUTO_INCREMENT,
  `object_id` int unsigned DEFAULT NULL,
  `image_file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `marked` tinyint(1) NOT NULL,
  `created` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `reserved` tinyint(1) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_image_type_id_efd58357_fk_gcd_image_type_id` (`type_id`),
  KEY `gcd_image_content_type_id_1ce97461_fk_django_content_type_id` (`content_type_id`),
  KEY `gcd_image_object_id_5ffd9e0e` (`object_id`),
  KEY `gcd_image_reserved_ef50dfee` (`reserved`),
  KEY `gcd_image_deleted_b5587898` (`deleted`),
  CONSTRAINT `gcd_image_content_type_id_1ce97461_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `gcd_image_type_id_efd58357_fk_gcd_image_type_id` FOREIGN KEY (`type_id`) REFERENCES `gcd_image_type` (`id`),
  CONSTRAINT `gcd_image_chk_1` CHECK ((`object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_image` WRITE;
/*!40000 ALTER TABLE `gcd_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_image` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_image_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_image_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unique` tinyint(1) NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_image_type` WRITE;
/*!40000 ALTER TABLE `gcd_image_type` DISABLE KEYS */;
INSERT INTO `gcd_image_type` VALUES (1,'IndiciaScan',1,'indicia scan'),(2,'SoOScan',1,'statement of ownership'),(3,'BrandScan',1,'brand emblem'),(4,'CreatorPortrait',1,'portrait image'),(5,'SampleScan',1,'sample scan image'),(6,'FeatureLogo',1,'feature logo'),(7,'CreatorSignature',1,'signature scan');
/*!40000 ALTER TABLE `gcd_image_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_indexer_languages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_indexer_languages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `indexer_id` int NOT NULL,
  `language_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_indexer_languages_indexer_id_language_id_3c9ee7ea_uniq` (`indexer_id`,`language_id`),
  KEY `gcd_indexer_language_language_id_3ca859e2_fk_stddata_l` (`language_id`),
  CONSTRAINT `gcd_indexer_language_language_id_3ca859e2_fk_stddata_l` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `gcd_indexer_languages_indexer_id_4ba64730_fk_indexer_indexer_id` FOREIGN KEY (`indexer_id`) REFERENCES `indexer_indexer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_indexer_languages` WRITE;
/*!40000 ALTER TABLE `gcd_indexer_languages` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_indexer_languages` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_indexer_no_show_sequences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_indexer_no_show_sequences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `indexer_id` int NOT NULL,
  `storytype_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_indexer_no_show_sequ_indexer_id_storytype_id_d11f052a_uniq` (`indexer_id`,`storytype_id`),
  KEY `gcd_indexer_no_show__storytype_id_7ca17135_fk_gcd_story` (`storytype_id`),
  CONSTRAINT `gcd_indexer_no_show__indexer_id_805f2173_fk_indexer_i` FOREIGN KEY (`indexer_id`) REFERENCES `indexer_indexer` (`id`),
  CONSTRAINT `gcd_indexer_no_show__storytype_id_7ca17135_fk_gcd_story` FOREIGN KEY (`storytype_id`) REFERENCES `gcd_story_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_indexer_no_show_sequences` WRITE;
/*!40000 ALTER TABLE `gcd_indexer_no_show_sequences` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_indexer_no_show_sequences` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_indicia_printer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_indicia_printer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issue_count` int NOT NULL,
  `country_id` int NOT NULL,
  `parent_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_indicia_printer_country_id_7721a445_fk_stddata_country_id` (`country_id`),
  KEY `gcd_indicia_printer_parent_id_530af9b7_fk_gcd_printer_id` (`parent_id`),
  KEY `gcd_indicia_printer_modified_778425fb` (`modified`),
  KEY `gcd_indicia_printer_deleted_7a641d17` (`deleted`),
  KEY `gcd_indicia_printer_name_2aca0f76` (`name`),
  KEY `gcd_indicia_printer_year_began_c96ca6c5` (`year_began`),
  KEY `gcd_indicia_printer_year_began_uncertain_0bd7f023` (`year_began_uncertain`),
  KEY `gcd_indicia_printer_year_ended_uncertain_efe8024d` (`year_ended_uncertain`),
  KEY `gcd_indicia_printer_year_overall_began_0ef47eac` (`year_overall_began`),
  KEY `gcd_indicia_printer_year_overall_began_uncertain_c73e8a3a` (`year_overall_began_uncertain`),
  KEY `gcd_indicia_printer_year_overall_ended_uncertain_1f5b498c` (`year_overall_ended_uncertain`),
  CONSTRAINT `gcd_indicia_printer_country_id_7721a445_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `gcd_indicia_printer_parent_id_530af9b7_fk_gcd_printer_id` FOREIGN KEY (`parent_id`) REFERENCES `gcd_printer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_indicia_printer` WRITE;
/*!40000 ALTER TABLE `gcd_indicia_printer` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_indicia_printer` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_indicia_publisher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_indicia_publisher` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `is_surrogate` tinyint(1) NOT NULL,
  `issue_count` int NOT NULL,
  `country_id` int NOT NULL,
  `parent_id` int NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_indicia_publisher_parent_id_e3d02b5b_fk_gcd_publisher_id` (`parent_id`),
  KEY `gcd_indicia_publisher_country_id_9de1afed_fk_stddata_country_id` (`country_id`),
  KEY `gcd_indicia_publisher_name_0892ec4b` (`name`),
  KEY `gcd_indicia_publisher_year_began_fbf7d8f4` (`year_began`),
  KEY `gcd_indicia_publisher_year_began_uncertain_f86c4eb1` (`year_began_uncertain`),
  KEY `gcd_indicia_publisher_year_ended_uncertain_86232af6` (`year_ended_uncertain`),
  KEY `gcd_indicia_publisher_deleted_ca6b8ba7` (`deleted`),
  KEY `gcd_indicia_publisher_is_surrogate_50e294ed` (`is_surrogate`),
  KEY `gcd_indicia_publisher_modified_8acaa125` (`modified`),
  KEY `gcd_indicia_publisher_year_overall_began_854f12bb` (`year_overall_began`),
  KEY `gcd_indicia_publisher_year_overall_began_uncertain_d51c93af` (`year_overall_began_uncertain`),
  KEY `gcd_indicia_publisher_year_overall_ended_uncertain_784b92eb` (`year_overall_ended_uncertain`),
  CONSTRAINT `gcd_indicia_publisher_country_id_9de1afed_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `gcd_indicia_publisher_parent_id_e3d02b5b_fk_gcd_publisher_id` FOREIGN KEY (`parent_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_indicia_publisher` WRITE;
/*!40000 ALTER TABLE `gcd_indicia_publisher` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_indicia_publisher` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_issue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_issue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_title` tinyint(1) NOT NULL,
  `volume` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_volume` tinyint(1) NOT NULL,
  `display_volume_with_number` tinyint(1) NOT NULL,
  `isbn` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_isbn` tinyint(1) NOT NULL,
  `valid_isbn` varchar(13) COLLATE utf8mb4_unicode_ci NOT NULL,
  `variant_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `barcode` varchar(38) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_barcode` tinyint(1) NOT NULL,
  `rating` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_rating` tinyint(1) NOT NULL,
  `publication_date` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `key_date` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `on_sale_date` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `on_sale_date_uncertain` tinyint(1) NOT NULL,
  `sort_code` int NOT NULL,
  `indicia_frequency` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_indicia_frequency` tinyint(1) NOT NULL,
  `price` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `page_count` decimal(10,3) DEFAULT NULL,
  `page_count_uncertain` tinyint(1) NOT NULL,
  `editing` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_editing` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `indicia_pub_not_printed` tinyint(1) NOT NULL,
  `no_brand` tinyint(1) NOT NULL,
  `is_indexed` int NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `brand_id` int DEFAULT NULL,
  `indicia_publisher_id` int DEFAULT NULL,
  `series_id` int NOT NULL,
  `variant_of_id` int DEFAULT NULL,
  `volume_not_printed` tinyint(1) NOT NULL,
  `indicia_printer_not_printed` tinyint(1) NOT NULL,
  `variant_cover_status` int NOT NULL,
  `indicia_printer_sourced_by` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_issue_series_id_sort_code_d6535af2_uniq` (`series_id`,`sort_code`),
  KEY `gcd_issue_variant_of_id_38b701d0_fk_gcd_issue_id` (`variant_of_id`),
  KEY `gcd_issue_brand_id_a2b3e323_fk_gcd_brand_id` (`brand_id`),
  KEY `gcd_issue_indicia_publisher_id_a0c46a76_fk_gcd_indic` (`indicia_publisher_id`),
  KEY `gcd_issue_number_f5670748` (`number`),
  KEY `gcd_issue_title_873c2a12` (`title`),
  KEY `gcd_issue_no_title_48a53ca4` (`no_title`),
  KEY `gcd_issue_volume_5f6acc14` (`volume`),
  KEY `gcd_issue_no_volume_34bedf57` (`no_volume`),
  KEY `gcd_issue_display_volume_with_number_e85811b4` (`display_volume_with_number`),
  KEY `gcd_issue_isbn_da8392db` (`isbn`),
  KEY `gcd_issue_no_isbn_1a9ac7fc` (`no_isbn`),
  KEY `gcd_issue_valid_isbn_dae885a0` (`valid_isbn`),
  KEY `gcd_issue_barcode_53de0d1e` (`barcode`),
  KEY `gcd_issue_rating_96a7ea18` (`rating`),
  KEY `gcd_issue_no_rating_3fbcdfb5` (`no_rating`),
  KEY `gcd_issue_key_date_fcdd1984` (`key_date`),
  KEY `gcd_issue_on_sale_date_181ba551` (`on_sale_date`),
  KEY `gcd_issue_sort_code_ebc8ab13` (`sort_code`),
  KEY `gcd_issue_no_indicia_frequency_3d6598e1` (`no_indicia_frequency`),
  KEY `gcd_issue_no_editing_deb5b10c` (`no_editing`),
  KEY `gcd_issue_no_brand_8d0869ea` (`no_brand`),
  KEY `gcd_issue_is_indexed_b2f32eeb` (`is_indexed`),
  KEY `gcd_issue_modified_26238b9f` (`modified`),
  KEY `gcd_issue_deleted_c704175f` (`deleted`),
  KEY `gcd_issue_variant_cover_status_52969645` (`variant_cover_status`),
  CONSTRAINT `gcd_issue_brand_id_a2b3e323_fk_gcd_brand_id` FOREIGN KEY (`brand_id`) REFERENCES `gcd_brand` (`id`),
  CONSTRAINT `gcd_issue_indicia_publisher_id_a0c46a76_fk_gcd_indic` FOREIGN KEY (`indicia_publisher_id`) REFERENCES `gcd_indicia_publisher` (`id`),
  CONSTRAINT `gcd_issue_series_id_ffbfbf73_fk_gcd_series_id` FOREIGN KEY (`series_id`) REFERENCES `gcd_series` (`id`),
  CONSTRAINT `gcd_issue_variant_of_id_38b701d0_fk_gcd_issue_id` FOREIGN KEY (`variant_of_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_issue` WRITE;
/*!40000 ALTER TABLE `gcd_issue` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_issue` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_issue_brand_emblem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_issue_brand_emblem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `issue_id` int NOT NULL,
  `brand_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_issue_brand_emblem_issue_id_brand_id_494f6346_uniq` (`issue_id`,`brand_id`),
  KEY `gcd_issue_brand_emblem_brand_id_4b9b4e20_fk_gcd_brand_id` (`brand_id`),
  CONSTRAINT `gcd_issue_brand_emblem_brand_id_4b9b4e20_fk_gcd_brand_id` FOREIGN KEY (`brand_id`) REFERENCES `gcd_brand` (`id`),
  CONSTRAINT `gcd_issue_brand_emblem_issue_id_c2a07a32_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_issue_brand_emblem` WRITE;
/*!40000 ALTER TABLE `gcd_issue_brand_emblem` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_issue_brand_emblem` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_issue_code_number`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_issue_code_number` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issue_id` int NOT NULL,
  `number_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_issue_code_number_issue_id_cc91cb1b_fk_gcd_issue_id` (`issue_id`),
  KEY `gcd_issue_code_numbe_number_type_id_c53ab04b_fk_gcd_code_` (`number_type_id`),
  KEY `gcd_issue_code_number_modified_32f79afc` (`modified`),
  KEY `gcd_issue_code_number_deleted_823e5d64` (`deleted`),
  KEY `gcd_issue_code_number_number_68dc61bd` (`number`),
  CONSTRAINT `gcd_issue_code_numbe_number_type_id_c53ab04b_fk_gcd_code_` FOREIGN KEY (`number_type_id`) REFERENCES `gcd_code_number_type` (`id`),
  CONSTRAINT `gcd_issue_code_number_issue_id_cc91cb1b_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_issue_code_number` WRITE;
/*!40000 ALTER TABLE `gcd_issue_code_number` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_issue_code_number` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_issue_credit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_issue_credit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `is_credited` tinyint(1) NOT NULL,
  `uncertain` tinyint(1) NOT NULL,
  `credited_as` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credit_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `creator_id` int NOT NULL,
  `credit_type_id` int NOT NULL,
  `issue_id` int NOT NULL,
  `is_sourced` tinyint(1) NOT NULL,
  `sourced_by` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_issue_credit_creator_id_d23239af_fk_gcd_creat` (`creator_id`),
  KEY `gcd_issue_credit_credit_type_id_85428160_fk_gcd_credit_type_id` (`credit_type_id`),
  KEY `gcd_issue_credit_issue_id_928f51d6_fk_gcd_issue_id` (`issue_id`),
  KEY `gcd_issue_credit_modified_92c90a4b` (`modified`),
  KEY `gcd_issue_credit_deleted_28f591fc` (`deleted`),
  KEY `gcd_issue_credit_is_credited_448cd70d` (`is_credited`),
  KEY `gcd_issue_credit_uncertain_a122bed6` (`uncertain`),
  KEY `gcd_issue_credit_is_sourced_f6bb6c2c` (`is_sourced`),
  CONSTRAINT `gcd_issue_credit_creator_id_d23239af_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator_name_detail` (`id`),
  CONSTRAINT `gcd_issue_credit_credit_type_id_85428160_fk_gcd_credit_type_id` FOREIGN KEY (`credit_type_id`) REFERENCES `gcd_credit_type` (`id`),
  CONSTRAINT `gcd_issue_credit_issue_id_928f51d6_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_issue_credit` WRITE;
/*!40000 ALTER TABLE `gcd_issue_credit` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_issue_credit` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_issue_external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_issue_external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `issue_id` int NOT NULL,
  `externallink_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_issue_external_link_issue_id_externallink_id_12da7e2b_uniq` (`issue_id`,`externallink_id`),
  KEY `gcd_issue_external_l_externallink_id_06751732_fk_gcd_exter` (`externallink_id`),
  CONSTRAINT `gcd_issue_external_l_externallink_id_06751732_fk_gcd_exter` FOREIGN KEY (`externallink_id`) REFERENCES `gcd_external_link` (`id`),
  CONSTRAINT `gcd_issue_external_link_issue_id_c13b37eb_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_issue_external_link` WRITE;
/*!40000 ALTER TABLE `gcd_issue_external_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_issue_external_link` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_issue_indicia_printer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_issue_indicia_printer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `issue_id` int NOT NULL,
  `indiciaprinter_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_issue_indicia_printe_issue_id_indiciaprinter__f9448194_uniq` (`issue_id`,`indiciaprinter_id`),
  KEY `gcd_issue_indicia_pr_indiciaprinter_id_c0f3b842_fk_gcd_indic` (`indiciaprinter_id`),
  CONSTRAINT `gcd_issue_indicia_pr_indiciaprinter_id_c0f3b842_fk_gcd_indic` FOREIGN KEY (`indiciaprinter_id`) REFERENCES `gcd_indicia_printer` (`id`),
  CONSTRAINT `gcd_issue_indicia_printer_issue_id_2965892e_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_issue_indicia_printer` WRITE;
/*!40000 ALTER TABLE `gcd_issue_indicia_printer` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_issue_indicia_printer` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_membership_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_membership_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_membership_type` WRITE;
/*!40000 ALTER TABLE `gcd_membership_type` DISABLE KEYS */;
INSERT INTO `gcd_membership_type` VALUES (1,'member'),(2,'president'),(3,'treasurer');
/*!40000 ALTER TABLE `gcd_membership_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_multiverse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_multiverse` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mainstream_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_multiverse_mainstream_id_9a3651b8_fk_gcd_universe_id` (`mainstream_id`),
  KEY `gcd_multiverse_modified_835703a1` (`modified`),
  KEY `gcd_multiverse_deleted_9d0a1781` (`deleted`),
  KEY `gcd_multiverse_name_d34fddb7` (`name`),
  CONSTRAINT `gcd_multiverse_mainstream_id_9a3651b8_fk_gcd_universe_id` FOREIGN KEY (`mainstream_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_multiverse` WRITE;
/*!40000 ALTER TABLE `gcd_multiverse` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_multiverse` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_name_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_name_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_name_type` WRITE;
/*!40000 ALTER TABLE `gcd_name_type` DISABLE KEYS */;
INSERT INTO `gcd_name_type` VALUES (1,'','GCD Official (type is deprecated)'),(2,'','Changed Name'),(3,'','Family (type is deprecated)'),(4,'','Given (birth) (type is deprecated)'),(5,'','House Name'),(6,'','Other Language (type is deprecated)'),(7,'','Pen Name'),(8,'','Studio Name'),(9,'Native Language','Native Language (type is deprecated)'),(10,'','Name at Birth'),(11,'','Common Alternative Name'),(12,'','Ghost Name'),(13,'','Joint Name'),(14,'','Misspelled Name');
/*!40000 ALTER TABLE `gcd_name_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_non_comic_work_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_non_comic_work_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_non_comic_work_role` WRITE;
/*!40000 ALTER TABLE `gcd_non_comic_work_role` DISABLE KEYS */;
INSERT INTO `gcd_non_comic_work_role` VALUES (1,'Owner'),(2,'Employee'),(3,'Art Director'),(4,'Artist'),(5,'Editor'),(6,'Animator'),(7,'Writer'),(8,'Set Designer'),(9,'Actor'),(10,'Voice Actor'),(11,'Assistant');
/*!40000 ALTER TABLE `gcd_non_comic_work_role` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_non_comic_work_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_non_comic_work_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_non_comic_work_type` WRITE;
/*!40000 ALTER TABLE `gcd_non_comic_work_type` DISABLE KEYS */;
INSERT INTO `gcd_non_comic_work_type` VALUES (1,'Book'),(2,'Magazine'),(3,'Newspaper'),(4,'Television'),(5,'Radio'),(6,'Movie'),(7,'Live Show'),(8,'Advertising'),(9,'Fine Arts'),(10,'Web Comics'),(11,'Internet Article'),(12,'Other');
/*!40000 ALTER TABLE `gcd_non_comic_work_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_non_comic_work_year`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_non_comic_work_year` (
  `id` int NOT NULL AUTO_INCREMENT,
  `work_year` smallint unsigned DEFAULT NULL,
  `work_year_uncertain` tinyint(1) NOT NULL,
  `non_comic_work_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_non_comic_work_y_non_comic_work_id_5b94ec22_fk_gcd_creat` (`non_comic_work_id`),
  CONSTRAINT `gcd_non_comic_work_y_non_comic_work_id_5b94ec22_fk_gcd_creat` FOREIGN KEY (`non_comic_work_id`) REFERENCES `gcd_creator_non_comic_work` (`id`),
  CONSTRAINT `gcd_non_comic_work_year_chk_1` CHECK ((`work_year` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_non_comic_work_year` WRITE;
/*!40000 ALTER TABLE `gcd_non_comic_work_year` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_non_comic_work_year` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_printer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_printer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `indicia_printer_count` int NOT NULL,
  `issue_count` int NOT NULL,
  `country_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_printer_country_id_889421fa_fk_stddata_country_id` (`country_id`),
  KEY `gcd_printer_modified_f0a0e321` (`modified`),
  KEY `gcd_printer_deleted_3b0b11ef` (`deleted`),
  KEY `gcd_printer_name_97854c5f` (`name`),
  KEY `gcd_printer_year_began_9471a3eb` (`year_began`),
  KEY `gcd_printer_year_began_uncertain_0b919273` (`year_began_uncertain`),
  KEY `gcd_printer_year_ended_uncertain_ff75a9b0` (`year_ended_uncertain`),
  KEY `gcd_printer_year_overall_began_3ba498cd` (`year_overall_began`),
  KEY `gcd_printer_year_overall_began_uncertain_4225255a` (`year_overall_began_uncertain`),
  KEY `gcd_printer_year_overall_ended_uncertain_5e639616` (`year_overall_ended_uncertain`),
  KEY `gcd_printer_indicia_printer_count_c38d8965` (`indicia_printer_count`),
  CONSTRAINT `gcd_printer_country_id_889421fa_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_printer` WRITE;
/*!40000 ALTER TABLE `gcd_printer` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_printer` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_publisher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_publisher` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `brand_count` int NOT NULL,
  `indicia_publisher_count` int NOT NULL,
  `series_count` int NOT NULL,
  `issue_count` int NOT NULL,
  `country_id` int NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_publisher_country_id_6682a430_fk_stddata_country_id` (`country_id`),
  KEY `gcd_publisher_name_1a77c2ca` (`name`),
  KEY `gcd_publisher_year_began_6b18d73d` (`year_began`),
  KEY `gcd_publisher_year_began_uncertain_e6fba77f` (`year_began_uncertain`),
  KEY `gcd_publisher_year_ended_uncertain_026e2502` (`year_ended_uncertain`),
  KEY `gcd_publisher_deleted_1f65bcff` (`deleted`),
  KEY `gcd_publisher_brand_count_16a89a6f` (`brand_count`),
  KEY `gcd_publisher_indicia_publisher_count_f41df2f6` (`indicia_publisher_count`),
  KEY `gcd_publisher_modified_975dfd29` (`modified`),
  KEY `gcd_publisher_year_overall_began_281cdf77` (`year_overall_began`),
  KEY `gcd_publisher_year_overall_began_uncertain_7213c847` (`year_overall_began_uncertain`),
  KEY `gcd_publisher_year_overall_ended_uncertain_e155ab76` (`year_overall_ended_uncertain`),
  CONSTRAINT `gcd_publisher_country_id_6682a430_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_publisher` WRITE;
/*!40000 ALTER TABLE `gcd_publisher` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_publisher` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_publisher_external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_publisher_external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `publisher_id` int NOT NULL,
  `externallink_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_publisher_external_l_publisher_id_externallin_ca957ad1_uniq` (`publisher_id`,`externallink_id`),
  KEY `gcd_publisher_extern_externallink_id_8bdc6130_fk_gcd_exter` (`externallink_id`),
  CONSTRAINT `gcd_publisher_extern_externallink_id_8bdc6130_fk_gcd_exter` FOREIGN KEY (`externallink_id`) REFERENCES `gcd_external_link` (`id`),
  CONSTRAINT `gcd_publisher_extern_publisher_id_14f70970_fk_gcd_publi` FOREIGN KEY (`publisher_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_publisher_external_link` WRITE;
/*!40000 ALTER TABLE `gcd_publisher_external_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_publisher_external_link` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_received_award`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_received_award` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `object_id` int unsigned DEFAULT NULL,
  `award_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_award_name` tinyint(1) NOT NULL,
  `award_year` smallint unsigned DEFAULT NULL,
  `award_year_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `award_id` int DEFAULT NULL,
  `content_type_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_received_award_award_id_a1daee53_fk_gcd_award_id` (`award_id`),
  KEY `gcd_received_award_content_type_id_76c10020_fk_django_co` (`content_type_id`),
  KEY `gcd_received_award_modified_dfc45335` (`modified`),
  KEY `gcd_received_award_deleted_db659429` (`deleted`),
  CONSTRAINT `gcd_received_award_award_id_a1daee53_fk_gcd_award_id` FOREIGN KEY (`award_id`) REFERENCES `gcd_award` (`id`),
  CONSTRAINT `gcd_received_award_content_type_id_76c10020_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `gcd_received_award_chk_1` CHECK ((`object_id` >= 0)),
  CONSTRAINT `gcd_received_award_chk_2` CHECK ((`award_year` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_received_award` WRITE;
/*!40000 ALTER TABLE `gcd_received_award` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_received_award` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_received_award_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_received_award_data_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `receivedaward_id` int NOT NULL,
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_received_award_data__receivedaward_id_datasou_731a5c0a_uniq` (`receivedaward_id`,`datasource_id`),
  KEY `gcd_received_award_d_datasource_id_289672c6_fk_gcd_data_` (`datasource_id`),
  CONSTRAINT `gcd_received_award_d_datasource_id_289672c6_fk_gcd_data_` FOREIGN KEY (`datasource_id`) REFERENCES `gcd_data_source` (`id`),
  CONSTRAINT `gcd_received_award_d_receivedaward_id_09c11d85_fk_gcd_recei` FOREIGN KEY (`receivedaward_id`) REFERENCES `gcd_received_award` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_received_award_data_source` WRITE;
/*!40000 ALTER TABLE `gcd_received_award_data_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_received_award_data_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_relation_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_relation_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reverse_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_relation_type` WRITE;
/*!40000 ALTER TABLE `gcd_relation_type` DISABLE KEYS */;
INSERT INTO `gcd_relation_type` VALUES (1,'Similar Name','Similar Name'),(2,'Owner','Owned by'),(3,'Employee','Employer'),(4,'User','Used by'),(5,'Child','Parent'),(6,'Spouse','Spouse');
/*!40000 ALTER TABLE `gcd_relation_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_reprint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_reprint` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `origin_id` int DEFAULT NULL,
  `target_id` int DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `origin_issue_id` int NOT NULL,
  `target_issue_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_reprint_origin_id_48220c89_fk_gcd_story_id` (`origin_id`),
  KEY `gcd_reprint_target_id_44bd71ce_fk_gcd_story_id` (`target_id`),
  KEY `gcd_reprint_modified_b8966555` (`modified`),
  KEY `gcd_reprint_origin_issue_id_35ba9bf2_fk_gcd_issue_id` (`origin_issue_id`),
  KEY `gcd_reprint_target_issue_id_c4c7d013_fk_gcd_issue_id` (`target_issue_id`),
  CONSTRAINT `gcd_reprint_origin_id_48220c89_fk_gcd_story_id` FOREIGN KEY (`origin_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `gcd_reprint_origin_issue_id_35ba9bf2_fk_gcd_issue_id` FOREIGN KEY (`origin_issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `gcd_reprint_target_id_44bd71ce_fk_gcd_story_id` FOREIGN KEY (`target_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `gcd_reprint_target_issue_id_c4c7d013_fk_gcd_issue_id` FOREIGN KEY (`target_issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_reprint` WRITE;
/*!40000 ALTER TABLE `gcd_reprint` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_reprint` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_school`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_school` (
  `id` int NOT NULL AUTO_INCREMENT,
  `school_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=636 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_school` WRITE;
/*!40000 ALTER TABLE `gcd_school` DISABLE KEYS */;
INSERT INTO `gcd_school` VALUES (1,'Abilene Christian College'),(2,'Académie de la Grande Chaumière [Paris]'),(3,'Académie Julian [Paris]'),(4,'Académie Royale des Beaux-Arts [Brussels]'),(5,'Academy of Art College'),(6,'Academy of Art College [San Francisco]'),(7,'Academy of Brera [Milan]'),(8,'Academy of Design'),(9,'Academy of Design [NYC]'),(10,'Academy of Fine Arts'),(11,'Academy of Fine Arts [Bologna, Italy]'),(12,'Academy of Fine Arts [Chicago]'),(13,'Academy of Fine Arts [Italy]'),(14,'Academy of Fine Arts [Paris]'),(15,'Academy of Fine Arts [Rome]'),(16,'Adelphi University [Long Island, New York]'),(17,'Advertising Art School [Portland]'),(18,'Alberta College of Art'),(19,'Albright College'),(20,'Albright School of Art [Buffalo, New York]'),(21,'Alexander Mackie School of Art'),(22,'Alfred University'),(23,'American Academy of Art [Chicago]'),(24,'American Artists School'),(25,'American School of Design [NYC]'),(26,'American University [Washington, D.C.]'),(27,'Amherst College'),(28,'Antioch College [Yellow Springs, Ohio]'),(29,'Arizona State University'),(30,'Armed Forces Information School [Pennsylvania]'),(31,'Army Extension Correspondence Course'),(32,'Art Academy of Cincinnati'),(33,'Art Career School [NYC]'),(34,'Art Center College of Design [Pasadena, California]'),(35,'Art Center School [Los Angeles]'),(36,'Art College [U.K.]'),(37,'Art Institute of Boston'),(38,'Art Institute of Chicago'),(39,'Art Institute of Ft. Lauderdale'),(40,'Art Institute of Minneapolis'),(41,'Art Institute of Pittsburgh'),(42,'Art Institute School [Chicago]'),(43,'Art Instruction Schools [Minneapolis, Minnesota]'),(44,'Art Instruction, Inc.'),(45,'Art School of Brera'),(46,'Art School, Richmond Professional Institute, Virginia Commonwealth University'),(47,'Art Students League'),(48,'Artist Guild'),(49,'Arts and Crafts [Detroit]'),(50,'Arts and Crafts Club [New Orleans]'),(51,'Ashland University'),(52,'Asnuntuck College'),(53,'ASU Art College'),(54,'Atelier Julian [Paris, France]'),(55,'Auburn University'),(56,'Auckland University [New Zealand]'),(57,'Austin Community College'),(58,'Avionics Systems Tech.'),(59,'Bakersfield College'),(60,'Ball State University'),(61,'Banbury Art College [U.K.]'),(62,'Bankstown Technical College'),(63,'Bard College'),(64,'Barstow Community College'),(65,'Baylor University'),(66,'Beaux Arts Institute'),(67,'Beckenham School of Art'),(68,'Benedictine College'),(69,'Benjamin Cardoz School of Law'),(70,'Berry College'),(71,'Beth Isreal Medical Center School of Nursing'),(72,'Billy Hon\'s Cartoon School'),(73,'Birmingham Southern College [Alabama]'),(74,'Bliss College'),(75,'Boise State University [Idaho]'),(76,'Boston College'),(77,'Boston University'),(78,'Bowdoin College [Maine]'),(79,'Bowling Green University'),(80,'Bradley University'),(81,'Brandeis University'),(82,'Brigham Young University'),(83,'Brighton Polytech [U.K.]'),(84,'Brock University'),(85,'Brooklyn Academy of Fine Arts'),(86,'Brooklyn College of the City University of New York (CUNY)'),(87,'Brooklyn Community College'),(88,'Brooklyn High School of Music and Art'),(89,'Brooklyn Museum Art School'),(90,'Brooklyn School of Law'),(91,'Brooklyn School of Visual Arts'),(92,'Brown University'),(93,'Burnley School of Commercial Art'),(94,'Buscema School'),(95,'California Art School [Los Angeles]'),(96,'California College of Arts and Crafts [Oakland]'),(97,'California College of Arts and Crafts [San Francisco]'),(98,'California Institute of Arts [Valencia, CA]'),(99,'California School of Fine Arts'),(100,'California State University'),(101,'California State University [Chico]'),(102,'California State University [Fresno]'),(103,'California State University [Long Beach]'),(104,'California State University [Los Angeles]'),(105,'California State University [Northridge]'),(106,'Camberwell College of Art'),(107,'Cambridge'),(108,'Cambridge Junior College'),(109,'Cambridge University [U.K.]'),(110,'Carlos Academy [New York]'),(111,'Carnegie Institute of Technology'),(112,'Carnegie-Mellon University'),(113,'Cartoonists and Illustrators School'),(114,'Catholic University'),(115,'Center for Creative Studies [Detroit]'),(116,'Central School of Art [London, U.K.]'),(117,'Central School of London'),(118,'Central State University'),(119,'Central State University [Oklahoma]'),(120,'Central Texas College'),(121,'Centre Pompidou'),(122,'Chabot College, University of California [Berkely]'),(123,'Chare Art School'),(124,'Chelsea School of Art'),(125,'Chicago Academy of Fine Arts'),(126,'Chicago Art Institute'),(127,'Chicago Professional School of Cartooning'),(128,'Chouinard Art Institute [Los Angeles]'),(129,'Christopher Newport University [Virginia]'),(130,'Cincinnati Art Institute'),(131,'City College of the City University of New York (CUNY)'),(132,'City University of New York (CUNY)'),(133,'Clarkamus Community College'),(134,'Clemson University'),(135,'Cleveland College of Art and Design [U.K.]'),(136,'Cleveland Institute of Art'),(137,'Cleveland School of Art'),(138,'Coastal Carolina Community College in Jacksonville'),(139,'Colgate University'),(140,'College of Commerce'),(141,'College of Industrial Arts [Denton, Texas]'),(142,'College of Mt. St. Joseph'),(143,'College of New Rochelle'),(144,'College of St. Thomas [St. Paul]'),(145,'College of Staten Island of the City University of New York (CUNY)'),(146,'Colorado Institute of Art [Denver]'),(147,'Colorado State University'),(148,'Columbia College'),(149,'Columbia College [Chicago]'),(150,'Columbia College of Radio Announcing and Writing'),(151,'Columbia University'),(152,'Columbus College of Art and Design [Ohio]'),(153,'Commercial Art Technical Schools'),(154,'Commercial Illustrators School'),(155,'Cooper School [Cleveland]'),(156,'Cooper Union School of Art [NYC]'),(157,'Corcoran School of Art [Washington D.C.]'),(158,'Cornell University'),(159,'Correspondence Art Institute'),(160,'Couinard Art School, California Institute of Arts'),(161,'Cranbrook Academy of Art [Michigan]'),(162,'Dana College, Blair [Maine]'),(163,'Danforth Tech [Toronto]'),(164,'Dartmouth University'),(165,'Dawson College'),(166,'Dayton Art Institute [Ohio]'),(167,'De Pauw University'),(168,'Defense Information School'),(169,'Detroit Art Academy'),(170,'Detroit City College'),(171,'DeWitt Clinton High School [Bronx]'),(172,'Drexel Institute'),(173,'East Carolina State College'),(174,'East Central University [Ada, Oklahoma]'),(175,'East Ham Technical College [London, U.K.]'),(176,'Eastbourne College'),(177,'Eastern Michigan University'),(178,'Eastern Montana College'),(179,'École des Arts Appliqués [Paris]'),(180,'École des Beaux-Arts [Paris]'),(181,'École Industrielle [Luxumberg]'),(182,'Emily Carr College of Art'),(183,'Escuela Superior de Arte [Spain]'),(184,'Essex Art Institute [Boston]'),(185,'Evergreen State College [Washington]'),(186,'Famous Artists School'),(187,'Fanshawe College [Ontario]'),(188,'Farmingdale College'),(189,'Fawcett Art School [Newark]'),(190,'FEATI University [Sta. Cruz, Philippines]'),(191,'Federal School of Illustrating [Minneapolis]'),(192,'Federal Schools, Art Institute Inc.'),(193,'Filton Technical College'),(194,'Finch College'),(195,'Florida State University'),(196,'Fordham University'),(197,'Frank J. Reilly School of Art'),(198,'Franklin and Marshall Academy'),(199,'Franklin Art School'),(200,'Ft. Wayne Art School [Indiana]'),(201,'General Motors Institute [Flint, Michigan]'),(202,'Genesee Area Skill Center'),(203,'George Mason University'),(204,'George Washington University'),(205,'George Watson\'s Ladies\' College [Edinburgh]'),(206,'Georgetown University'),(207,'Georgia State College'),(208,'Georgia State University'),(209,'Girls Commercial High School'),(210,'Glasgow School of Art [Scotland]'),(211,'Glassboro State College [New Jersey]'),(212,'Grand Central School of Art [NYC]'),(213,'Graphic Arts School'),(214,'Green River Community College [Washington]'),(215,'Greenfield Community College'),(216,'Hamilton Ontario Art School'),(217,'Hamlin University'),(218,'Hartford Art School [Connecticut]'),(219,'Harvard Univserity'),(220,'Hastings Animation School'),(221,'Hayward State University'),(222,'Hewitt School of Journalism [Chicago]'),(223,'High Point University [North Carolina]'),(224,'High School of Art and Design [NYC]'),(225,'High School of Industrial Arts [NYC]'),(226,'High School of Music and Art [NYC]'),(227,'HND Graphics, Granville College'),(228,'Hofstra University [New York]'),(229,'Hollywood Art Center'),(230,'Holy Cross College'),(231,'Honolulu Academy of Art'),(232,'Humbolt State [Arcata, California]'),(233,'Hunter College of the City University of New York (CUNY)'),(234,'Hussian School of Art [Philadelphia]'),(235,'Illinois State University'),(236,'Indiana University'),(237,'Iona College'),(238,'Iowa Academy of Fine Arts'),(239,'Iowa State University'),(240,'Ithaca College [New York]'),(241,'Ivy School of Professional Art [Pittsburgh]'),(242,'Jean Morgan School of Art'),(243,'Jefferson Davis Jr. College [Gulfport, Mississippi]'),(244,'Joe Kubert School of Cartoon and Graphic Arts'),(245,'Joe Rubinstein Invitational Masters Class'),(246,'John Cass School [London, U.K.]'),(247,'John Herron School of Art, Indiana University'),(248,'John Huntington Polytechnical Institute [Cleveland, Ohio]'),(249,'John Machamer\'s School of Art [California]'),(250,'Johnson County Community College [Kansas City, Kansas]'),(251,'Johnson State College [Vermont]'),(252,'Joliet Junior College [Joliet, Illinois]'),(253,'Junior College of Albany [NYC]'),(254,'Kansas City Art Institute [Missouri]'),(255,'Kansas State University [Manhattan, Kansas]'),(256,'Kendall College of Art and Design'),(257,'Kent State University'),(258,'Kingston School of Art'),(259,'Knox College'),(260,'Kushuin University'),(261,'Kutztown State University [Pennsylvania]'),(262,'La Roche College [Pittsburgh]'),(263,'Lake Forest College'),(264,'Landon School [high school]'),(265,'Landon School of Illustrating and Cartooning [Cleveland]'),(266,'Leeds College of Art [U.K.]'),(267,'Leeds Polytechnic University [U.K.]'),(268,'Leicester Polytechnic'),(269,'Liege University [Belgium]'),(270,'London Cartoon Centre'),(271,'Long Beach State University'),(272,'Long Island University'),(273,'Los Angeles Art Center School'),(274,'Los Angeles Art Institute'),(275,'Los Angeles City College'),(276,'Los Angeles County Art Institute'),(277,'Los Angeles School of Design'),(278,'Louisiana State University'),(279,'Louisiana Tech'),(280,'Loyola University'),(281,'Lukits [Los Angeles]'),(282,'Madison Area Technical College'),(283,'Manhattan\'s High School of Music and Art'),(284,'Mapau Institute of Technology [Philippines]'),(285,'Maricopa Tech [Arizona]'),(286,'Mark Hopkins Institute of Art [San Francisco]'),(287,'Marquette University'),(288,'Marshall University'),(289,'Maryland Institute College of Art'),(290,'Massachusetts College of Art and Design'),(291,'McGill University'),(292,'Mechanics Art Institute'),(293,'Mechanics Institute'),(294,'Mechanics Institute [Rochester, New York]'),(295,'Medical College of Virginia'),(296,'Meinzinger School of Art [Detroit]'),(297,'Metro Art School [Phoenix]'),(298,'Miami School of Art [Florida]'),(299,'Miami University'),(300,'Miami-Dade Community College'),(301,'Michigan State University'),(302,'Midland College'),(303,'Midland College [Fremont, Nebraska]'),(304,'Mills Academy [St. Paul]'),(305,'Milwaukee Institute of Design'),(306,'Milwaukee State Teachers College [University of Wisconsin]'),(307,'Milwaukee Technical High School'),(308,'Minneapolis College Art and Design'),(309,'Minneapolis Institute of Art'),(310,'Minnesota School of Art'),(311,'Mont Saint-Louis'),(312,'Montana State University'),(313,'Montreal School of Fine Arts'),(314,'Moody Bible School'),(315,'Murray State University [Kentucky]'),(316,'Museum of Art'),(317,'Museum School of Modern Art'),(318,'Nassau Community College'),(319,'National Academy of Design [Dartmouth]'),(320,'National School of Fine Arts [Peru]'),(321,'New College of California'),(322,'New England School of Art'),(323,'New Haven State Teachers College'),(324,'New School'),(325,'New School of Social Research'),(326,'New School, Parsons School of Design [NYC]'),(327,'New School, Parsons School of Design [Paris]'),(328,'New York Advertising Art School'),(329,'New York Art School'),(330,'New York City Community College'),(331,'New York City Technical College'),(332,'New York Law School'),(333,'New York Maritime College'),(334,'New York Musical Institute'),(335,'New York School of Art and Design'),(336,'New York School of Fine and Applied Arts [Parsons]'),(337,'New York School of Industrial Arts'),(338,'New York School of Printing'),(339,'New York School of Visual Arts'),(340,'New York State University'),(341,'New York University'),(342,'New York University Film School'),(343,'New York University School of Arts'),(344,'Newark School of Fine and Industrial Arts'),(345,'Newark State College'),(346,'Northeast Louisiana University'),(347,'Northeastern University'),(348,'Northern Illinois University'),(349,'Northern Michigan University'),(350,'Northern State College [Aberdeen, South Dakota]'),(351,'Northwestern University'),(352,'Northwestern University of Louisiana'),(353,'Notre Dame University'),(354,'Oakland University'),(355,'Oberlin College'),(356,'Occidental College [California]'),(357,'Ohio State University'),(358,'Oklahoma City Southwestern'),(359,'Oklahoma State University at Okmulgee'),(360,'Ontario College of Art'),(361,'Otis Art Institute [Los Angeles]'),(362,'Oxford University'),(363,'Pace College [NYC]'),(364,'Palette and Chisel Academy [Chicago]'),(365,'Pan American Art School'),(366,'Paris School of Design [France]'),(367,'Park College'),(368,'Pasadena City College'),(369,'Penn State University'),(370,'Pennsylvania Academy of the Fine Arts'),(371,'Phil Stel\'s Rocky Mountain School of Art [Denver]'),(372,'Philadelphia College of Art'),(373,'Philadelphia Museum School of Industrial Art'),(374,'Phillips Junior College'),(375,'Phoenix Art Institute [NYC]'),(376,'Phoenix School of Design [NYC]'),(377,'Polytechnic [Huddersfield, U.K.]'),(378,'Polytechnic Institute of New York'),(379,'Pomona College [California]'),(380,'Port Royal Atelier Studios'),(381,'Portfolio Center'),(382,'Portland Academy of Fine Arts'),(383,'Portland Art Museum Film Study Center'),(384,'Portland State University'),(385,'Pratt Institute [Brooklyn]'),(386,'Preston Polytech'),(387,'Prince George Community College'),(388,'Princeton University'),(389,'Providence College [Rhode Island]'),(390,'Purdue University'),(391,'Queens College of the City University of New York (CUNY)'),(392,'Quinnipiac College'),(393,'Radcliffe Museum of Modern Art'),(394,'Ravensbourne College of Art'),(395,'Red River Community College [Winnipeg]'),(396,'Reformed Eposcopal Seminary'),(397,'Rhode Island School of Design'),(398,'Rhodes School'),(399,'Richmond Art School'),(400,'Richmond Professional Institute'),(401,'Rider College'),(402,'Ringling School of Art and Design [Sarasota, Florida]'),(403,'Rio Grande College'),(404,'Rochester Art Institute'),(405,'Rochester Institute of Technology'),(406,'Rome Academy'),(407,'Roosevelt College'),(408,'Roosevelt University'),(409,'Royal Ontario College of Art'),(410,'Russell Sage'),(411,'Rutgers University'),(412,'Sacramento City College [California]'),(413,'Salem Commercial'),(414,'San Francisco Academy of Art'),(415,'San Francisco State University'),(416,'San Jose State University [California]'),(417,'Santa Monica College'),(418,'Sarah Lawrence College [New York]'),(419,'School of Art and Design'),(420,'School of Art and Design [Boston]'),(421,'School of Art in Barcelona'),(422,'School of Art Studies [NYC]'),(423,'School of Art-Life Illustration [New Jersey]'),(424,'School of Industrial Arts [NYC]'),(425,'School of Music and Art [NYC]'),(426,'School of the Art Institute of Chicago'),(427,'School of the Museum of Fine Arts [Tufts, Boston]'),(428,'School of Visual Arts [NYC]'),(429,'Schule Reimann [Berlin]'),(430,'Scranton Correspondence School'),(431,'Scuola di Magistero d\'Arte'),(432,'Seddon Memorial Polytechnic'),(433,'Shepherd College [West Virginia]'),(434,'Sheridan College'),(435,'Sheridan College School of Visual Arts [Oakville, Ontario]'),(436,'Shimer College, Museum Art'),(437,'Silvermine Guild'),(438,'Smith College'),(439,'Society of Arts and Crafts [Detroit]'),(440,'Society of Typographic Art [Chicago]'),(441,'Sonoma State University of California'),(442,'Sorbonne [Paris]'),(443,'Sorsogon School of Arts and Trades [Philippines]'),(444,'South West Essex Tech and School of Art'),(445,'Southeast Missouri State University [Cape Girardeau]'),(446,'Southeastern Massachusetts University'),(447,'Southern Illinois University'),(448,'Southwest Texas State University'),(449,'Spertus College'),(450,'St. Andrews University'),(451,'St. Anselm\'s College [New Hampshire]'),(452,'St. Edmond Hall [Oxford, U.K.]'),(453,'St. John\'s College'),(454,'St. John\'s Law School'),(455,'St. John\'s University'),(456,'St. Louis Brush and Pencil Club'),(457,'St. Louis School of Fine Arts'),(458,'St. Louis University'),(459,'St. Martin\'s School of Art'),(460,'St. Peter\'s College'),(461,'Staffordshire Polytechnic'),(462,'Stanford University'),(463,'State Normal College [Ohio]'),(464,'State University of New York'),(465,'State University of New York [Albany]'),(466,'State University of New York [Binghamton]'),(467,'State University of New York [Buffalo]'),(468,'State University of New York [Farmingdale]'),(469,'State University of New York [Fredonia]'),(470,'State University of New York [New Paltz]'),(471,'State University of New York [Oswego]'),(472,'Stockton State College'),(473,'Stony Brook University'),(474,'Suffolk Law School'),(475,'Suhrabul Art College [Seoul]'),(476,'Sunderland College of Art [U.K.]'),(477,'Syracuse University'),(478,'Technikum [Bingen, Germany]'),(479,'Temple University'),(480,'Temple University, Tyler School of Fine Arts'),(481,'Texarkana College'),(482,'Texas A&M University'),(483,'Texas Technological University'),(484,'Thomas School of Art'),(485,'Towson State University [Maryland]'),(486,'Traphagen School of Fashion'),(487,'Trinity College'),(488,'Trinity University'),(489,'Trinity University [San Antonio, Texas]'),(490,'Twickenham Art College'),(491,'Tyler School of Art [Philadelphia]'),(492,'U.S. International University [U.K.]'),(493,'Union Graduate School [Cincinnati]'),(494,'Universidad de Michoacan [Mexico]'),(495,'University College, University of London'),(496,'University of Akron'),(497,'University of Alabama'),(498,'University of Arizona'),(499,'University of Arizona'),(500,'University of Baltimore'),(501,'University of Berlin'),(502,'University of Bridgeport'),(503,'University of British Columbia'),(504,'University of California'),(505,'University of California [Berkeley]'),(506,'University of California [Davis]'),(507,'University of California [Irvine]'),(508,'University of California [Los Angeles]'),(509,'University of California [Riverside]'),(510,'University of California [San Diego]'),(511,'University of California [Santa Barbara]'),(512,'University of California [Santa Cruz]'),(513,'University of Central Florida'),(514,'University of Chicago'),(515,'University of Cincinnati'),(516,'University of Colorado'),(517,'University of Connecticut'),(518,'University of Dayton [Ohio]'),(519,'University of Delaware'),(520,'University of Evansville [Indiana]'),(521,'University of Florida [Gainesville]'),(522,'University of Frankfurt'),(523,'University of Georgia'),(524,'University of Georgia [Athens]'),(525,'University of Hartford'),(526,'University of Hawaii'),(527,'University of Idaho'),(528,'University of Illinois'),(529,'University of Illinois [Campagne-Urbana]'),(530,'University of Illinois [Chicago]'),(531,'University of Illinois Fine Arts School'),(532,'University of Iowa'),(533,'University of Kansas'),(534,'University of Louisiana'),(535,'University of Louisville'),(536,'University of Lowell [Massachusetts]'),(537,'University of Maine'),(538,'University of Manitoba [Canada]'),(539,'University of Maryland'),(540,'University of Maryland Nursing School'),(541,'University of Massachusetts'),(542,'University of Massachusetts [Amherst]'),(543,'University of Massechusetts [Dorchester]'),(544,'University of Miami'),(545,'University of Miami Film School'),(546,'University of Michigan'),(547,'University of Minnesota'),(548,'University of Missouri'),(549,'University of Missouri [Columbia]'),(550,'University of Missouri [Kansas City]'),(551,'University of Nebraska'),(552,'University of Nevada'),(553,'University of North Carolina'),(554,'University of North Carolina [Greensboro]'),(555,'University of Northern Colorado'),(556,'University of Oklahoma'),(557,'University of Oregon'),(558,'University of Ottawa'),(559,'University of Pennsylvania'),(560,'University of Santa Clara'),(561,'University of Santiago [Chile]'),(562,'University of Sao Paolo'),(563,'University of South Carolina'),(564,'University of South Dakota'),(565,'University of Southern California'),(566,'University of Southern Florida'),(567,'University of Southern Mississippi'),(568,'University of Southwestern Louisiana'),(569,'University of St. Thomas'),(570,'University of Texas'),(571,'University of Texas [Austin]'),(572,'University of Texas [El Paso]'),(573,'University of the Philippines'),(574,'University of the State of New York'),(575,'University of Toledo'),(576,'University of Toronto'),(577,'University of Washington'),(578,'University of Waterloo'),(579,'University of Winnipeg [Canada]'),(580,'University of Wisconsin'),(581,'University of Wisconsin [Madison]'),(582,'University of Wisconsin [Milwaukee]'),(583,'University of Wisconsin [Oshkosh]'),(584,'University of Wisconsin Extension'),(585,'University of Wyoming'),(586,'University of Zagreb [Croatia]'),(587,'Upper Canada College'),(588,'Valley City College'),(589,'Valley State'),(590,'Venice School of Fine Arts'),(591,'Vesper George School of Art [Boston]'),(592,'Vienna Academy of Fine Arts'),(593,'Virginia Commonwealth University'),(594,'Virginia Polytechnic Institute (Virginia Tech)'),(595,'Virginia Union University'),(596,'Wabash College'),(597,'Waco Tech'),(598,'Walt Disney Animation School'),(599,'Walt Disney Studios Training Program'),(600,'Waseda University [Tokyo]'),(601,'Washburn Tech'),(602,'Washburn University [Kansas]'),(603,'Washington School of Art'),(604,'Washington State University'),(605,'Washington University'),(606,'Washington University [St. Louis]'),(607,'Wayne County Community College'),(608,'Wayne State University [Detroit]'),(609,'Wellesley College'),(610,'Wesleyan University'),(611,'Wesleyan University [Connecticut]'),(612,'West Texas State University'),(613,'West Valley Occupational Center [California]'),(614,'West Virginia University'),(615,'Western Connecticut State University'),(616,'Western Kentucky University'),(617,'Western Oregon State College'),(618,'Western Tech [Toronto]'),(619,'Western Washington State University'),(620,'Western Washington University'),(621,'Westminster College'),(622,'Whitney School of Art [Connecticut]'),(623,'Wicker Art School'),(624,'Wigan School of Art'),(625,'Wilcox Technical School [Meriden, Connecticut]'),(626,'Williams College'),(627,'Williams College [Massachusetts]'),(628,'Wittenberg University [Ohio]'),(629,'World Campus Afloat'),(630,'WPA Art Classes'),(631,'Yale School of Fine Arts'),(632,'Yale University'),(633,'Yale University School of Art and Architecture'),(634,'York University [Toronto]'),(635,'Youngstown State');
/*!40000 ALTER TABLE `gcd_school` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_series` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `format` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dimensions` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `paper_stock` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `binding` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `publishing_format` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int NOT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `is_current` tinyint(1) NOT NULL,
  `publication_dates` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issue_count` int NOT NULL,
  `tracking_notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `has_barcode` tinyint(1) NOT NULL,
  `has_indicia_frequency` tinyint(1) NOT NULL,
  `has_isbn` tinyint(1) NOT NULL,
  `has_issue_title` tinyint(1) NOT NULL,
  `has_volume` tinyint(1) NOT NULL,
  `has_rating` tinyint(1) NOT NULL,
  `is_comics_publication` tinyint(1) NOT NULL,
  `is_singleton` tinyint(1) NOT NULL,
  `has_gallery` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `country_id` int NOT NULL,
  `first_issue_id` int DEFAULT NULL,
  `language_id` int NOT NULL,
  `last_issue_id` int DEFAULT NULL,
  `publication_type_id` int DEFAULT NULL,
  `publisher_id` int NOT NULL,
  `has_about_comics` tinyint(1) NOT NULL,
  `has_indicia_printer` tinyint(1) NOT NULL,
  `has_publisher_code_number` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_series_publication_type_id_cf4742f1_fk_gcd_serie` (`publication_type_id`),
  KEY `gcd_series_publisher_id_6389ecaa_fk_gcd_publisher_id` (`publisher_id`),
  KEY `gcd_series_country_id_82a3fe9e_fk_stddata_country_id` (`country_id`),
  KEY `gcd_series_first_issue_id_46e8a82c_fk_gcd_issue_id` (`first_issue_id`),
  KEY `gcd_series_language_id_69197ee7_fk_stddata_language_id` (`language_id`),
  KEY `gcd_series_last_issue_id_8c2b6b93_fk_gcd_issue_id` (`last_issue_id`),
  KEY `gcd_series_name_eb3fdff0` (`name`),
  KEY `gcd_series_sort_name_3330ea57` (`sort_name`),
  KEY `gcd_series_year_began_46b07eba` (`year_began`),
  KEY `gcd_series_is_current_9c0bbad9` (`is_current`),
  KEY `gcd_series_has_gallery_ec7bbed4` (`has_gallery`),
  KEY `gcd_series_deleted_659dd6eb` (`deleted`),
  KEY `gcd_series_modified_0320e1a0` (`modified`),
  CONSTRAINT `gcd_series_country_id_82a3fe9e_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `gcd_series_first_issue_id_46e8a82c_fk_gcd_issue_id` FOREIGN KEY (`first_issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `gcd_series_language_id_69197ee7_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `gcd_series_last_issue_id_8c2b6b93_fk_gcd_issue_id` FOREIGN KEY (`last_issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `gcd_series_publication_type_id_cf4742f1_fk_gcd_serie` FOREIGN KEY (`publication_type_id`) REFERENCES `gcd_series_publication_type` (`id`),
  CONSTRAINT `gcd_series_publisher_id_6389ecaa_fk_gcd_publisher_id` FOREIGN KEY (`publisher_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_series` WRITE;
/*!40000 ALTER TABLE `gcd_series` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_series` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_series_bond`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_series_bond` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserved` tinyint(1) NOT NULL,
  `bond_type_id` int NOT NULL,
  `origin_id` int NOT NULL,
  `origin_issue_id` int DEFAULT NULL,
  `target_id` int NOT NULL,
  `target_issue_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_series_bond_bond_type_id_9c9fad2d_fk_gcd_series_bond_type_id` (`bond_type_id`),
  KEY `gcd_series_bond_origin_id_f3688880_fk_gcd_series_id` (`origin_id`),
  KEY `gcd_series_bond_origin_issue_id_5d6157ba_fk_gcd_issue_id` (`origin_issue_id`),
  KEY `gcd_series_bond_target_id_65035c9e_fk_gcd_series_id` (`target_id`),
  KEY `gcd_series_bond_target_issue_id_163f94c4_fk_gcd_issue_id` (`target_issue_id`),
  KEY `gcd_series_bond_reserved_cad72d5d` (`reserved`),
  CONSTRAINT `gcd_series_bond_bond_type_id_9c9fad2d_fk_gcd_series_bond_type_id` FOREIGN KEY (`bond_type_id`) REFERENCES `gcd_series_bond_type` (`id`),
  CONSTRAINT `gcd_series_bond_origin_id_f3688880_fk_gcd_series_id` FOREIGN KEY (`origin_id`) REFERENCES `gcd_series` (`id`),
  CONSTRAINT `gcd_series_bond_origin_issue_id_5d6157ba_fk_gcd_issue_id` FOREIGN KEY (`origin_issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `gcd_series_bond_target_id_65035c9e_fk_gcd_series_id` FOREIGN KEY (`target_id`) REFERENCES `gcd_series` (`id`),
  CONSTRAINT `gcd_series_bond_target_issue_id_163f94c4_fk_gcd_issue_id` FOREIGN KEY (`target_issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_series_bond` WRITE;
/*!40000 ALTER TABLE `gcd_series_bond` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_series_bond` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_series_bond_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_series_bond_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_series_bond_type_name_950408fa` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_series_bond_type` WRITE;
/*!40000 ALTER TABLE `gcd_series_bond_type` DISABLE KEYS */;
INSERT INTO `gcd_series_bond_type` VALUES (1,'minor_name_numbering_continues','Tracks numbering from one series to another due to minor name changes.','Minor name changes include for example adding or dropping of leading articles.'),(2,'major_name_numbering_continues','Tracks numbering from one series to another due to major name changes.',''),(3,'publisher_numbering_continues','Tracks numbering from one series to another due to publisher changes.',''),(4,'subnumbering_continues','Tracks subnumbering from one series to another.',''),(5,'merge_numbering_continues','Tracks merging of one series into another with continued numbering.',''),(6,'merge','Tracks merging of one series into another.','');
/*!40000 ALTER TABLE `gcd_series_bond_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_series_external_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_series_external_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `series_id` int NOT NULL,
  `externallink_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_series_external_link_series_id_externallink_id_1f963b17_uniq` (`series_id`,`externallink_id`),
  KEY `gcd_series_external__externallink_id_45531a86_fk_gcd_exter` (`externallink_id`),
  CONSTRAINT `gcd_series_external__externallink_id_45531a86_fk_gcd_exter` FOREIGN KEY (`externallink_id`) REFERENCES `gcd_external_link` (`id`),
  CONSTRAINT `gcd_series_external_link_series_id_cffe877c_fk_gcd_series_id` FOREIGN KEY (`series_id`) REFERENCES `gcd_series` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_series_external_link` WRITE;
/*!40000 ALTER TABLE `gcd_series_external_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_series_external_link` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_series_publication_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_series_publication_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_series_publication_type_name_1027360b` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_series_publication_type` WRITE;
/*!40000 ALTER TABLE `gcd_series_publication_type` DISABLE KEYS */;
INSERT INTO `gcd_series_publication_type` VALUES (1,'book',''),(2,'magazine',''),(3,'album','');
/*!40000 ALTER TABLE `gcd_series_publication_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_source_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_source_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_source_type` WRITE;
/*!40000 ALTER TABLE `gcd_source_type` DISABLE KEYS */;
INSERT INTO `gcd_source_type` VALUES (1,'Book citation'),(2,'Comic credit'),(3,'Comic signature'),(4,'Creator questionnaire'),(5,'Creator\'s records'),(6,'Internet citation'),(7,'Interview'),(8,'Legal document'),(9,'News citation'),(10,'Publisher\'s records');
/*!40000 ALTER TABLE `gcd_source_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_inferred` tinyint(1) NOT NULL,
  `feature` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sequence_number` int NOT NULL,
  `page_count` decimal(10,3) DEFAULT NULL,
  `page_count_uncertain` tinyint(1) NOT NULL,
  `script` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `pencils` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `inks` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `colors` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `letters` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `editing` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_script` tinyint(1) NOT NULL,
  `no_pencils` tinyint(1) NOT NULL,
  `no_inks` tinyint(1) NOT NULL,
  `no_colors` tinyint(1) NOT NULL,
  `no_letters` tinyint(1) NOT NULL,
  `no_editing` tinyint(1) NOT NULL,
  `job_number` varchar(25) COLLATE utf8mb4_unicode_ci NOT NULL,
  `genre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `characters` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `synopsis` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `reprint_notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `issue_id` int NOT NULL,
  `type_id` int NOT NULL,
  `first_line` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_story_type_id_d7671a75_fk_gcd_story_type_id` (`type_id`),
  KEY `gcd_story_issue_id_95155bf9_fk_gcd_issue_id` (`issue_id`),
  KEY `gcd_story_title_inferred_31ab008d` (`title_inferred`),
  KEY `gcd_story_page_count_e179a608` (`page_count`),
  KEY `gcd_story_page_count_uncertain_d57e5c11` (`page_count_uncertain`),
  KEY `gcd_story_no_script_9f675407` (`no_script`),
  KEY `gcd_story_no_pencils_1ae49b3c` (`no_pencils`),
  KEY `gcd_story_no_inks_1abc766f` (`no_inks`),
  KEY `gcd_story_no_colors_aa4b9abb` (`no_colors`),
  KEY `gcd_story_no_letters_618bebdd` (`no_letters`),
  KEY `gcd_story_no_editing_04a6465a` (`no_editing`),
  KEY `gcd_story_modified_6ffd66a4` (`modified`),
  KEY `gcd_story_deleted_65abba08` (`deleted`),
  CONSTRAINT `gcd_story_issue_id_95155bf9_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `gcd_story_type_id_d7671a75_fk_gcd_story_type_id` FOREIGN KEY (`type_id`) REFERENCES `gcd_story_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story` WRITE;
/*!40000 ALTER TABLE `gcd_story` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_arc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_arc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `language_id` int NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_story_arc_language_id_4880d4a7_fk_stddata_language_id` (`language_id`),
  KEY `gcd_story_arc_modified_dbc41fc0` (`modified`),
  KEY `gcd_story_arc_deleted_dee7a24f` (`deleted`),
  KEY `gcd_story_arc_name_11760466` (`name`),
  KEY `gcd_story_arc_sort_name_6629f123` (`sort_name`),
  KEY `gcd_story_arc_disambiguation_05e48bc1` (`disambiguation`),
  KEY `gcd_story_arc_year_first_published_657ebbdd` (`year_first_published`),
  CONSTRAINT `gcd_story_arc_language_id_4880d4a7_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_arc` WRITE;
/*!40000 ALTER TABLE `gcd_story_arc` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_arc` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_arc_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_arc_relation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_story_arc_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `to_story_arc_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_story_arc_relati_from_story_arc_id_54a3fed9_fk_gcd_story` (`from_story_arc_id`),
  KEY `gcd_story_arc_relati_relation_type_id_fe1e25d8_fk_gcd_story` (`relation_type_id`),
  KEY `gcd_story_arc_relati_to_story_arc_id_5f72f57a_fk_gcd_story` (`to_story_arc_id`),
  KEY `gcd_story_arc_relation_modified_93e610ac` (`modified`),
  CONSTRAINT `gcd_story_arc_relati_from_story_arc_id_54a3fed9_fk_gcd_story` FOREIGN KEY (`from_story_arc_id`) REFERENCES `gcd_story_arc` (`id`),
  CONSTRAINT `gcd_story_arc_relati_relation_type_id_fe1e25d8_fk_gcd_story` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_story_arc_relation_type` (`id`),
  CONSTRAINT `gcd_story_arc_relati_to_story_arc_id_5f72f57a_fk_gcd_story` FOREIGN KEY (`to_story_arc_id`) REFERENCES `gcd_story_arc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_arc_relation` WRITE;
/*!40000 ALTER TABLE `gcd_story_arc_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_arc_relation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_arc_relation_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_arc_relation_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reverse_description` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_story_arc_relation_type_name_371b563b` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_arc_relation_type` WRITE;
/*!40000 ALTER TABLE `gcd_story_arc_relation_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_arc_relation_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_character` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `is_flashback` tinyint(1) NOT NULL,
  `is_origin` tinyint(1) NOT NULL,
  `is_death` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `character_id` int NOT NULL,
  `role_id` int DEFAULT NULL,
  `story_id` int NOT NULL,
  `universe_id` int DEFAULT NULL,
  `group_universe_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_story_character_character_id_eac50f28_fk_gcd_chara` (`character_id`),
  KEY `gcd_story_character_role_id_f7883e66_fk_gcd_character_role_id` (`role_id`),
  KEY `gcd_story_character_story_id_13ce6388_fk_gcd_story_id` (`story_id`),
  KEY `gcd_story_character_modified_6f623117` (`modified`),
  KEY `gcd_story_character_deleted_5b1dd00b` (`deleted`),
  KEY `gcd_story_character_is_flashback_3898577a` (`is_flashback`),
  KEY `gcd_story_character_is_origin_17b5e411` (`is_origin`),
  KEY `gcd_story_character_is_death_a3861547` (`is_death`),
  KEY `gcd_story_character_universe_id_a98c97a2_fk_gcd_universe_id` (`universe_id`),
  KEY `gcd_story_character_group_universe_id_1660ef69_fk_gcd_unive` (`group_universe_id`),
  CONSTRAINT `gcd_story_character_character_id_eac50f28_fk_gcd_chara` FOREIGN KEY (`character_id`) REFERENCES `gcd_character_name_detail` (`id`),
  CONSTRAINT `gcd_story_character_group_universe_id_1660ef69_fk_gcd_unive` FOREIGN KEY (`group_universe_id`) REFERENCES `gcd_universe` (`id`),
  CONSTRAINT `gcd_story_character_role_id_f7883e66_fk_gcd_character_role_id` FOREIGN KEY (`role_id`) REFERENCES `gcd_character_role` (`id`),
  CONSTRAINT `gcd_story_character_story_id_13ce6388_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `gcd_story_character_universe_id_a98c97a2_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_character` WRITE;
/*!40000 ALTER TABLE `gcd_story_character` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_character` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_character_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_character_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storycharacter_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_story_character_grou_storycharacter_id_group__630fc99e_uniq` (`storycharacter_id`,`group_id`),
  KEY `gcd_story_character_group_group_id_191387e6_fk_gcd_group_id` (`group_id`),
  CONSTRAINT `gcd_story_character__storycharacter_id_1cab539d_fk_gcd_story` FOREIGN KEY (`storycharacter_id`) REFERENCES `gcd_story_character` (`id`),
  CONSTRAINT `gcd_story_character_group_group_id_191387e6_fk_gcd_group_id` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_character_group` WRITE;
/*!40000 ALTER TABLE `gcd_story_character_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_character_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_character_group_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_character_group_name` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storycharacter_id` int NOT NULL,
  `groupnamedetail_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_story_character_grou_storycharacter_id_groupn_ad2e39b0_uniq` (`storycharacter_id`,`groupnamedetail_id`),
  KEY `gcd_story_character__groupnamedetail_id_cd88e5c1_fk_gcd_group` (`groupnamedetail_id`),
  CONSTRAINT `gcd_story_character__groupnamedetail_id_cd88e5c1_fk_gcd_group` FOREIGN KEY (`groupnamedetail_id`) REFERENCES `gcd_group_name_detail` (`id`),
  CONSTRAINT `gcd_story_character__storycharacter_id_8c6a614f_fk_gcd_story` FOREIGN KEY (`storycharacter_id`) REFERENCES `gcd_story_character` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_character_group_name` WRITE;
/*!40000 ALTER TABLE `gcd_story_character_group_name` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_character_group_name` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_credit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_credit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `is_credited` tinyint(1) NOT NULL,
  `is_signed` tinyint(1) NOT NULL,
  `uncertain` tinyint(1) NOT NULL,
  `signed_as` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credited_as` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credit_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `creator_id` int NOT NULL,
  `credit_type_id` int NOT NULL,
  `story_id` int NOT NULL,
  `signature_id` int DEFAULT NULL,
  `is_sourced` tinyint(1) NOT NULL,
  `sourced_by` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_story_credit_creator_id_7c632a78_fk_gcd_creat` (`creator_id`),
  KEY `gcd_story_credit_credit_type_id_2b1eda8a_fk_gcd_credit_type_id` (`credit_type_id`),
  KEY `gcd_story_credit_story_id_7b35c2b5_fk_gcd_story_id` (`story_id`),
  KEY `gcd_story_credit_modified_1b831920` (`modified`),
  KEY `gcd_story_credit_deleted_5f31a0d2` (`deleted`),
  KEY `gcd_story_credit_is_credited_a0f3090d` (`is_credited`),
  KEY `gcd_story_credit_is_signed_da26e307` (`is_signed`),
  KEY `gcd_story_credit_uncertain_1a69a71c` (`uncertain`),
  KEY `gcd_story_credit_signature_id_0c4a25cd_fk_gcd_creat` (`signature_id`),
  KEY `gcd_story_credit_is_sourced_b8200d3b` (`is_sourced`),
  CONSTRAINT `gcd_story_credit_creator_id_7c632a78_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator_name_detail` (`id`),
  CONSTRAINT `gcd_story_credit_credit_type_id_2b1eda8a_fk_gcd_credit_type_id` FOREIGN KEY (`credit_type_id`) REFERENCES `gcd_credit_type` (`id`),
  CONSTRAINT `gcd_story_credit_signature_id_0c4a25cd_fk_gcd_creat` FOREIGN KEY (`signature_id`) REFERENCES `gcd_creator_signature` (`id`),
  CONSTRAINT `gcd_story_credit_story_id_7b35c2b5_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_credit` WRITE;
/*!40000 ALTER TABLE `gcd_story_credit` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_credit` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_feature_logo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_feature_logo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `story_id` int NOT NULL,
  `featurelogo_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_story_feature_logo_story_id_featurelogo_id_5a345f8c_uniq` (`story_id`,`featurelogo_id`),
  KEY `gcd_story_feature_lo_featurelogo_id_169a1ec3_fk_gcd_featu` (`featurelogo_id`),
  CONSTRAINT `gcd_story_feature_lo_featurelogo_id_169a1ec3_fk_gcd_featu` FOREIGN KEY (`featurelogo_id`) REFERENCES `gcd_feature_logo` (`id`),
  CONSTRAINT `gcd_story_feature_logo_story_id_41377b84_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_feature_logo` WRITE;
/*!40000 ALTER TABLE `gcd_story_feature_logo` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_feature_logo` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_feature_object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_feature_object` (
  `id` int NOT NULL AUTO_INCREMENT,
  `story_id` int NOT NULL,
  `feature_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_story_feature_object_story_id_feature_id_e2de9a4d_uniq` (`story_id`,`feature_id`),
  KEY `gcd_story_feature_object_feature_id_fea4dbf9_fk_gcd_feature_id` (`feature_id`),
  CONSTRAINT `gcd_story_feature_object_feature_id_fea4dbf9_fk_gcd_feature_id` FOREIGN KEY (`feature_id`) REFERENCES `gcd_feature` (`id`),
  CONSTRAINT `gcd_story_feature_object_story_id_0393a434_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_feature_object` WRITE;
/*!40000 ALTER TABLE `gcd_story_feature_object` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_feature_object` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_story_arc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_story_arc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `story_id` int NOT NULL,
  `storyarc_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_story_story_arc_story_id_storyarc_id_f9adf1b5_uniq` (`story_id`,`storyarc_id`),
  KEY `gcd_story_story_arc_storyarc_id_4b052401_fk_gcd_story_arc_id` (`storyarc_id`),
  CONSTRAINT `gcd_story_story_arc_story_id_406c134b_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `gcd_story_story_arc_storyarc_id_4b052401_fk_gcd_story_arc_id` FOREIGN KEY (`storyarc_id`) REFERENCES `gcd_story_arc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_story_arc` WRITE;
/*!40000 ALTER TABLE `gcd_story_story_arc` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_story_arc` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_code` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `sort_code` (`sort_code`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_type` WRITE;
/*!40000 ALTER TABLE `gcd_story_type` DISABLE KEYS */;
INSERT INTO `gcd_story_type` VALUES (1,'activity',24),(2,'advertisement',21),(3,'(backcovers) *do not use* / *please fix*',500),(4,'biography (nonfictional)',502),(5,'cartoon',7),(6,'cover',5),(7,'cover reprint (on interior page)',6),(8,'credits, title page',43),(9,'filler',47),(10,'foreword, introduction, preface, afterword',42),(11,'insert or dust jacket',46),(12,'letters page',45),(13,'photo story',4),(14,'illustration',8),(15,'character profile',40),(16,'promo (ad from the publisher)',22),(17,'public service announcement',29),(18,'recap',44),(19,'comic story',1),(20,'text article',3),(21,'text story',2),(22,'statement of ownership',41),(23,'(unknown)',501),(24,'blank page(s)',235),(25,'table of contents',165),(26,'preview (from the publisher)',23),(27,'about comics',60),(28,'comics-form advertising',20),(29,'in-house column',25);
/*!40000 ALTER TABLE `gcd_story_type` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_story_universe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_story_universe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `story_id` int NOT NULL,
  `universe_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gcd_story_universe_story_id_universe_id_3a74cf57_uniq` (`story_id`,`universe_id`),
  KEY `gcd_story_universe_universe_id_d3185012_fk_gcd_universe_id` (`universe_id`),
  CONSTRAINT `gcd_story_universe_story_id_6cbde435_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `gcd_story_universe_universe_id_d3185012_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_story_universe` WRITE;
/*!40000 ALTER TABLE `gcd_story_universe` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_story_universe` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `gcd_universe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gcd_universe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `multiverse` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `designation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `verse_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gcd_universe_modified_c5d3bbeb` (`modified`),
  KEY `gcd_universe_deleted_ff60af35` (`deleted`),
  KEY `gcd_universe_multiverse_33bbb4b5` (`multiverse`),
  KEY `gcd_universe_name_6d727a81` (`name`),
  KEY `gcd_universe_designation_c44a1a75` (`designation`),
  KEY `gcd_universe_year_first_published_deedfad5` (`year_first_published`),
  KEY `gcd_universe_verse_id_b2ae21fa_fk_gcd_multiverse_id` (`verse_id`),
  CONSTRAINT `gcd_universe_verse_id_b2ae21fa_fk_gcd_multiverse_id` FOREIGN KEY (`verse_id`) REFERENCES `gcd_multiverse` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `gcd_universe` WRITE;
/*!40000 ALTER TABLE `gcd_universe` DISABLE KEYS */;
/*!40000 ALTER TABLE `gcd_universe` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `indexer_error`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `indexer_error` (
  `error_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_text` longtext COLLATE utf8mb4_unicode_ci,
  `is_safe` tinyint(1) NOT NULL,
  PRIMARY KEY (`error_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `indexer_error` WRITE;
/*!40000 ALTER TABLE `indexer_error` DISABLE KEYS */;
/*!40000 ALTER TABLE `indexer_error` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `indexer_imp_grant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `indexer_imp_grant` (
  `id` int NOT NULL AUTO_INCREMENT,
  `imps` int NOT NULL,
  `grant_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `indexer_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `indexer_imp_grant_indexer_id_b0f7fede_fk_indexer_indexer_id` (`indexer_id`),
  CONSTRAINT `indexer_imp_grant_indexer_id_b0f7fede_fk_indexer_indexer_id` FOREIGN KEY (`indexer_id`) REFERENCES `indexer_indexer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `indexer_imp_grant` WRITE;
/*!40000 ALTER TABLE `indexer_imp_grant` DISABLE KEYS */;
/*!40000 ALTER TABLE `indexer_imp_grant` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `indexer_indexer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `indexer_indexer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `interests` longtext COLLATE utf8mb4_unicode_ci,
  `opt_in_email` tinyint(1) NOT NULL,
  `from_where` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `max_reservations` int NOT NULL,
  `max_ongoing` int NOT NULL,
  `is_new` tinyint(1) NOT NULL,
  `is_banned` tinyint(1) NOT NULL,
  `deceased` tinyint(1) NOT NULL,
  `registration_key` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `registration_expires` date DEFAULT NULL,
  `imps` int NOT NULL,
  `issue_detail` int NOT NULL,
  `notify_on_approve` tinyint(1) NOT NULL,
  `collapse_compare_view` tinyint(1) NOT NULL,
  `show_wiki_links` tinyint(1) NOT NULL,
  `country_id` int NOT NULL,
  `mentor_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  `seen_privacy_policy` tinyint(1) NOT NULL,
  `cover_letterer_creator_only` tinyint(1) NOT NULL,
  `use_tabs` tinyint(1) NOT NULL,
  `reprint_threshold` int NOT NULL,
  `variant_threshold` int NOT NULL,
  `cache_size` int NOT NULL,
  `items_per_page` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `indexer_indexer_country_id_c0581bfc_fk_stddata_country_id` (`country_id`),
  KEY `indexer_indexer_mentor_id_327fdd5e_fk_auth_user_id` (`mentor_id`),
  KEY `indexer_indexer_opt_in_email_ff60dff7` (`opt_in_email`),
  KEY `indexer_indexer_is_new_986db9d7` (`is_new`),
  KEY `indexer_indexer_is_banned_85e42292` (`is_banned`),
  KEY `indexer_indexer_deceased_54e9ec6a` (`deceased`),
  KEY `indexer_indexer_registration_key_16331a46` (`registration_key`),
  KEY `indexer_indexer_registration_expires_fed55199` (`registration_expires`),
  KEY `indexer_indexer_notify_on_approve_d7439dc7` (`notify_on_approve`),
  KEY `indexer_indexer_collapse_compare_view_3cd2d49c` (`collapse_compare_view`),
  KEY `indexer_indexer_show_wiki_links_d63128d6` (`show_wiki_links`),
  KEY `indexer_indexer_seen_privacy_policy_7751cd92` (`seen_privacy_policy`),
  KEY `indexer_indexer_use_tabs_161de20c` (`use_tabs`),
  CONSTRAINT `indexer_indexer_country_id_c0581bfc_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `indexer_indexer_mentor_id_327fdd5e_fk_auth_user_id` FOREIGN KEY (`mentor_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `indexer_indexer_user_id_6950082c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `indexer_indexer` WRITE;
/*!40000 ALTER TABLE `indexer_indexer` DISABLE KEYS */;
/*!40000 ALTER TABLE `indexer_indexer` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `legacy_migration_story_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legacy_migration_story_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reprint_needs_inspection` tinyint(1) NOT NULL,
  `reprint_confirmed` tinyint(1) NOT NULL,
  `reprint_original_notes` longtext COLLATE utf8mb4_unicode_ci,
  `modified` datetime(6) NOT NULL,
  `story_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `story_id` (`story_id`),
  KEY `legacy_migration_story_status_reprint_needs_inspection_aeb0c890` (`reprint_needs_inspection`),
  KEY `legacy_migration_story_status_reprint_confirmed_e26505f1` (`reprint_confirmed`),
  CONSTRAINT `legacy_migration_story_status_story_id_8de3a871_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `legacy_migration_story_status` WRITE;
/*!40000 ALTER TABLE `legacy_migration_story_status` DISABLE KEYS */;
/*!40000 ALTER TABLE `legacy_migration_story_status` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `legacy_reservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legacy_reservation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` int NOT NULL,
  `expires` date DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `indexer_id` int NOT NULL,
  `issue_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `legacy_reservation_indexer_id_0e64de75_fk_indexer_indexer_id` (`indexer_id`),
  KEY `legacy_reservation_issue_id_bb3749d9_fk_gcd_issue_id` (`issue_id`),
  KEY `legacy_reservation_status_b49cc285` (`status`),
  CONSTRAINT `legacy_reservation_indexer_id_0e64de75_fk_indexer_indexer_id` FOREIGN KEY (`indexer_id`) REFERENCES `indexer_indexer` (`id`),
  CONSTRAINT `legacy_reservation_issue_id_bb3749d9_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `legacy_reservation` WRITE;
/*!40000 ALTER TABLE `legacy_reservation` DISABLE KEYS */;
/*!40000 ALTER TABLE `legacy_reservation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `legacy_series_indexers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legacy_series_indexers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `run` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci,
  `modified` datetime(6) NOT NULL,
  `indexer_id` int NOT NULL,
  `series_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `legacy_series_indexers_indexer_id_5b06ad9b_fk_indexer_indexer_id` (`indexer_id`),
  KEY `legacy_series_indexers_series_id_6bee0ea6_fk_gcd_series_id` (`series_id`),
  CONSTRAINT `legacy_series_indexers_indexer_id_5b06ad9b_fk_indexer_indexer_id` FOREIGN KEY (`indexer_id`) REFERENCES `indexer_indexer` (`id`),
  CONSTRAINT `legacy_series_indexers_series_id_6bee0ea6_fk_gcd_series_id` FOREIGN KEY (`series_id`) REFERENCES `gcd_series` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `legacy_series_indexers` WRITE;
/*!40000 ALTER TABLE `legacy_series_indexers` DISABLE KEYS */;
/*!40000 ALTER TABLE `legacy_series_indexers` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_collection` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `public` tinyint(1) NOT NULL,
  `condition_used` tinyint(1) NOT NULL,
  `acquisition_date_used` tinyint(1) NOT NULL,
  `sell_date_used` tinyint(1) NOT NULL,
  `location_used` tinyint(1) NOT NULL,
  `purchase_location_used` tinyint(1) NOT NULL,
  `own_used` tinyint(1) NOT NULL,
  `own_default` tinyint(1) DEFAULT NULL,
  `was_read_used` tinyint(1) NOT NULL,
  `for_sale_used` tinyint(1) NOT NULL,
  `signed_used` tinyint(1) NOT NULL,
  `price_paid_used` tinyint(1) NOT NULL,
  `market_value_used` tinyint(1) NOT NULL,
  `sell_price_used` tinyint(1) NOT NULL,
  `collector_id` int NOT NULL,
  `digital_used` tinyint(1) NOT NULL,
  `rating_used` tinyint(1) NOT NULL,
  `for_sale_default` tinyint(1) NOT NULL,
  `location_default_id` int DEFAULT NULL,
  `purchase_location_default_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_collection_collector_id_fedbd922_fk_mycomics_` (`collector_id`),
  KEY `mycomics_collection_name_3781fbcb` (`name`),
  KEY `mycomics_collection_location_default_id_a0a5ee8c_fk_mycomics_` (`location_default_id`),
  KEY `mycomics_collection_purchase_location_de_540eea6e_fk_mycomics_` (`purchase_location_default_id`),
  CONSTRAINT `mycomics_collection_collector_id_fedbd922_fk_mycomics_` FOREIGN KEY (`collector_id`) REFERENCES `mycomics_collector` (`id`),
  CONSTRAINT `mycomics_collection_location_default_id_a0a5ee8c_fk_mycomics_` FOREIGN KEY (`location_default_id`) REFERENCES `mycomics_location` (`id`),
  CONSTRAINT `mycomics_collection_purchase_location_de_540eea6e_fk_mycomics_` FOREIGN KEY (`purchase_location_default_id`) REFERENCES `mycomics_purchase_location` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_collection` WRITE;
/*!40000 ALTER TABLE `mycomics_collection` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_collection` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_collection_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_collection_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `own` tinyint(1) DEFAULT NULL,
  `was_read` tinyint(1) DEFAULT NULL,
  `for_sale` tinyint(1) NOT NULL,
  `signed` tinyint(1) NOT NULL,
  `price_paid` decimal(10,2) DEFAULT NULL,
  `market_value` decimal(10,2) DEFAULT NULL,
  `sell_price` decimal(10,2) DEFAULT NULL,
  `acquisition_date_id` int DEFAULT NULL,
  `grade_id` int DEFAULT NULL,
  `issue_id` int NOT NULL,
  `location_id` int DEFAULT NULL,
  `market_value_currency_id` int DEFAULT NULL,
  `price_paid_currency_id` int DEFAULT NULL,
  `purchase_location_id` int DEFAULT NULL,
  `sell_date_id` int DEFAULT NULL,
  `sell_price_currency_id` int DEFAULT NULL,
  `is_digital` tinyint(1) NOT NULL,
  `rating` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_collection__grade_id_e9bbe307_fk_mycomics_` (`grade_id`),
  KEY `mycomics_collection_item_issue_id_9e72f0d8_fk_gcd_issue_id` (`issue_id`),
  KEY `mycomics_collection__location_id_b76c3a2e_fk_mycomics_` (`location_id`),
  KEY `mycomics_collection__market_value_currenc_5a5d3ba9_fk_stddata_c` (`market_value_currency_id`),
  KEY `mycomics_collection__price_paid_currency__9f84dd40_fk_stddata_c` (`price_paid_currency_id`),
  KEY `mycomics_collection__purchase_location_id_e6dba5e0_fk_mycomics_` (`purchase_location_id`),
  KEY `mycomics_collection__sell_date_id_84c117e9_fk_stddata_d` (`sell_date_id`),
  KEY `mycomics_collection__sell_price_currency__601674ac_fk_stddata_c` (`sell_price_currency_id`),
  KEY `mycomics_collection__acquisition_date_id_1d006790_fk_stddata_d` (`acquisition_date_id`),
  CONSTRAINT `mycomics_collection__acquisition_date_id_1d006790_fk_stddata_d` FOREIGN KEY (`acquisition_date_id`) REFERENCES `stddata_date` (`id`),
  CONSTRAINT `mycomics_collection__grade_id_e9bbe307_fk_mycomics_` FOREIGN KEY (`grade_id`) REFERENCES `mycomics_condition_grade` (`id`),
  CONSTRAINT `mycomics_collection__location_id_b76c3a2e_fk_mycomics_` FOREIGN KEY (`location_id`) REFERENCES `mycomics_location` (`id`),
  CONSTRAINT `mycomics_collection__market_value_currenc_5a5d3ba9_fk_stddata_c` FOREIGN KEY (`market_value_currency_id`) REFERENCES `stddata_currency` (`id`),
  CONSTRAINT `mycomics_collection__price_paid_currency__9f84dd40_fk_stddata_c` FOREIGN KEY (`price_paid_currency_id`) REFERENCES `stddata_currency` (`id`),
  CONSTRAINT `mycomics_collection__purchase_location_id_e6dba5e0_fk_mycomics_` FOREIGN KEY (`purchase_location_id`) REFERENCES `mycomics_purchase_location` (`id`),
  CONSTRAINT `mycomics_collection__sell_date_id_84c117e9_fk_stddata_d` FOREIGN KEY (`sell_date_id`) REFERENCES `stddata_date` (`id`),
  CONSTRAINT `mycomics_collection__sell_price_currency__601674ac_fk_stddata_c` FOREIGN KEY (`sell_price_currency_id`) REFERENCES `stddata_currency` (`id`),
  CONSTRAINT `mycomics_collection_item_issue_id_9e72f0d8_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_collection_item` WRITE;
/*!40000 ALTER TABLE `mycomics_collection_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_collection_item` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_collection_item_collections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_collection_item_collections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `collectionitem_id` int NOT NULL,
  `collection_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mycomics_collection_item_collectionitem_id_collec_b444e41b_uniq` (`collectionitem_id`,`collection_id`),
  KEY `mycomics_collection__collection_id_0adb8b74_fk_mycomics_` (`collection_id`),
  CONSTRAINT `mycomics_collection__collection_id_0adb8b74_fk_mycomics_` FOREIGN KEY (`collection_id`) REFERENCES `mycomics_collection` (`id`),
  CONSTRAINT `mycomics_collection__collectionitem_id_b3c335ae_fk_mycomics_` FOREIGN KEY (`collectionitem_id`) REFERENCES `mycomics_collection_item` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_collection_item_collections` WRITE;
/*!40000 ALTER TABLE `mycomics_collection_item_collections` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_collection_item_collections` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_collector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_collector` (
  `id` int NOT NULL AUTO_INCREMENT,
  `default_currency_id` int DEFAULT NULL,
  `default_have_collection_id` int DEFAULT NULL,
  `default_language_id` int NOT NULL,
  `default_want_collection_id` int DEFAULT NULL,
  `grade_system_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `mycomics_collector_grade_system_id_8f179956_fk_mycomics_` (`grade_system_id`),
  KEY `mycomics_collector_default_currency_id_f390b262_fk_stddata_c` (`default_currency_id`),
  KEY `mycomics_collector_default_have_collect_5b03c6c4_fk_mycomics_` (`default_have_collection_id`),
  KEY `mycomics_collector_default_language_id_ca71a5f3_fk_stddata_l` (`default_language_id`),
  KEY `mycomics_collector_default_want_collect_da26c741_fk_mycomics_` (`default_want_collection_id`),
  CONSTRAINT `mycomics_collector_default_currency_id_f390b262_fk_stddata_c` FOREIGN KEY (`default_currency_id`) REFERENCES `stddata_currency` (`id`),
  CONSTRAINT `mycomics_collector_default_have_collect_5b03c6c4_fk_mycomics_` FOREIGN KEY (`default_have_collection_id`) REFERENCES `mycomics_collection` (`id`),
  CONSTRAINT `mycomics_collector_default_language_id_ca71a5f3_fk_stddata_l` FOREIGN KEY (`default_language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `mycomics_collector_default_want_collect_da26c741_fk_mycomics_` FOREIGN KEY (`default_want_collection_id`) REFERENCES `mycomics_collection` (`id`),
  CONSTRAINT `mycomics_collector_grade_system_id_8f179956_fk_mycomics_` FOREIGN KEY (`grade_system_id`) REFERENCES `mycomics_condition_grade_scale` (`id`),
  CONSTRAINT `mycomics_collector_user_id_f4b8f4a7_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_collector` WRITE;
/*!40000 ALTER TABLE `mycomics_collector` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_collector` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_condition_grade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_condition_grade` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `scale_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_condition_g_scale_id_723bc3a9_fk_mycomics_` (`scale_id`),
  CONSTRAINT `mycomics_condition_g_scale_id_723bc3a9_fk_mycomics_` FOREIGN KEY (`scale_id`) REFERENCES `mycomics_condition_grade_scale` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_condition_grade` WRITE;
/*!40000 ALTER TABLE `mycomics_condition_grade` DISABLE KEYS */;
INSERT INTO `mycomics_condition_grade` VALUES (1,'NM','Near Mint',8,1),(2,'VF','Very Fine',7,1),(3,'FN','Fine',6,1),(4,'FG','Very Good',5,1),(5,'GD','Good',4,1),(6,'FR','Fair',3,1),(7,'PR','Poor',2,1),(8,'GM','Gem Mint',10,2),(9,'M','Mint',9.9,2),(10,'NM/M','Near Mint/Mint',9.8,2),(11,'NM+','Near Mint+',9.6,2),(12,'NM','Near Mint',9.4,2),(13,'NM-','Near Mint-',9.2,2),(14,'VF/NM','Very Fine/Near Mint',9,2),(15,'VF+','Very Fine+',8.5,2),(16,'VF','Very Fine',8,2),(17,'VF-vVery Fine-','',7.5,2),(18,'FN/VF','Fine/Very Fine',7,2),(19,'FN+','Fine+',6.5,2),(20,'FN','Fine',6,2),(21,'FN-','Fine-',5.5,2),(22,'VG/FN','Very Good/Fine',5,2),(23,'VG+','Very Good+',4.5,2),(24,'VG','Very Good',4,2),(25,'VG-','Very Good-',3.5,2),(26,'GD/VG','Good/Very Good',3,2),(27,'GD+vGood+','',2.5,2),(28,'GD','Good',2,2),(29,'GD-','Good-',1.8,2),(30,'FR/GD','Fair/Good',1.5,2),(31,'FR','Fair',1,2),(32,'PR','Poor',0.5,2),(33,'Zustand 0','perfekt',10,3),(34,'Zustand 0-1','fast perfekt',9,3),(35,'Zustand 1','sehr gut',8,3),(36,'Zustand 1-2','fast sehr gut',7,3),(37,'Zustand 2','gut',6,3),(38,'Zustand 2-3','noch recht gut',5,3),(39,'Zustand 3','noch sammelwürdig',4,3),(40,'Zustand 3-4','schlecht',3,3),(41,'Zustand 4','zum Wegwerfen zu schade',2,3),(42,'Zustand 5','unvollständig',1,3);
/*!40000 ALTER TABLE `mycomics_condition_grade` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_condition_grade_scale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_condition_grade_scale` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_condition_grade_scale` WRITE;
/*!40000 ALTER TABLE `mycomics_condition_grade_scale` DISABLE KEYS */;
INSERT INTO `mycomics_condition_grade_scale` VALUES (1,'US basic grading scale',''),(2,'US ten-point grading scale',''),(3,'German grading scale','');
/*!40000 ALTER TABLE `mycomics_condition_grade_scale` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_location` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_location_user_id_a5300c89_fk_mycomics_collector_id` (`user_id`),
  CONSTRAINT `mycomics_location_user_id_a5300c89_fk_mycomics_collector_id` FOREIGN KEY (`user_id`) REFERENCES `mycomics_collector` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_location` WRITE;
/*!40000 ALTER TABLE `mycomics_location` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_location` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_purchase_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_purchase_location` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_purchase_lo_user_id_adfa0d4b_fk_mycomics_` (`user_id`),
  CONSTRAINT `mycomics_purchase_lo_user_id_adfa0d4b_fk_mycomics_` FOREIGN KEY (`user_id`) REFERENCES `mycomics_collector` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_purchase_location` WRITE;
/*!40000 ALTER TABLE `mycomics_purchase_location` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_purchase_location` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_reading_order_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_reading_order_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sequence_number` int NOT NULL,
  `was_read` tinyint(1) DEFAULT NULL,
  `issue_id` int NOT NULL,
  `reading_order_id` int NOT NULL,
  `story_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_reading_order_item_issue_id_7dd8109a_fk_gcd_issue_id` (`issue_id`),
  KEY `mycomics_reading_ord_reading_order_id_b7c2dd51_fk_mycomics_` (`reading_order_id`),
  KEY `mycomics_reading_order_item_story_id_12bb1619_fk_gcd_story_id` (`story_id`),
  CONSTRAINT `mycomics_reading_ord_reading_order_id_b7c2dd51_fk_mycomics_` FOREIGN KEY (`reading_order_id`) REFERENCES `mycomics_readingorder` (`id`),
  CONSTRAINT `mycomics_reading_order_item_issue_id_7dd8109a_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `mycomics_reading_order_item_story_id_12bb1619_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_reading_order_item` WRITE;
/*!40000 ALTER TABLE `mycomics_reading_order_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_reading_order_item` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_readingorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_readingorder` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `public` tinyint(1) NOT NULL,
  `was_read_used` tinyint(1) NOT NULL,
  `collector_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_readingorde_collector_id_a9f1dfe0_fk_mycomics_` (`collector_id`),
  KEY `mycomics_readingorder_name_5576da7c` (`name`),
  CONSTRAINT `mycomics_readingorde_collector_id_a9f1dfe0_fk_mycomics_` FOREIGN KEY (`collector_id`) REFERENCES `mycomics_collector` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_readingorder` WRITE;
/*!40000 ALTER TABLE `mycomics_readingorder` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_readingorder` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mycomics_subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mycomics_subscription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `last_pulled` datetime(6) NOT NULL,
  `collection_id` int NOT NULL,
  `series_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mycomics_subscriptio_collection_id_c058c1de_fk_mycomics_` (`collection_id`),
  KEY `mycomics_subscription_series_id_826b7d5e_fk_gcd_series_id` (`series_id`),
  CONSTRAINT `mycomics_subscriptio_collection_id_c058c1de_fk_mycomics_` FOREIGN KEY (`collection_id`) REFERENCES `mycomics_collection` (`id`),
  CONSTRAINT `mycomics_subscription_series_id_826b7d5e_fk_gcd_series_id` FOREIGN KEY (`series_id`) REFERENCES `gcd_series` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mycomics_subscription` WRITE;
/*!40000 ALTER TABLE `mycomics_subscription` DISABLE KEYS */;
/*!40000 ALTER TABLE `mycomics_subscription` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_award_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_award_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `award_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_award_revision_award_id_10077073_fk_gcd_award_id` (`award_id`),
  KEY `oi_award_revision_changeset_id_323994d7_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_award_revision_deleted_3a33219c` (`deleted`),
  KEY `oi_award_revision_created_1095eb34` (`created`),
  KEY `oi_award_revision_modified_89af429f` (`modified`),
  KEY `oi_award_revision_committed_65c6056b` (`committed`),
  CONSTRAINT `oi_award_revision_award_id_10077073_fk_gcd_award_id` FOREIGN KEY (`award_id`) REFERENCES `gcd_award` (`id`),
  CONSTRAINT `oi_award_revision_changeset_id_323994d7_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_award_revision_previous_revision_id_a3829962_fk_oi_award_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_award_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_award_revision` WRITE;
/*!40000 ALTER TABLE `oi_award_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_award_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_biblio_entry_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_biblio_entry_revision` (
  `storyrevision_ptr_id` int NOT NULL,
  `page_began` int DEFAULT NULL,
  `page_ended` int DEFAULT NULL,
  `abstract` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `doi` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`storyrevision_ptr_id`),
  CONSTRAINT `oi_biblio_entry_revi_storyrevision_ptr_id_b066c616_fk_oi_story_` FOREIGN KEY (`storyrevision_ptr_id`) REFERENCES `oi_story_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_biblio_entry_revision` WRITE;
/*!40000 ALTER TABLE `oi_biblio_entry_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_biblio_entry_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_brand_group_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_brand_group_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `brand_group_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_brand_group_revision_changeset_id_040ac0f0_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_brand_group_revision_parent_id_0de3b5db_fk_gcd_publisher_id` (`parent_id`),
  KEY `oi_brand_group_revis_brand_group_id_6ab443ee_fk_gcd_brand` (`brand_group_id`),
  KEY `oi_brand_group_revision_deleted_5ff21d25` (`deleted`),
  KEY `oi_brand_group_revision_created_8de93479` (`created`),
  KEY `oi_brand_group_revision_modified_84f5fefa` (`modified`),
  KEY `oi_brand_group_revision_committed_2f500a67` (`committed`),
  CONSTRAINT `oi_brand_group_revis_brand_group_id_6ab443ee_fk_gcd_brand` FOREIGN KEY (`brand_group_id`) REFERENCES `gcd_brand_group` (`id`),
  CONSTRAINT `oi_brand_group_revis_previous_revision_id_b35807c0_fk_oi_brand_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_brand_group_revision` (`id`),
  CONSTRAINT `oi_brand_group_revision_changeset_id_040ac0f0_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_brand_group_revision_parent_id_0de3b5db_fk_gcd_publisher_id` FOREIGN KEY (`parent_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_brand_group_revision` WRITE;
/*!40000 ALTER TABLE `oi_brand_group_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_brand_group_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_brand_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_brand_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `brand_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  `generic` tinyint(1) NOT NULL,
  `image_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_brand_revision_changeset_id_4b9ad094_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_brand_revision_parent_id_c46e5ef9_fk_gcd_publisher_id` (`parent_id`),
  KEY `oi_brand_revision_brand_id_b04c0c1a_fk_gcd_brand_id` (`brand_id`),
  KEY `oi_brand_revision_deleted_152bce40` (`deleted`),
  KEY `oi_brand_revision_created_5e3e0cad` (`created`),
  KEY `oi_brand_revision_modified_43c3d295` (`modified`),
  KEY `oi_brand_revision_committed_86333624` (`committed`),
  KEY `oi_brand_revision_image_revision_id_2e272494_fk_oi_image_` (`image_revision_id`),
  CONSTRAINT `oi_brand_revision_brand_id_b04c0c1a_fk_gcd_brand_id` FOREIGN KEY (`brand_id`) REFERENCES `gcd_brand` (`id`),
  CONSTRAINT `oi_brand_revision_changeset_id_4b9ad094_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_brand_revision_image_revision_id_2e272494_fk_oi_image_` FOREIGN KEY (`image_revision_id`) REFERENCES `oi_image_revision` (`id`),
  CONSTRAINT `oi_brand_revision_parent_id_c46e5ef9_fk_gcd_publisher_id` FOREIGN KEY (`parent_id`) REFERENCES `gcd_publisher` (`id`),
  CONSTRAINT `oi_brand_revision_previous_revision_id_619c26bd_fk_oi_brand_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_brand_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_brand_revision` WRITE;
/*!40000 ALTER TABLE `oi_brand_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_brand_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_brand_revision_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_brand_revision_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `brandrevision_id` int NOT NULL,
  `brandgroup_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_brand_revision_group_brandrevision_id_brandgr_49713700_uniq` (`brandrevision_id`,`brandgroup_id`),
  KEY `oi_brand_revision_gr_brandgroup_id_92629254_fk_gcd_brand` (`brandgroup_id`),
  CONSTRAINT `oi_brand_revision_gr_brandgroup_id_92629254_fk_gcd_brand` FOREIGN KEY (`brandgroup_id`) REFERENCES `gcd_brand_group` (`id`),
  CONSTRAINT `oi_brand_revision_gr_brandrevision_id_05443808_fk_oi_brand_` FOREIGN KEY (`brandrevision_id`) REFERENCES `oi_brand_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_brand_revision_group` WRITE;
/*!40000 ALTER TABLE `oi_brand_revision_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_brand_revision_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_brand_use_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_brand_use_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `brand_use_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `emblem_id` int DEFAULT NULL,
  `publisher_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_brand_use_revision_changeset_id_b9e8a6fe_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_brand_use_revision_emblem_id_ed990457_fk_gcd_brand_id` (`emblem_id`),
  KEY `oi_brand_use_revision_publisher_id_277730e8_fk_gcd_publisher_id` (`publisher_id`),
  KEY `oi_brand_use_revision_brand_use_id_3341e19d_fk_gcd_brand_use_id` (`brand_use_id`),
  KEY `oi_brand_use_revision_deleted_fa1b2483` (`deleted`),
  KEY `oi_brand_use_revision_created_e46073a9` (`created`),
  KEY `oi_brand_use_revision_modified_eb229a67` (`modified`),
  KEY `oi_brand_use_revision_year_began_4f1d24fe` (`year_began`),
  KEY `oi_brand_use_revision_committed_d249739e` (`committed`),
  CONSTRAINT `oi_brand_use_revisio_previous_revision_id_960be011_fk_oi_brand_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_brand_use_revision` (`id`),
  CONSTRAINT `oi_brand_use_revision_brand_use_id_3341e19d_fk_gcd_brand_use_id` FOREIGN KEY (`brand_use_id`) REFERENCES `gcd_brand_use` (`id`),
  CONSTRAINT `oi_brand_use_revision_changeset_id_b9e8a6fe_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_brand_use_revision_emblem_id_ed990457_fk_gcd_brand_id` FOREIGN KEY (`emblem_id`) REFERENCES `gcd_brand` (`id`),
  CONSTRAINT `oi_brand_use_revision_publisher_id_277730e8_fk_gcd_publisher_id` FOREIGN KEY (`publisher_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_brand_use_revision` WRITE;
/*!40000 ALTER TABLE `oi_brand_use_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_brand_use_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_changeset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_changeset` (
  `id` int NOT NULL AUTO_INCREMENT,
  `state` int NOT NULL,
  `change_type` int NOT NULL,
  `migrated` tinyint(1) NOT NULL,
  `date_inferred` tinyint(1) NOT NULL,
  `imps` int NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `approver_id` int DEFAULT NULL,
  `indexer_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `oi_changeset_approver_id_f970226e_fk_auth_user_id` (`approver_id`),
  KEY `oi_changeset_indexer_id_dd348fc6_fk_auth_user_id` (`indexer_id`),
  KEY `oi_changeset_state_a368e26d` (`state`),
  KEY `oi_changeset_change_type_fcc0b41a` (`change_type`),
  KEY `oi_changeset_migrated_d0f725c0` (`migrated`),
  KEY `oi_changeset_created_a8f81b00` (`created`),
  KEY `oi_changeset_modified_7f648d8f` (`modified`),
  CONSTRAINT `oi_changeset_approver_id_f970226e_fk_auth_user_id` FOREIGN KEY (`approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `oi_changeset_indexer_id_dd348fc6_fk_auth_user_id` FOREIGN KEY (`indexer_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_changeset` WRITE;
/*!40000 ALTER TABLE `oi_changeset` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_changeset` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_changeset_along_with`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_changeset_along_with` (
  `id` int NOT NULL AUTO_INCREMENT,
  `changeset_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_changeset_along_with_changeset_id_user_id_116fcdff_uniq` (`changeset_id`,`user_id`),
  KEY `oi_changeset_along_with_user_id_116fa8e2_fk_auth_user_id` (`user_id`),
  CONSTRAINT `oi_changeset_along_with_changeset_id_c73d87c4_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_changeset_along_with_user_id_116fa8e2_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_changeset_along_with` WRITE;
/*!40000 ALTER TABLE `oi_changeset_along_with` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_changeset_along_with` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_changeset_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_changeset_comment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `revision_id` int DEFAULT NULL,
  `old_state` int NOT NULL,
  `new_state` int NOT NULL,
  `created` datetime(6) NOT NULL,
  `changeset_id` int NOT NULL,
  `commenter_id` int NOT NULL,
  `content_type_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `oi_changeset_comment_changeset_id_4e28133a_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_changeset_comment_commenter_id_46052c0f_fk_auth_user_id` (`commenter_id`),
  KEY `oi_changeset_comment_content_type_id_eb8dfc4e_fk_django_co` (`content_type_id`),
  KEY `oi_changeset_comment_revision_id_3e6c4291` (`revision_id`),
  CONSTRAINT `oi_changeset_comment_changeset_id_4e28133a_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_changeset_comment_commenter_id_46052c0f_fk_auth_user_id` FOREIGN KEY (`commenter_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `oi_changeset_comment_content_type_id_eb8dfc4e_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_changeset_comment` WRITE;
/*!40000 ALTER TABLE `oi_changeset_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_changeset_comment` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_changeset_on_behalf_of`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_changeset_on_behalf_of` (
  `id` int NOT NULL AUTO_INCREMENT,
  `changeset_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_changeset_on_behalf_of_changeset_id_user_id_863e201f_uniq` (`changeset_id`,`user_id`),
  KEY `oi_changeset_on_behalf_of_user_id_569cd4a8_fk_auth_user_id` (`user_id`),
  CONSTRAINT `oi_changeset_on_beha_changeset_id_b7d65937_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_changeset_on_behalf_of_user_id_569cd4a8_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_changeset_on_behalf_of` WRITE;
/*!40000 ALTER TABLE `oi_changeset_on_behalf_of` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_changeset_on_behalf_of` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_character_name_detail_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_character_name_detail_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `character_id` int DEFAULT NULL,
  `character_name_detail_id` int DEFAULT NULL,
  `character_revision_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `is_official_name` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_character_name_de_changeset_id_ca981e14_fk_oi_change` (`changeset_id`),
  KEY `oi_character_name_de_character_id_4ca5ab1d_fk_gcd_chara` (`character_id`),
  KEY `oi_character_name_de_character_name_detai_86f64841_fk_gcd_chara` (`character_name_detail_id`),
  KEY `oi_character_name_de_character_revision_i_7a1b09f7_fk_oi_charac` (`character_revision_id`),
  KEY `oi_character_name_detail_revision_deleted_766c3758` (`deleted`),
  KEY `oi_character_name_detail_revision_committed_e47c4061` (`committed`),
  KEY `oi_character_name_detail_revision_created_2b8df7b4` (`created`),
  KEY `oi_character_name_detail_revision_modified_7657dccc` (`modified`),
  KEY `oi_character_name_detail_revision_name_1a7f387a` (`name`),
  CONSTRAINT `oi_character_name_de_changeset_id_ca981e14_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_character_name_de_character_id_4ca5ab1d_fk_gcd_chara` FOREIGN KEY (`character_id`) REFERENCES `gcd_character` (`id`),
  CONSTRAINT `oi_character_name_de_character_name_detai_86f64841_fk_gcd_chara` FOREIGN KEY (`character_name_detail_id`) REFERENCES `gcd_character_name_detail` (`id`),
  CONSTRAINT `oi_character_name_de_character_revision_i_7a1b09f7_fk_oi_charac` FOREIGN KEY (`character_revision_id`) REFERENCES `oi_character_revision` (`id`),
  CONSTRAINT `oi_character_name_de_previous_revision_id_ca21d6c4_fk_oi_charac` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_character_name_detail_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_character_name_detail_revision` WRITE;
/*!40000 ALTER TABLE `oi_character_name_detail_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_character_name_detail_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_character_order_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_character_order_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `changeset_id` int NOT NULL,
  `character_order_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `story_revision_id` int NOT NULL,
  `type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_character_order_r_changeset_id_539fa189_fk_oi_change` (`changeset_id`),
  KEY `oi_character_order_r_character_order_id_83bfe29d_fk_gcd_chara` (`character_order_id`),
  KEY `oi_character_order_r_story_revision_id_41334cd2_fk_oi_story_` (`story_revision_id`),
  KEY `oi_character_order_r_type_id_fa412cee_fk_gcd_chara` (`type_id`),
  KEY `oi_character_order_revision_deleted_aed55dba` (`deleted`),
  KEY `oi_character_order_revision_committed_e10e5a46` (`committed`),
  KEY `oi_character_order_revision_created_08b11f71` (`created`),
  KEY `oi_character_order_revision_modified_21432926` (`modified`),
  CONSTRAINT `oi_character_order_r_changeset_id_539fa189_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_character_order_r_character_order_id_83bfe29d_fk_gcd_chara` FOREIGN KEY (`character_order_id`) REFERENCES `gcd_character_order` (`id`),
  CONSTRAINT `oi_character_order_r_previous_revision_id_30698368_fk_oi_charac` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_character_order_revision` (`id`),
  CONSTRAINT `oi_character_order_r_story_revision_id_41334cd2_fk_oi_story_` FOREIGN KEY (`story_revision_id`) REFERENCES `oi_story_revision` (`id`),
  CONSTRAINT `oi_character_order_r_type_id_fa412cee_fk_gcd_chara` FOREIGN KEY (`type_id`) REFERENCES `gcd_character_order_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_character_order_revision` WRITE;
/*!40000 ALTER TABLE `oi_character_order_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_character_order_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_character_relation_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_character_relation_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `character_relation_id` int DEFAULT NULL,
  `from_character_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `relation_type_id` int NOT NULL,
  `to_character_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_character_relatio_changeset_id_7b128916_fk_oi_change` (`changeset_id`),
  KEY `oi_character_relatio_character_relation_i_d6b84377_fk_gcd_chara` (`character_relation_id`),
  KEY `oi_character_relatio_from_character_id_ad4c9a87_fk_gcd_chara` (`from_character_id`),
  KEY `oi_character_relatio_relation_type_id_95402e70_fk_gcd_chara` (`relation_type_id`),
  KEY `oi_character_relatio_to_character_id_9c30e013_fk_gcd_chara` (`to_character_id`),
  KEY `oi_character_relation_revision_deleted_c8f40910` (`deleted`),
  KEY `oi_character_relation_revision_committed_0abf5c1c` (`committed`),
  KEY `oi_character_relation_revision_created_3830a0f6` (`created`),
  KEY `oi_character_relation_revision_modified_80d49c26` (`modified`),
  CONSTRAINT `oi_character_relatio_changeset_id_7b128916_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_character_relatio_character_relation_i_d6b84377_fk_gcd_chara` FOREIGN KEY (`character_relation_id`) REFERENCES `gcd_character_relation` (`id`),
  CONSTRAINT `oi_character_relatio_from_character_id_ad4c9a87_fk_gcd_chara` FOREIGN KEY (`from_character_id`) REFERENCES `gcd_character` (`id`),
  CONSTRAINT `oi_character_relatio_previous_revision_id_f7214cbc_fk_oi_charac` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_character_relation_revision` (`id`),
  CONSTRAINT `oi_character_relatio_relation_type_id_95402e70_fk_gcd_chara` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_character_relation_type` (`id`),
  CONSTRAINT `oi_character_relatio_to_character_id_9c30e013_fk_gcd_chara` FOREIGN KEY (`to_character_id`) REFERENCES `gcd_character` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_character_relation_revision` WRITE;
/*!40000 ALTER TABLE `oi_character_relation_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_character_relation_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_character_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_character_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `character_id` int DEFAULT NULL,
  `language_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `universe_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_character_revision_changeset_id_8796d324_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_character_revision_character_id_3a98bcc4_fk_gcd_character_id` (`character_id`),
  KEY `oi_character_revisio_language_id_a9e6bf66_fk_stddata_l` (`language_id`),
  KEY `oi_character_revision_deleted_058e60e5` (`deleted`),
  KEY `oi_character_revision_committed_11ac9fee` (`committed`),
  KEY `oi_character_revision_created_fac039c2` (`created`),
  KEY `oi_character_revision_modified_71c5addf` (`modified`),
  KEY `oi_character_revision_name_d7194497` (`name`),
  KEY `oi_character_revision_disambiguation_8994e26b` (`disambiguation`),
  KEY `oi_character_revision_year_first_published_eab704f3` (`year_first_published`),
  KEY `oi_character_revision_universe_id_e263f718_fk_gcd_universe_id` (`universe_id`),
  CONSTRAINT `oi_character_revisio_language_id_a9e6bf66_fk_stddata_l` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `oi_character_revisio_previous_revision_id_cca9d0d6_fk_oi_charac` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_character_revision` (`id`),
  CONSTRAINT `oi_character_revision_changeset_id_8796d324_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_character_revision_character_id_3a98bcc4_fk_gcd_character_id` FOREIGN KEY (`character_id`) REFERENCES `gcd_character` (`id`),
  CONSTRAINT `oi_character_revision_universe_id_e263f718_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_character_revision` WRITE;
/*!40000 ALTER TABLE `oi_character_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_character_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_character_through_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_character_through_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_code` int NOT NULL,
  `order_id` int NOT NULL,
  `story_character_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `oi_character_through_order_id_8599ffe4_fk_oi_charac` (`order_id`),
  KEY `oi_character_through_story_character_id_4e024e05_fk_oi_story_` (`story_character_id`),
  KEY `oi_character_through_order_order_code_5559195d` (`order_code`),
  CONSTRAINT `oi_character_through_order_id_8599ffe4_fk_oi_charac` FOREIGN KEY (`order_id`) REFERENCES `oi_character_order_revision` (`id`),
  CONSTRAINT `oi_character_through_story_character_id_4e024e05_fk_oi_story_` FOREIGN KEY (`story_character_id`) REFERENCES `oi_story_character_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_character_through_order` WRITE;
/*!40000 ALTER TABLE `oi_character_through_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_character_through_order` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_cover_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_cover_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `marked` tinyint(1) NOT NULL,
  `is_replacement` tinyint(1) NOT NULL,
  `is_wraparound` tinyint(1) NOT NULL,
  `front_left` int DEFAULT NULL,
  `front_right` int DEFAULT NULL,
  `front_bottom` int DEFAULT NULL,
  `front_top` int DEFAULT NULL,
  `file_source` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `cover_id` int DEFAULT NULL,
  `issue_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_cover_revision_changeset_id_a233094b_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_cover_revision_cover_id_4a38c303_fk_gcd_cover_id` (`cover_id`),
  KEY `oi_cover_revision_issue_id_7e56ae0f_fk_gcd_issue_id` (`issue_id`),
  KEY `oi_cover_revision_deleted_80a20c3a` (`deleted`),
  KEY `oi_cover_revision_created_4179491e` (`created`),
  KEY `oi_cover_revision_modified_79c32dc1` (`modified`),
  KEY `oi_cover_revision_committed_d6ac9b95` (`committed`),
  CONSTRAINT `oi_cover_revision_changeset_id_a233094b_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_cover_revision_cover_id_4a38c303_fk_gcd_cover_id` FOREIGN KEY (`cover_id`) REFERENCES `gcd_cover` (`id`),
  CONSTRAINT `oi_cover_revision_issue_id_7e56ae0f_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `oi_cover_revision_previous_revision_id_a63389c2_fk_oi_cover_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_cover_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_cover_revision` WRITE;
/*!40000 ALTER TABLE `oi_cover_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_cover_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_art_influence_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_art_influence_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `influence_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `creator_art_influence_id` int DEFAULT NULL,
  `influence_link_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_art_influ_changeset_id_fe12d79e_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_art_influ_creator_id_529b0266_fk_gcd_creat` (`creator_id`),
  KEY `oi_creator_art_influ_creator_art_influenc_a7127c7a_fk_gcd_creat` (`creator_art_influence_id`),
  KEY `oi_creator_art_influ_influence_link_id_6b688414_fk_gcd_creat` (`influence_link_id`),
  KEY `oi_creator_art_influence_revision_deleted_a00d6710` (`deleted`),
  KEY `oi_creator_art_influence_revision_created_129d737f` (`created`),
  KEY `oi_creator_art_influence_revision_modified_c01b0ba6` (`modified`),
  KEY `oi_creator_art_influence_revision_committed_58e438bf` (`committed`),
  CONSTRAINT `oi_creator_art_influ_changeset_id_fe12d79e_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_art_influ_creator_art_influenc_a7127c7a_fk_gcd_creat` FOREIGN KEY (`creator_art_influence_id`) REFERENCES `gcd_creator_art_influence` (`id`),
  CONSTRAINT `oi_creator_art_influ_creator_id_529b0266_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_art_influ_influence_link_id_6b688414_fk_gcd_creat` FOREIGN KEY (`influence_link_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_art_influ_previous_revision_id_1805de4d_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_art_influence_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_art_influence_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_art_influence_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_art_influence_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_degree_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_degree_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `degree_year` smallint unsigned DEFAULT NULL,
  `degree_year_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `creator_degree_id` int DEFAULT NULL,
  `degree_id` int NOT NULL,
  `school_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_degree_re_changeset_id_4b2f04b6_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_degree_revision_creator_id_312bb0f7_fk_gcd_creator_id` (`creator_id`),
  KEY `oi_creator_degree_re_creator_degree_id_9b0691db_fk_gcd_creat` (`creator_degree_id`),
  KEY `oi_creator_degree_revision_degree_id_1d047df0_fk_gcd_degree_id` (`degree_id`),
  KEY `oi_creator_degree_revision_school_id_42076b09_fk_gcd_school_id` (`school_id`),
  KEY `oi_creator_degree_revision_deleted_0697da4c` (`deleted`),
  KEY `oi_creator_degree_revision_created_207bc086` (`created`),
  KEY `oi_creator_degree_revision_modified_17f01e81` (`modified`),
  KEY `oi_creator_degree_revision_committed_d44f6978` (`committed`),
  CONSTRAINT `oi_creator_degree_re_changeset_id_4b2f04b6_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_degree_re_creator_degree_id_9b0691db_fk_gcd_creat` FOREIGN KEY (`creator_degree_id`) REFERENCES `gcd_creator_degree` (`id`),
  CONSTRAINT `oi_creator_degree_re_previous_revision_id_650fc25e_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_degree_revision` (`id`),
  CONSTRAINT `oi_creator_degree_revision_creator_id_312bb0f7_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_degree_revision_degree_id_1d047df0_fk_gcd_degree_id` FOREIGN KEY (`degree_id`) REFERENCES `gcd_degree` (`id`),
  CONSTRAINT `oi_creator_degree_revision_school_id_42076b09_fk_gcd_school_id` FOREIGN KEY (`school_id`) REFERENCES `gcd_school` (`id`),
  CONSTRAINT `oi_creator_degree_revision_chk_1` CHECK ((`degree_year` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_degree_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_degree_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_degree_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_membership_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_membership_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `organization_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `membership_year_began` smallint unsigned DEFAULT NULL,
  `membership_year_began_uncertain` tinyint(1) NOT NULL,
  `membership_year_ended` smallint unsigned DEFAULT NULL,
  `membership_year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `creator_membership_id` int DEFAULT NULL,
  `membership_type_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_membershi_changeset_id_f577a882_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_membershi_creator_id_75dc459d_fk_gcd_creat` (`creator_id`),
  KEY `oi_creator_membershi_creator_membership_i_99d7114c_fk_gcd_creat` (`creator_membership_id`),
  KEY `oi_creator_membershi_membership_type_id_531d7d87_fk_gcd_membe` (`membership_type_id`),
  KEY `oi_creator_membership_revision_deleted_9b637b03` (`deleted`),
  KEY `oi_creator_membership_revision_created_ec79c45c` (`created`),
  KEY `oi_creator_membership_revision_modified_83c6413a` (`modified`),
  KEY `oi_creator_membership_revision_committed_8136ca47` (`committed`),
  CONSTRAINT `oi_creator_membershi_changeset_id_f577a882_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_membershi_creator_id_75dc459d_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_membershi_creator_membership_i_99d7114c_fk_gcd_creat` FOREIGN KEY (`creator_membership_id`) REFERENCES `gcd_creator_membership` (`id`),
  CONSTRAINT `oi_creator_membershi_membership_type_id_531d7d87_fk_gcd_membe` FOREIGN KEY (`membership_type_id`) REFERENCES `gcd_membership_type` (`id`),
  CONSTRAINT `oi_creator_membershi_previous_revision_id_42dc2991_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_membership_revision` (`id`),
  CONSTRAINT `oi_creator_membership_revision_chk_1` CHECK ((`membership_year_began` >= 0)),
  CONSTRAINT `oi_creator_membership_revision_chk_2` CHECK ((`membership_year_ended` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_membership_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_membership_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_membership_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_name_detail_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_name_detail_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_revision_id` int DEFAULT NULL,
  `creator_name_detail_id` int DEFAULT NULL,
  `type_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `creator_id` int DEFAULT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_official_name` tinyint(1) NOT NULL,
  `in_script_id` int NOT NULL,
  `family_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `given_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_name_deta_creator_name_detail__db6695a7_fk_gcd_creat` (`creator_name_detail_id`),
  KEY `oi_creator_name_deta_type_id_8d6f51b1_fk_gcd_name_` (`type_id`),
  KEY `oi_creator_name_deta_changeset_id_5d1e3308_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_name_detail_revision_deleted_4f7cdb4f` (`deleted`),
  KEY `oi_creator_name_detail_revision_created_1c7b2665` (`created`),
  KEY `oi_creator_name_detail_revision_modified_91146161` (`modified`),
  KEY `oi_creator_name_detail_revision_name_8eac408d` (`name`),
  KEY `oi_creator_name_detail_revision_committed_25d4dd2a` (`committed`),
  KEY `oi_creator_name_deta_creator_id_a91c544c_fk_gcd_creat` (`creator_id`),
  KEY `oi_creator_name_deta_creator_revision_id_9a308254_fk_oi_creato` (`creator_revision_id`),
  KEY `oi_creator_name_deta_in_script_id_2b36e1b3_fk_stddata_s` (`in_script_id`),
  KEY `oi_creator_name_detail_revision_family_name_394e0c7d` (`family_name`),
  KEY `oi_creator_name_detail_revision_given_name_ae167599` (`given_name`),
  CONSTRAINT `oi_creator_name_deta_changeset_id_5d1e3308_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_name_deta_creator_id_a91c544c_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_name_deta_creator_name_detail__db6695a7_fk_gcd_creat` FOREIGN KEY (`creator_name_detail_id`) REFERENCES `gcd_creator_name_detail` (`id`),
  CONSTRAINT `oi_creator_name_deta_creator_revision_id_9a308254_fk_oi_creato` FOREIGN KEY (`creator_revision_id`) REFERENCES `oi_creator_revision` (`id`),
  CONSTRAINT `oi_creator_name_deta_in_script_id_2b36e1b3_fk_stddata_s` FOREIGN KEY (`in_script_id`) REFERENCES `stddata_script` (`id`),
  CONSTRAINT `oi_creator_name_deta_previous_revision_id_dee3b168_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_name_detail_revision` (`id`),
  CONSTRAINT `oi_creator_name_deta_type_id_8d6f51b1_fk_gcd_name_` FOREIGN KEY (`type_id`) REFERENCES `gcd_name_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_name_detail_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_name_detail_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_name_detail_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_non_comic_work_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_non_comic_work_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `publication_title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employer_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `work_title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `work_years` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `work_urls` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `creator_non_comic_work_id` int DEFAULT NULL,
  `work_role_id` int DEFAULT NULL,
  `work_type_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_non_comic_changeset_id_1e007f7a_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_non_comic_creator_id_888356cf_fk_gcd_creat` (`creator_id`),
  KEY `oi_creator_non_comic_creator_non_comic_wo_bd6ae75e_fk_gcd_creat` (`creator_non_comic_work_id`),
  KEY `oi_creator_non_comic_work_role_id_cf792744_fk_gcd_non_c` (`work_role_id`),
  KEY `oi_creator_non_comic_work_revision_deleted_3d732552` (`deleted`),
  KEY `oi_creator_non_comic_work_revision_created_e8626770` (`created`),
  KEY `oi_creator_non_comic_work_revision_modified_73ed0701` (`modified`),
  KEY `oi_creator_non_comic_work_revision_committed_ae152af3` (`committed`),
  KEY `oi_creator_non_comic_work_type_id_5732d6ff_fk_gcd_non_c` (`work_type_id`),
  CONSTRAINT `oi_creator_non_comic_changeset_id_1e007f7a_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_non_comic_creator_id_888356cf_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_non_comic_creator_non_comic_wo_bd6ae75e_fk_gcd_creat` FOREIGN KEY (`creator_non_comic_work_id`) REFERENCES `gcd_creator_non_comic_work` (`id`),
  CONSTRAINT `oi_creator_non_comic_previous_revision_id_279453cf_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_non_comic_work_revision` (`id`),
  CONSTRAINT `oi_creator_non_comic_work_role_id_cf792744_fk_gcd_non_c` FOREIGN KEY (`work_role_id`) REFERENCES `gcd_non_comic_work_role` (`id`),
  CONSTRAINT `oi_creator_non_comic_work_type_id_5732d6ff_fk_gcd_non_c` FOREIGN KEY (`work_type_id`) REFERENCES `gcd_non_comic_work_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_non_comic_work_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_non_comic_work_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_non_comic_work_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_relation_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_relation_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_relation_id` int DEFAULT NULL,
  `from_creator_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `to_creator_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_relation__changeset_id_cceaf64f_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_relation__creator_relation_id_340962d2_fk_gcd_creat` (`creator_relation_id`),
  KEY `oi_creator_relation__from_creator_id_6a091de7_fk_gcd_creat` (`from_creator_id`),
  KEY `oi_creator_relation__relation_type_id_78c60270_fk_gcd_relat` (`relation_type_id`),
  KEY `oi_creator_relation__to_creator_id_51b1dfa5_fk_gcd_creat` (`to_creator_id`),
  KEY `oi_creator_relation_revision_deleted_9e491326` (`deleted`),
  KEY `oi_creator_relation_revision_created_f52a4909` (`created`),
  KEY `oi_creator_relation_revision_modified_50982885` (`modified`),
  KEY `oi_creator_relation_revision_committed_d8f39ba8` (`committed`),
  CONSTRAINT `oi_creator_relation__changeset_id_cceaf64f_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_relation__creator_relation_id_340962d2_fk_gcd_creat` FOREIGN KEY (`creator_relation_id`) REFERENCES `gcd_creator_relation` (`id`),
  CONSTRAINT `oi_creator_relation__from_creator_id_6a091de7_fk_gcd_creat` FOREIGN KEY (`from_creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_relation__previous_revision_id_e57006b4_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_relation_revision` (`id`),
  CONSTRAINT `oi_creator_relation__relation_type_id_78c60270_fk_gcd_relat` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_relation_type` (`id`),
  CONSTRAINT `oi_creator_relation__to_creator_id_51b1dfa5_fk_gcd_creat` FOREIGN KEY (`to_creator_id`) REFERENCES `gcd_creator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_relation_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_relation_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_relation_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_relation_revision_creator_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_relation_revision_creator_name` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creatorrelationrevision_id` int NOT NULL,
  `creatornamedetail_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_creator_relation_revi_creatorrelationrevision__d7dd54cc_uniq` (`creatorrelationrevision_id`,`creatornamedetail_id`),
  KEY `oi_creator_relation__creatornamedetail_id_83665531_fk_gcd_creat` (`creatornamedetail_id`),
  CONSTRAINT `oi_creator_relation__creatornamedetail_id_83665531_fk_gcd_creat` FOREIGN KEY (`creatornamedetail_id`) REFERENCES `gcd_creator_name_detail` (`id`),
  CONSTRAINT `oi_creator_relation__creatorrelationrevis_60ca1b46_fk_oi_creato` FOREIGN KEY (`creatorrelationrevision_id`) REFERENCES `oi_creator_relation_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_relation_revision_creator_name` WRITE;
/*!40000 ALTER TABLE `oi_creator_relation_revision_creator_name` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_relation_revision_creator_name` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `gcd_official_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_country_uncertain` tinyint(1) NOT NULL,
  `birth_province` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_province_uncertain` tinyint(1) NOT NULL,
  `birth_city` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_city_uncertain` tinyint(1) NOT NULL,
  `death_country_uncertain` tinyint(1) NOT NULL,
  `death_province` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `death_province_uncertain` tinyint(1) NOT NULL,
  `death_city` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `death_city_uncertain` tinyint(1) NOT NULL,
  `whos_who` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bio` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `birth_country_id` int DEFAULT NULL,
  `birth_date_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int DEFAULT NULL,
  `death_country_id` int DEFAULT NULL,
  `death_date_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_revision_death_country_id_405924d9_fk_stddata_c` (`death_country_id`),
  KEY `oi_creator_revision_death_date_id_7eb30a5f_fk_stddata_date_id` (`death_date_id`),
  KEY `oi_creator_revision_birth_country_id_08110f1c_fk_stddata_c` (`birth_country_id`),
  KEY `oi_creator_revision_birth_date_id_e366754f_fk_stddata_date_id` (`birth_date_id`),
  KEY `oi_creator_revision_changeset_id_47425c3b_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_creator_revision_creator_id_5e1f2e33_fk_gcd_creator_id` (`creator_id`),
  KEY `oi_creator_revision_deleted_1f07f041` (`deleted`),
  KEY `oi_creator_revision_created_69c176f7` (`created`),
  KEY `oi_creator_revision_modified_3821c4d1` (`modified`),
  KEY `oi_creator_revision_gcd_official_name_27da02bd` (`gcd_official_name`),
  KEY `oi_creator_revision_committed_fb43914d` (`committed`),
  KEY `oi_creator_revision_disambiguation_802e0b91` (`disambiguation`),
  CONSTRAINT `oi_creator_revision_birth_country_id_08110f1c_fk_stddata_c` FOREIGN KEY (`birth_country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `oi_creator_revision_birth_date_id_e366754f_fk_stddata_date_id` FOREIGN KEY (`birth_date_id`) REFERENCES `stddata_date` (`id`),
  CONSTRAINT `oi_creator_revision_changeset_id_47425c3b_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_revision_creator_id_5e1f2e33_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_revision_death_country_id_405924d9_fk_stddata_c` FOREIGN KEY (`death_country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `oi_creator_revision_death_date_id_7eb30a5f_fk_stddata_date_id` FOREIGN KEY (`death_date_id`) REFERENCES `stddata_date` (`id`),
  CONSTRAINT `oi_creator_revision_previous_revision_id_708cb511_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_school_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_school_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `school_year_began` smallint unsigned DEFAULT NULL,
  `school_year_began_uncertain` tinyint(1) NOT NULL,
  `school_year_ended` smallint unsigned DEFAULT NULL,
  `school_year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `creator_school_id` int DEFAULT NULL,
  `school_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_school_re_changeset_id_bef44da8_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_school_revision_creator_id_d511895e_fk_gcd_creator_id` (`creator_id`),
  KEY `oi_creator_school_re_creator_school_id_b76cd97c_fk_gcd_creat` (`creator_school_id`),
  KEY `oi_creator_school_revision_school_id_c6f22b8d_fk_gcd_school_id` (`school_id`),
  KEY `oi_creator_school_revision_deleted_55fe0871` (`deleted`),
  KEY `oi_creator_school_revision_created_da95a78f` (`created`),
  KEY `oi_creator_school_revision_modified_2b4dfb7f` (`modified`),
  KEY `oi_creator_school_revision_committed_c408a0bf` (`committed`),
  CONSTRAINT `oi_creator_school_re_changeset_id_bef44da8_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_school_re_creator_school_id_b76cd97c_fk_gcd_creat` FOREIGN KEY (`creator_school_id`) REFERENCES `gcd_creator_school` (`id`),
  CONSTRAINT `oi_creator_school_re_previous_revision_id_8c17f175_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_school_revision` (`id`),
  CONSTRAINT `oi_creator_school_revision_creator_id_d511895e_fk_gcd_creator_id` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_school_revision_school_id_c6f22b8d_fk_gcd_school_id` FOREIGN KEY (`school_id`) REFERENCES `gcd_school` (`id`),
  CONSTRAINT `oi_creator_school_revision_chk_1` CHECK ((`school_year_began` >= 0)),
  CONSTRAINT `oi_creator_school_revision_chk_2` CHECK ((`school_year_ended` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_school_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_school_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_school_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_creator_signature_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_creator_signature_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `generic` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `creator_signature_id` int DEFAULT NULL,
  `image_revision_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_creator_signature_changeset_id_a50e9fb6_fk_oi_change` (`changeset_id`),
  KEY `oi_creator_signature_creator_id_4c75d831_fk_gcd_creat` (`creator_id`),
  KEY `oi_creator_signature_creator_signature_id_4266ac7b_fk_gcd_creat` (`creator_signature_id`),
  KEY `oi_creator_signature_image_revision_id_b93da436_fk_oi_image_` (`image_revision_id`),
  KEY `oi_creator_signature_revision_deleted_a3d0077d` (`deleted`),
  KEY `oi_creator_signature_revision_committed_a7fec756` (`committed`),
  KEY `oi_creator_signature_revision_created_c7cd1030` (`created`),
  KEY `oi_creator_signature_revision_modified_9e371812` (`modified`),
  CONSTRAINT `oi_creator_signature_changeset_id_a50e9fb6_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_creator_signature_creator_id_4c75d831_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator` (`id`),
  CONSTRAINT `oi_creator_signature_creator_signature_id_4266ac7b_fk_gcd_creat` FOREIGN KEY (`creator_signature_id`) REFERENCES `gcd_creator_signature` (`id`),
  CONSTRAINT `oi_creator_signature_image_revision_id_b93da436_fk_oi_image_` FOREIGN KEY (`image_revision_id`) REFERENCES `oi_image_revision` (`id`),
  CONSTRAINT `oi_creator_signature_previous_revision_id_45dcecc7_fk_oi_creato` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_creator_signature_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_creator_signature_revision` WRITE;
/*!40000 ALTER TABLE `oi_creator_signature_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_creator_signature_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_data_source_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_data_source_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `revision_id` int DEFAULT NULL,
  `source_description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `field` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `data_source_id` int DEFAULT NULL,
  `source_type_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_data_source_revision_changeset_id_50f0765a_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_data_source_revis_content_type_id_b71e0f4c_fk_django_co` (`content_type_id`),
  KEY `oi_data_source_revis_data_source_id_60186c3c_fk_gcd_data_` (`data_source_id`),
  KEY `oi_data_source_revis_source_type_id_9a1e2528_fk_gcd_sourc` (`source_type_id`),
  KEY `oi_data_source_revision_deleted_015b3a8a` (`deleted`),
  KEY `oi_data_source_revision_created_53dc9651` (`created`),
  KEY `oi_data_source_revision_modified_08b0738d` (`modified`),
  KEY `oi_data_source_revision_revision_id_aa12b83e` (`revision_id`),
  KEY `oi_data_source_revision_committed_abb23945` (`committed`),
  CONSTRAINT `oi_data_source_revis_content_type_id_b71e0f4c_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `oi_data_source_revis_data_source_id_60186c3c_fk_gcd_data_` FOREIGN KEY (`data_source_id`) REFERENCES `gcd_data_source` (`id`),
  CONSTRAINT `oi_data_source_revis_previous_revision_id_917464e7_fk_oi_data_s` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_data_source_revision` (`id`),
  CONSTRAINT `oi_data_source_revis_source_type_id_9a1e2528_fk_gcd_sourc` FOREIGN KEY (`source_type_id`) REFERENCES `gcd_source_type` (`id`),
  CONSTRAINT `oi_data_source_revision_changeset_id_50f0765a_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_data_source_revision` WRITE;
/*!40000 ALTER TABLE `oi_data_source_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_data_source_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_external_link_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_external_link_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `object_id` int DEFAULT NULL,
  `link` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `external_link_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `site_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_external_link_rev_changeset_id_9a8326f0_fk_oi_change` (`changeset_id`),
  KEY `oi_external_link_rev_content_type_id_8ffadb66_fk_django_co` (`content_type_id`),
  KEY `oi_external_link_rev_external_link_id_972fb748_fk_gcd_exter` (`external_link_id`),
  KEY `oi_external_link_rev_site_id_9fb18059_fk_gcd_exter` (`site_id`),
  KEY `oi_external_link_revision_deleted_e8649312` (`deleted`),
  KEY `oi_external_link_revision_committed_4ca35ada` (`committed`),
  KEY `oi_external_link_revision_created_0fc4fe6a` (`created`),
  KEY `oi_external_link_revision_modified_c3b2e83a` (`modified`),
  KEY `oi_external_link_revision_object_id_dd1be01d` (`object_id`),
  CONSTRAINT `oi_external_link_rev_changeset_id_9a8326f0_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_external_link_rev_content_type_id_8ffadb66_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `oi_external_link_rev_external_link_id_972fb748_fk_gcd_exter` FOREIGN KEY (`external_link_id`) REFERENCES `gcd_external_link` (`id`),
  CONSTRAINT `oi_external_link_rev_previous_revision_id_818cb166_fk_oi_extern` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_external_link_revision` (`id`),
  CONSTRAINT `oi_external_link_rev_site_id_9fb18059_fk_gcd_exter` FOREIGN KEY (`site_id`) REFERENCES `gcd_external_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_external_link_revision` WRITE;
/*!40000 ALTER TABLE `oi_external_link_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_external_link_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_feature_logo_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_feature_logo_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `leading_article` tinyint(1) NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `feature_logo_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `generic` tinyint(1) NOT NULL,
  `image_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_feature_logo_revi_changeset_id_9da78b5e_fk_oi_change` (`changeset_id`),
  KEY `oi_feature_logo_revi_feature_logo_id_4a59e362_fk_gcd_featu` (`feature_logo_id`),
  KEY `oi_feature_logo_revision_deleted_057b1479` (`deleted`),
  KEY `oi_feature_logo_revision_committed_aad677f8` (`committed`),
  KEY `oi_feature_logo_revision_created_fff59aca` (`created`),
  KEY `oi_feature_logo_revision_modified_3fadac73` (`modified`),
  KEY `oi_feature_logo_revision_year_began_1e9569ee` (`year_began`),
  KEY `oi_feature_logo_revi_image_revision_id_12ce229d_fk_oi_image_` (`image_revision_id`),
  CONSTRAINT `oi_feature_logo_revi_changeset_id_9da78b5e_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_feature_logo_revi_feature_logo_id_4a59e362_fk_gcd_featu` FOREIGN KEY (`feature_logo_id`) REFERENCES `gcd_feature_logo` (`id`),
  CONSTRAINT `oi_feature_logo_revi_image_revision_id_12ce229d_fk_oi_image_` FOREIGN KEY (`image_revision_id`) REFERENCES `oi_image_revision` (`id`),
  CONSTRAINT `oi_feature_logo_revi_previous_revision_id_05983ab4_fk_oi_featur` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_feature_logo_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_feature_logo_revision` WRITE;
/*!40000 ALTER TABLE `oi_feature_logo_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_feature_logo_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_feature_logo_revision_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_feature_logo_revision_feature` (
  `id` int NOT NULL AUTO_INCREMENT,
  `featurelogorevision_id` int NOT NULL,
  `feature_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_feature_logo_revision_featurelogorevision_id_f_ac421657_uniq` (`featurelogorevision_id`,`feature_id`),
  KEY `oi_feature_logo_revi_feature_id_b8b188fd_fk_gcd_featu` (`feature_id`),
  CONSTRAINT `oi_feature_logo_revi_feature_id_b8b188fd_fk_gcd_featu` FOREIGN KEY (`feature_id`) REFERENCES `gcd_feature` (`id`),
  CONSTRAINT `oi_feature_logo_revi_featurelogorevision__16c86f37_fk_oi_featur` FOREIGN KEY (`featurelogorevision_id`) REFERENCES `oi_feature_logo_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_feature_logo_revision_feature` WRITE;
/*!40000 ALTER TABLE `oi_feature_logo_revision_feature` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_feature_logo_revision_feature` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_feature_relation_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_feature_relation_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `feature_relation_id` int DEFAULT NULL,
  `from_feature_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `relation_type_id` int NOT NULL,
  `to_feature_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_feature_relation__changeset_id_556a7bb6_fk_oi_change` (`changeset_id`),
  KEY `oi_feature_relation__feature_relation_id_3d027e06_fk_gcd_featu` (`feature_relation_id`),
  KEY `oi_feature_relation__from_feature_id_a1958195_fk_gcd_featu` (`from_feature_id`),
  KEY `oi_feature_relation__relation_type_id_085c6b13_fk_gcd_featu` (`relation_type_id`),
  KEY `oi_feature_relation__to_feature_id_cb00fcfe_fk_gcd_featu` (`to_feature_id`),
  KEY `oi_feature_relation_revision_deleted_1b19e3d1` (`deleted`),
  KEY `oi_feature_relation_revision_committed_ed3a4919` (`committed`),
  KEY `oi_feature_relation_revision_created_4ce19608` (`created`),
  KEY `oi_feature_relation_revision_modified_502c974d` (`modified`),
  CONSTRAINT `oi_feature_relation__changeset_id_556a7bb6_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_feature_relation__feature_relation_id_3d027e06_fk_gcd_featu` FOREIGN KEY (`feature_relation_id`) REFERENCES `gcd_feature_relation` (`id`),
  CONSTRAINT `oi_feature_relation__from_feature_id_a1958195_fk_gcd_featu` FOREIGN KEY (`from_feature_id`) REFERENCES `gcd_feature` (`id`),
  CONSTRAINT `oi_feature_relation__previous_revision_id_11c60d5a_fk_oi_featur` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_feature_relation_revision` (`id`),
  CONSTRAINT `oi_feature_relation__relation_type_id_085c6b13_fk_gcd_featu` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_feature_relation_type` (`id`),
  CONSTRAINT `oi_feature_relation__to_feature_id_cb00fcfe_fk_gcd_featu` FOREIGN KEY (`to_feature_id`) REFERENCES `gcd_feature` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_feature_relation_revision` WRITE;
/*!40000 ALTER TABLE `oi_feature_relation_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_feature_relation_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_feature_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_feature_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `leading_article` tinyint(1) NOT NULL,
  `genre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `feature_id` int DEFAULT NULL,
  `feature_type_id` int NOT NULL,
  `language_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_feature_revision_changeset_id_c52c2cf1_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_feature_revision_feature_id_ad167e45_fk_gcd_feature_id` (`feature_id`),
  KEY `oi_feature_revision_feature_type_id_e743b3a0_fk_gcd_featu` (`feature_type_id`),
  KEY `oi_feature_revision_language_id_3f424884_fk_stddata_language_id` (`language_id`),
  KEY `oi_feature_revision_deleted_3bb6cf9b` (`deleted`),
  KEY `oi_feature_revision_committed_f8e2681c` (`committed`),
  KEY `oi_feature_revision_created_adee457a` (`created`),
  KEY `oi_feature_revision_modified_ce744889` (`modified`),
  KEY `oi_feature_revision_year_created_46ad3047` (`year_first_published`),
  KEY `oi_feature_revision_disambiguation_2bb58885` (`disambiguation`),
  CONSTRAINT `oi_feature_revision_changeset_id_c52c2cf1_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_feature_revision_feature_id_ad167e45_fk_gcd_feature_id` FOREIGN KEY (`feature_id`) REFERENCES `gcd_feature` (`id`),
  CONSTRAINT `oi_feature_revision_feature_type_id_e743b3a0_fk_gcd_featu` FOREIGN KEY (`feature_type_id`) REFERENCES `gcd_feature_type` (`id`),
  CONSTRAINT `oi_feature_revision_language_id_3f424884_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `oi_feature_revision_previous_revision_id_e7a621bb_fk_oi_featur` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_feature_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_feature_revision` WRITE;
/*!40000 ALTER TABLE `oi_feature_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_feature_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_group_membership_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_group_membership_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `organization_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_joined` smallint unsigned DEFAULT NULL,
  `year_joined_uncertain` tinyint(1) NOT NULL,
  `year_left` smallint unsigned DEFAULT NULL,
  `year_left_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `character_id` int NOT NULL,
  `group_id` int NOT NULL,
  `group_membership_id` int DEFAULT NULL,
  `membership_type_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_group_membership__changeset_id_051833a7_fk_oi_change` (`changeset_id`),
  KEY `oi_group_membership__character_id_e6bb5416_fk_gcd_chara` (`character_id`),
  KEY `oi_group_membership_revision_group_id_59a3a164_fk_gcd_group_id` (`group_id`),
  KEY `oi_group_membership__group_membership_id_70263e3c_fk_gcd_group` (`group_membership_id`),
  KEY `oi_group_membership__membership_type_id_b976d0ff_fk_gcd_group` (`membership_type_id`),
  KEY `oi_group_membership_revision_deleted_c573587f` (`deleted`),
  KEY `oi_group_membership_revision_committed_6b381168` (`committed`),
  KEY `oi_group_membership_revision_created_5222895f` (`created`),
  KEY `oi_group_membership_revision_modified_f42b609f` (`modified`),
  CONSTRAINT `oi_group_membership__changeset_id_051833a7_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_group_membership__character_id_e6bb5416_fk_gcd_chara` FOREIGN KEY (`character_id`) REFERENCES `gcd_character` (`id`),
  CONSTRAINT `oi_group_membership__group_membership_id_70263e3c_fk_gcd_group` FOREIGN KEY (`group_membership_id`) REFERENCES `gcd_group_membership` (`id`),
  CONSTRAINT `oi_group_membership__membership_type_id_b976d0ff_fk_gcd_group` FOREIGN KEY (`membership_type_id`) REFERENCES `gcd_group_membership_type` (`id`),
  CONSTRAINT `oi_group_membership__previous_revision_id_0ebb45d8_fk_oi_group_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_group_membership_revision` (`id`),
  CONSTRAINT `oi_group_membership_revision_group_id_59a3a164_fk_gcd_group_id` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`),
  CONSTRAINT `oi_group_membership_revision_chk_1` CHECK ((`year_joined` >= 0)),
  CONSTRAINT `oi_group_membership_revision_chk_2` CHECK ((`year_left` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_group_membership_revision` WRITE;
/*!40000 ALTER TABLE `oi_group_membership_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_group_membership_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_group_name_detail_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_group_name_detail_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_official_name` tinyint(1) NOT NULL,
  `changeset_id` int NOT NULL,
  `group_id` int DEFAULT NULL,
  `group_name_detail_id` int DEFAULT NULL,
  `group_revision_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_group_name_detail_changeset_id_fc0763c2_fk_oi_change` (`changeset_id`),
  KEY `oi_group_name_detail_revision_group_id_e190708f_fk_gcd_group_id` (`group_id`),
  KEY `oi_group_name_detail_group_name_detail_id_d05027a7_fk_gcd_group` (`group_name_detail_id`),
  KEY `oi_group_name_detail_group_revision_id_2d083514_fk_oi_group_` (`group_revision_id`),
  KEY `oi_group_name_detail_revision_deleted_844c3d16` (`deleted`),
  KEY `oi_group_name_detail_revision_committed_406755cd` (`committed`),
  KEY `oi_group_name_detail_revision_created_85399bfa` (`created`),
  KEY `oi_group_name_detail_revision_modified_f6e0c5d0` (`modified`),
  KEY `oi_group_name_detail_revision_name_ba5040dc` (`name`),
  CONSTRAINT `oi_group_name_detail_changeset_id_fc0763c2_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_group_name_detail_group_name_detail_id_d05027a7_fk_gcd_group` FOREIGN KEY (`group_name_detail_id`) REFERENCES `gcd_group_name_detail` (`id`),
  CONSTRAINT `oi_group_name_detail_group_revision_id_2d083514_fk_oi_group_` FOREIGN KEY (`group_revision_id`) REFERENCES `oi_group_revision` (`id`),
  CONSTRAINT `oi_group_name_detail_previous_revision_id_506d5c47_fk_oi_group_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_group_name_detail_revision` (`id`),
  CONSTRAINT `oi_group_name_detail_revision_group_id_e190708f_fk_gcd_group_id` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_group_name_detail_revision` WRITE;
/*!40000 ALTER TABLE `oi_group_name_detail_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_group_name_detail_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_group_relation_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_group_relation_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `from_group_id` int NOT NULL,
  `group_relation_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `relation_type_id` int NOT NULL,
  `to_group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_group_relation_re_changeset_id_d54a0269_fk_oi_change` (`changeset_id`),
  KEY `oi_group_relation_re_from_group_id_aa65fa72_fk_gcd_group` (`from_group_id`),
  KEY `oi_group_relation_re_group_relation_id_5b0456c7_fk_gcd_group` (`group_relation_id`),
  KEY `oi_group_relation_re_relation_type_id_97685ea6_fk_gcd_group` (`relation_type_id`),
  KEY `oi_group_relation_revision_to_group_id_35baf2e6_fk_gcd_group_id` (`to_group_id`),
  KEY `oi_group_relation_revision_deleted_12dc9ac3` (`deleted`),
  KEY `oi_group_relation_revision_committed_357476a6` (`committed`),
  KEY `oi_group_relation_revision_created_eb87736a` (`created`),
  KEY `oi_group_relation_revision_modified_0cbe2ba1` (`modified`),
  CONSTRAINT `oi_group_relation_re_changeset_id_d54a0269_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_group_relation_re_from_group_id_aa65fa72_fk_gcd_group` FOREIGN KEY (`from_group_id`) REFERENCES `gcd_group` (`id`),
  CONSTRAINT `oi_group_relation_re_group_relation_id_5b0456c7_fk_gcd_group` FOREIGN KEY (`group_relation_id`) REFERENCES `gcd_group_relation` (`id`),
  CONSTRAINT `oi_group_relation_re_previous_revision_id_02b2024a_fk_oi_group_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_group_relation_revision` (`id`),
  CONSTRAINT `oi_group_relation_re_relation_type_id_97685ea6_fk_gcd_group` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_group_relation_type` (`id`),
  CONSTRAINT `oi_group_relation_revision_to_group_id_35baf2e6_fk_gcd_group_id` FOREIGN KEY (`to_group_id`) REFERENCES `gcd_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_group_relation_revision` WRITE;
/*!40000 ALTER TABLE `oi_group_relation_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_group_relation_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_group_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_group_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `group_id` int DEFAULT NULL,
  `language_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `universe_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_group_revision_changeset_id_764e7f80_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_group_revision_group_id_97973cac_fk_gcd_group_id` (`group_id`),
  KEY `oi_group_revision_language_id_70fcb279_fk_stddata_language_id` (`language_id`),
  KEY `oi_group_revision_deleted_8d0de76c` (`deleted`),
  KEY `oi_group_revision_committed_c55f71f2` (`committed`),
  KEY `oi_group_revision_created_28b54918` (`created`),
  KEY `oi_group_revision_modified_e2329d25` (`modified`),
  KEY `oi_group_revision_name_fb4d0a2c` (`name`),
  KEY `oi_group_revision_disambiguation_db58c99d` (`disambiguation`),
  KEY `oi_group_revision_year_first_published_d3886f81` (`year_first_published`),
  KEY `oi_group_revision_universe_id_ee4d57b2_fk_gcd_universe_id` (`universe_id`),
  CONSTRAINT `oi_group_revision_changeset_id_764e7f80_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_group_revision_group_id_97973cac_fk_gcd_group_id` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`),
  CONSTRAINT `oi_group_revision_language_id_70fcb279_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `oi_group_revision_previous_revision_id_1d54cb3e_fk_oi_group_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_group_revision` (`id`),
  CONSTRAINT `oi_group_revision_universe_id_ee4d57b2_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_group_revision` WRITE;
/*!40000 ALTER TABLE `oi_group_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_group_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_image_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_image_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `object_id` int unsigned DEFAULT NULL,
  `image_file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `marked` tinyint(1) NOT NULL,
  `is_replacement` tinyint(1) NOT NULL,
  `changeset_id` int NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `image_id` int DEFAULT NULL,
  `type_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_image_revision_changeset_id_4f3485f3_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_image_revision_content_type_id_b5002d57_fk_django_co` (`content_type_id`),
  KEY `oi_image_revision_image_id_c6b213bd_fk_gcd_image_id` (`image_id`),
  KEY `oi_image_revision_type_id_508b672d_fk_gcd_image_type_id` (`type_id`),
  KEY `oi_image_revision_deleted_13d05cab` (`deleted`),
  KEY `oi_image_revision_created_37b36f61` (`created`),
  KEY `oi_image_revision_modified_c1bc14da` (`modified`),
  KEY `oi_image_revision_object_id_8837c216` (`object_id`),
  KEY `oi_image_revision_committed_95ae58ac` (`committed`),
  CONSTRAINT `oi_image_revision_changeset_id_4f3485f3_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_image_revision_content_type_id_b5002d57_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `oi_image_revision_image_id_c6b213bd_fk_gcd_image_id` FOREIGN KEY (`image_id`) REFERENCES `gcd_image` (`id`),
  CONSTRAINT `oi_image_revision_previous_revision_id_cc587ebb_fk_oi_image_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_image_revision` (`id`),
  CONSTRAINT `oi_image_revision_type_id_508b672d_fk_gcd_image_type_id` FOREIGN KEY (`type_id`) REFERENCES `gcd_image_type` (`id`),
  CONSTRAINT `oi_image_revision_chk_1` CHECK ((`object_id` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_image_revision` WRITE;
/*!40000 ALTER TABLE `oi_image_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_image_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_indicia_printer_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_indicia_printer_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `country_id` int NOT NULL,
  `indicia_printer_id` int DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_indicia_printer_r_changeset_id_e4c33b68_fk_oi_change` (`changeset_id`),
  KEY `oi_indicia_printer_r_country_id_8163be02_fk_stddata_c` (`country_id`),
  KEY `oi_indicia_printer_r_indicia_printer_id_f8b727e1_fk_gcd_indic` (`indicia_printer_id`),
  KEY `oi_indicia_printer_revision_parent_id_1fcdbf0d_fk_gcd_printer_id` (`parent_id`),
  KEY `oi_indicia_printer_revision_deleted_f617e91f` (`deleted`),
  KEY `oi_indicia_printer_revision_committed_f45ad0dc` (`committed`),
  KEY `oi_indicia_printer_revision_created_f1c946f1` (`created`),
  KEY `oi_indicia_printer_revision_modified_ea547e97` (`modified`),
  CONSTRAINT `oi_indicia_printer_r_changeset_id_e4c33b68_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_indicia_printer_r_country_id_8163be02_fk_stddata_c` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `oi_indicia_printer_r_indicia_printer_id_f8b727e1_fk_gcd_indic` FOREIGN KEY (`indicia_printer_id`) REFERENCES `gcd_indicia_printer` (`id`),
  CONSTRAINT `oi_indicia_printer_r_previous_revision_id_8196f927_fk_oi_indici` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_indicia_printer_revision` (`id`),
  CONSTRAINT `oi_indicia_printer_revision_parent_id_1fcdbf0d_fk_gcd_printer_id` FOREIGN KEY (`parent_id`) REFERENCES `gcd_printer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_indicia_printer_revision` WRITE;
/*!40000 ALTER TABLE `oi_indicia_printer_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_indicia_printer_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_indicia_publisher_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_indicia_publisher_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_surrogate` tinyint(1) NOT NULL,
  `changeset_id` int NOT NULL,
  `country_id` int NOT NULL,
  `indicia_publisher_id` int DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_indicia_publisher_changeset_id_20bda850_fk_oi_change` (`changeset_id`),
  KEY `oi_indicia_publisher_country_id_1bcfa59c_fk_stddata_c` (`country_id`),
  KEY `oi_indicia_publisher_indicia_publisher_id_4d4d910d_fk_gcd_indic` (`indicia_publisher_id`),
  KEY `oi_indicia_publisher_parent_id_d0ee8243_fk_gcd_publi` (`parent_id`),
  KEY `oi_indicia_publisher_revision_deleted_b3e598c2` (`deleted`),
  KEY `oi_indicia_publisher_revision_created_fc218047` (`created`),
  KEY `oi_indicia_publisher_revision_modified_28d7187c` (`modified`),
  KEY `oi_indicia_publisher_revision_committed_353236d5` (`committed`),
  CONSTRAINT `oi_indicia_publisher_changeset_id_20bda850_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_indicia_publisher_country_id_1bcfa59c_fk_stddata_c` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `oi_indicia_publisher_indicia_publisher_id_4d4d910d_fk_gcd_indic` FOREIGN KEY (`indicia_publisher_id`) REFERENCES `gcd_indicia_publisher` (`id`),
  CONSTRAINT `oi_indicia_publisher_parent_id_d0ee8243_fk_gcd_publi` FOREIGN KEY (`parent_id`) REFERENCES `gcd_publisher` (`id`),
  CONSTRAINT `oi_indicia_publisher_previous_revision_id_855aeaf2_fk_oi_indici` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_indicia_publisher_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_indicia_publisher_revision` WRITE;
/*!40000 ALTER TABLE `oi_indicia_publisher_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_indicia_publisher_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_issue_code_number_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_issue_code_number_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `issue_revision_id` int NOT NULL,
  `number_type_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `publisher_code_number_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_issue_code_number_changeset_id_7c1523aa_fk_oi_change` (`changeset_id`),
  KEY `oi_issue_code_number_issue_revision_id_886045a6_fk_oi_issue_` (`issue_revision_id`),
  KEY `oi_issue_code_number_number_type_id_add99eda_fk_gcd_code_` (`number_type_id`),
  KEY `oi_issue_code_number_publisher_code_numbe_44ad6bed_fk_gcd_issue` (`publisher_code_number_id`),
  KEY `oi_issue_code_number_revision_deleted_57e7042e` (`deleted`),
  KEY `oi_issue_code_number_revision_committed_1765397f` (`committed`),
  KEY `oi_issue_code_number_revision_created_b1095425` (`created`),
  KEY `oi_issue_code_number_revision_modified_4599e554` (`modified`),
  KEY `oi_issue_code_number_revision_number_afbe48c9` (`number`),
  CONSTRAINT `oi_issue_code_number_changeset_id_7c1523aa_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_issue_code_number_issue_revision_id_886045a6_fk_oi_issue_` FOREIGN KEY (`issue_revision_id`) REFERENCES `oi_issue_revision` (`id`),
  CONSTRAINT `oi_issue_code_number_number_type_id_add99eda_fk_gcd_code_` FOREIGN KEY (`number_type_id`) REFERENCES `gcd_code_number_type` (`id`),
  CONSTRAINT `oi_issue_code_number_previous_revision_id_3c1ddfb8_fk_oi_issue_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_issue_code_number_revision` (`id`),
  CONSTRAINT `oi_issue_code_number_publisher_code_numbe_44ad6bed_fk_gcd_issue` FOREIGN KEY (`publisher_code_number_id`) REFERENCES `gcd_issue_code_number` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_issue_code_number_revision` WRITE;
/*!40000 ALTER TABLE `oi_issue_code_number_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_issue_code_number_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_issue_credit_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_issue_credit_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `is_credited` tinyint(1) NOT NULL,
  `uncertain` tinyint(1) NOT NULL,
  `credited_as` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credit_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `credit_type_id` int NOT NULL,
  `issue_credit_id` int DEFAULT NULL,
  `issue_revision_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `is_sourced` tinyint(1) NOT NULL,
  `sourced_by` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_issue_credit_revi_changeset_id_81c9dd73_fk_oi_change` (`changeset_id`),
  KEY `oi_issue_credit_revi_creator_id_464ddeb3_fk_gcd_creat` (`creator_id`),
  KEY `oi_issue_credit_revi_credit_type_id_0c9b2e8d_fk_gcd_credi` (`credit_type_id`),
  KEY `oi_issue_credit_revi_issue_credit_id_ba1c5921_fk_gcd_issue` (`issue_credit_id`),
  KEY `oi_issue_credit_revi_issue_revision_id_9437797a_fk_oi_issue_` (`issue_revision_id`),
  KEY `oi_issue_credit_revision_deleted_acdf6156` (`deleted`),
  KEY `oi_issue_credit_revision_committed_2a8e39d1` (`committed`),
  KEY `oi_issue_credit_revision_created_1983b093` (`created`),
  KEY `oi_issue_credit_revision_modified_a028d646` (`modified`),
  KEY `oi_issue_credit_revision_is_credited_ddb4ab94` (`is_credited`),
  KEY `oi_issue_credit_revision_uncertain_efce121e` (`uncertain`),
  KEY `oi_issue_credit_revision_is_sourced_1df930e3` (`is_sourced`),
  CONSTRAINT `oi_issue_credit_revi_changeset_id_81c9dd73_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_issue_credit_revi_creator_id_464ddeb3_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator_name_detail` (`id`),
  CONSTRAINT `oi_issue_credit_revi_credit_type_id_0c9b2e8d_fk_gcd_credi` FOREIGN KEY (`credit_type_id`) REFERENCES `gcd_credit_type` (`id`),
  CONSTRAINT `oi_issue_credit_revi_issue_credit_id_ba1c5921_fk_gcd_issue` FOREIGN KEY (`issue_credit_id`) REFERENCES `gcd_issue_credit` (`id`),
  CONSTRAINT `oi_issue_credit_revi_issue_revision_id_9437797a_fk_oi_issue_` FOREIGN KEY (`issue_revision_id`) REFERENCES `oi_issue_revision` (`id`),
  CONSTRAINT `oi_issue_credit_revi_previous_revision_id_bd4e9ea0_fk_oi_issue_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_issue_credit_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_issue_credit_revision` WRITE;
/*!40000 ALTER TABLE `oi_issue_credit_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_issue_credit_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_issue_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_issue_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `revision_sort_code` int DEFAULT NULL,
  `reservation_requested` tinyint(1) NOT NULL,
  `number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_title` tinyint(1) NOT NULL,
  `volume` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_volume` tinyint(1) NOT NULL,
  `display_volume_with_number` tinyint(1) NOT NULL,
  `variant_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `publication_date` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `key_date` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_on_sale` int DEFAULT NULL,
  `month_on_sale` int DEFAULT NULL,
  `day_on_sale` int DEFAULT NULL,
  `on_sale_date_uncertain` tinyint(1) NOT NULL,
  `indicia_frequency` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_indicia_frequency` tinyint(1) NOT NULL,
  `price` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `page_count` decimal(10,3) DEFAULT NULL,
  `page_count_uncertain` tinyint(1) NOT NULL,
  `editing` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_editing` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `indicia_pub_not_printed` tinyint(1) NOT NULL,
  `no_brand` tinyint(1) NOT NULL,
  `isbn` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_isbn` tinyint(1) NOT NULL,
  `barcode` varchar(38) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_barcode` tinyint(1) NOT NULL,
  `rating` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_rating` tinyint(1) NOT NULL,
  `date_inferred` tinyint(1) NOT NULL,
  `after_id` int DEFAULT NULL,
  `brand_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `indicia_publisher_id` int DEFAULT NULL,
  `issue_id` int DEFAULT NULL,
  `series_id` int NOT NULL,
  `variant_of_id` int DEFAULT NULL,
  `volume_not_printed` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `indicia_printer_not_printed` tinyint(1) NOT NULL,
  `variant_cover_status` int NOT NULL,
  `indicia_printer_sourced_by` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_issue_revision_after_id_de871538_fk_gcd_issue_id` (`after_id`),
  KEY `oi_issue_revision_brand_id_4ea5d3b8_fk_gcd_brand_id` (`brand_id`),
  KEY `oi_issue_revision_changeset_id_caa51f9a_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_issue_revision_indicia_publisher_id_0d6488d1_fk_gcd_indic` (`indicia_publisher_id`),
  KEY `oi_issue_revision_issue_id_ed145702_fk_gcd_issue_id` (`issue_id`),
  KEY `oi_issue_revision_series_id_6775b98e_fk_gcd_series_id` (`series_id`),
  KEY `oi_issue_revision_variant_of_id_b8e9251d_fk_gcd_issue_id` (`variant_of_id`),
  KEY `oi_issue_revision_deleted_a6772617` (`deleted`),
  KEY `oi_issue_revision_created_b3f24c3d` (`created`),
  KEY `oi_issue_revision_modified_61fcad15` (`modified`),
  KEY `oi_issue_revision_year_on_sale_e9eccb09` (`year_on_sale`),
  KEY `oi_issue_revision_month_on_sale_bb3d7821` (`month_on_sale`),
  KEY `oi_issue_revision_day_on_sale_6f252d19` (`day_on_sale`),
  KEY `oi_issue_revision_committed_0dcbd237` (`committed`),
  KEY `oi_issue_revision_variant_cover_status_c70628f1` (`variant_cover_status`),
  CONSTRAINT `oi_issue_revision_after_id_de871538_fk_gcd_issue_id` FOREIGN KEY (`after_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `oi_issue_revision_brand_id_4ea5d3b8_fk_gcd_brand_id` FOREIGN KEY (`brand_id`) REFERENCES `gcd_brand` (`id`),
  CONSTRAINT `oi_issue_revision_changeset_id_caa51f9a_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_issue_revision_indicia_publisher_id_0d6488d1_fk_gcd_indic` FOREIGN KEY (`indicia_publisher_id`) REFERENCES `gcd_indicia_publisher` (`id`),
  CONSTRAINT `oi_issue_revision_issue_id_ed145702_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `oi_issue_revision_previous_revision_id_18214c8c_fk_oi_issue_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_issue_revision` (`id`),
  CONSTRAINT `oi_issue_revision_series_id_6775b98e_fk_gcd_series_id` FOREIGN KEY (`series_id`) REFERENCES `gcd_series` (`id`),
  CONSTRAINT `oi_issue_revision_variant_of_id_b8e9251d_fk_gcd_issue_id` FOREIGN KEY (`variant_of_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_issue_revision` WRITE;
/*!40000 ALTER TABLE `oi_issue_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_issue_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_issue_revision_brand_emblem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_issue_revision_brand_emblem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `issuerevision_id` int NOT NULL,
  `brand_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_issue_revision_brand__issuerevision_id_brand_i_c379119b_uniq` (`issuerevision_id`,`brand_id`),
  KEY `oi_issue_revision_brand_emblem_brand_id_a37cd4a4_fk_gcd_brand_id` (`brand_id`),
  CONSTRAINT `oi_issue_revision_br_issuerevision_id_36bac96e_fk_oi_issue_` FOREIGN KEY (`issuerevision_id`) REFERENCES `oi_issue_revision` (`id`),
  CONSTRAINT `oi_issue_revision_brand_emblem_brand_id_a37cd4a4_fk_gcd_brand_id` FOREIGN KEY (`brand_id`) REFERENCES `gcd_brand` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_issue_revision_brand_emblem` WRITE;
/*!40000 ALTER TABLE `oi_issue_revision_brand_emblem` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_issue_revision_brand_emblem` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_issue_revision_indicia_printer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_issue_revision_indicia_printer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `issuerevision_id` int NOT NULL,
  `indiciaprinter_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_issue_revision_indici_issuerevision_id_indicia_b5baaec3_uniq` (`issuerevision_id`,`indiciaprinter_id`),
  KEY `oi_issue_revision_in_indiciaprinter_id_cd96a7e9_fk_gcd_indic` (`indiciaprinter_id`),
  CONSTRAINT `oi_issue_revision_in_indiciaprinter_id_cd96a7e9_fk_gcd_indic` FOREIGN KEY (`indiciaprinter_id`) REFERENCES `gcd_indicia_printer` (`id`),
  CONSTRAINT `oi_issue_revision_in_issuerevision_id_0b34e563_fk_oi_issue_` FOREIGN KEY (`issuerevision_id`) REFERENCES `oi_issue_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_issue_revision_indicia_printer` WRITE;
/*!40000 ALTER TABLE `oi_issue_revision_indicia_printer` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_issue_revision_indicia_printer` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_ongoing_reservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_ongoing_reservation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `indexer_id` int NOT NULL,
  `series_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `series_id` (`series_id`),
  KEY `oi_ongoing_reservation_indexer_id_770823d2_fk_auth_user_id` (`indexer_id`),
  KEY `oi_ongoing_reservation_created_804a76c2` (`created`),
  CONSTRAINT `oi_ongoing_reservation_indexer_id_770823d2_fk_auth_user_id` FOREIGN KEY (`indexer_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `oi_ongoing_reservation_series_id_7fe9c008_fk_gcd_series_id` FOREIGN KEY (`series_id`) REFERENCES `gcd_series` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_ongoing_reservation` WRITE;
/*!40000 ALTER TABLE `oi_ongoing_reservation` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_ongoing_reservation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_ongoing_reservation_along_with`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_ongoing_reservation_along_with` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ongoingreservation_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_ongoing_reservation_a_ongoingreservation_id_us_643cb371_uniq` (`ongoingreservation_id`,`user_id`),
  KEY `oi_ongoing_reservati_user_id_28d74a05_fk_auth_user` (`user_id`),
  CONSTRAINT `oi_ongoing_reservati_ongoingreservation_i_574c89a1_fk_oi_ongoin` FOREIGN KEY (`ongoingreservation_id`) REFERENCES `oi_ongoing_reservation` (`id`),
  CONSTRAINT `oi_ongoing_reservati_user_id_28d74a05_fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_ongoing_reservation_along_with` WRITE;
/*!40000 ALTER TABLE `oi_ongoing_reservation_along_with` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_ongoing_reservation_along_with` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_ongoing_reservation_on_behalf_of`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_ongoing_reservation_on_behalf_of` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ongoingreservation_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_ongoing_reservation_o_ongoingreservation_id_us_8eda3d3f_uniq` (`ongoingreservation_id`,`user_id`),
  KEY `oi_ongoing_reservati_user_id_1798c57a_fk_auth_user` (`user_id`),
  CONSTRAINT `oi_ongoing_reservati_ongoingreservation_i_f5816016_fk_oi_ongoin` FOREIGN KEY (`ongoingreservation_id`) REFERENCES `oi_ongoing_reservation` (`id`),
  CONSTRAINT `oi_ongoing_reservati_user_id_1798c57a_fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_ongoing_reservation_on_behalf_of` WRITE;
/*!40000 ALTER TABLE `oi_ongoing_reservation_on_behalf_of` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_ongoing_reservation_on_behalf_of` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_printer_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_printer_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `country_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `printer_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_printer_revision_changeset_id_9b22597f_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_printer_revision_country_id_4db6bec9_fk_stddata_country_id` (`country_id`),
  KEY `oi_printer_revision_printer_id_7f708464_fk_gcd_printer_id` (`printer_id`),
  KEY `oi_printer_revision_deleted_b8cd8202` (`deleted`),
  KEY `oi_printer_revision_committed_c008f4f4` (`committed`),
  KEY `oi_printer_revision_created_82c2e5c3` (`created`),
  KEY `oi_printer_revision_modified_ec4bbce7` (`modified`),
  CONSTRAINT `oi_printer_revision_changeset_id_9b22597f_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_printer_revision_country_id_4db6bec9_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `oi_printer_revision_previous_revision_id_a19c5674_fk_oi_printe` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_printer_revision` (`id`),
  CONSTRAINT `oi_printer_revision_printer_id_7f708464_fk_gcd_printer_id` FOREIGN KEY (`printer_id`) REFERENCES `gcd_printer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_printer_revision` WRITE;
/*!40000 ALTER TABLE `oi_printer_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_printer_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_publisher_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_publisher_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int DEFAULT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_master` tinyint(1) NOT NULL,
  `date_inferred` tinyint(1) NOT NULL,
  `changeset_id` int NOT NULL,
  `country_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `publisher_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `year_overall_began` int DEFAULT NULL,
  `year_overall_began_uncertain` tinyint(1) NOT NULL,
  `year_overall_ended` int DEFAULT NULL,
  `year_overall_ended_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_publisher_revision_changeset_id_2bc3398c_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_publisher_revision_country_id_7b40d493_fk_stddata_country_id` (`country_id`),
  KEY `oi_publisher_revision_parent_id_d136f3b7_fk_gcd_publisher_id` (`parent_id`),
  KEY `oi_publisher_revision_publisher_id_534dffa5_fk_gcd_publisher_id` (`publisher_id`),
  KEY `oi_publisher_revision_deleted_97044e97` (`deleted`),
  KEY `oi_publisher_revision_created_fcda2c3c` (`created`),
  KEY `oi_publisher_revision_modified_5df32242` (`modified`),
  KEY `oi_publisher_revision_is_master_2ca4c580` (`is_master`),
  KEY `oi_publisher_revision_committed_3e865bb6` (`committed`),
  CONSTRAINT `oi_publisher_revisio_previous_revision_id_b59fb69d_fk_oi_publis` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_publisher_revision` (`id`),
  CONSTRAINT `oi_publisher_revision_changeset_id_2bc3398c_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_publisher_revision_country_id_7b40d493_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `oi_publisher_revision_parent_id_d136f3b7_fk_gcd_publisher_id` FOREIGN KEY (`parent_id`) REFERENCES `gcd_publisher` (`id`),
  CONSTRAINT `oi_publisher_revision_publisher_id_534dffa5_fk_gcd_publisher_id` FOREIGN KEY (`publisher_id`) REFERENCES `gcd_publisher` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_publisher_revision` WRITE;
/*!40000 ALTER TABLE `oi_publisher_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_publisher_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_received_award_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_received_award_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `object_id` int unsigned DEFAULT NULL,
  `award_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_award_name` tinyint(1) NOT NULL,
  `award_year` smallint unsigned DEFAULT NULL,
  `award_year_uncertain` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `award_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `received_award_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_received_award_revision_award_id_dc610944_fk_gcd_award_id` (`award_id`),
  KEY `oi_received_award_re_changeset_id_c19fa584_fk_oi_change` (`changeset_id`),
  KEY `oi_received_award_re_content_type_id_7f2e505d_fk_django_co` (`content_type_id`),
  KEY `oi_received_award_re_received_award_id_90618da3_fk_gcd_recei` (`received_award_id`),
  KEY `oi_received_award_revision_deleted_29159e99` (`deleted`),
  KEY `oi_received_award_revision_committed_81112be0` (`committed`),
  KEY `oi_received_award_revision_created_7f3856c7` (`created`),
  KEY `oi_received_award_revision_modified_2cde743d` (`modified`),
  CONSTRAINT `oi_received_award_re_changeset_id_c19fa584_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_received_award_re_content_type_id_7f2e505d_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `oi_received_award_re_previous_revision_id_cf7392f0_fk_oi_receiv` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_received_award_revision` (`id`),
  CONSTRAINT `oi_received_award_re_received_award_id_90618da3_fk_gcd_recei` FOREIGN KEY (`received_award_id`) REFERENCES `gcd_received_award` (`id`),
  CONSTRAINT `oi_received_award_revision_award_id_dc610944_fk_gcd_award_id` FOREIGN KEY (`award_id`) REFERENCES `gcd_award` (`id`),
  CONSTRAINT `oi_received_award_revision_chk_1` CHECK ((`object_id` >= 0)),
  CONSTRAINT `oi_received_award_revision_chk_2` CHECK ((`award_year` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_received_award_revision` WRITE;
/*!40000 ALTER TABLE `oi_received_award_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_received_award_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_reprint_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_reprint_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `origin_issue_id` int DEFAULT NULL,
  `origin_revision_id` int DEFAULT NULL,
  `origin_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `reprint_id` int DEFAULT NULL,
  `target_issue_id` int DEFAULT NULL,
  `target_revision_id` int DEFAULT NULL,
  `target_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_reprint_revision_origin_revision_id_ae30303e_fk_oi_story_` (`origin_revision_id`),
  KEY `oi_reprint_revision_reprint_id_31f0686a_fk_gcd_reprint_id` (`reprint_id`),
  KEY `oi_reprint_revision_target_issue_id_d08d4b50_fk_gcd_issue_id` (`target_issue_id`),
  KEY `oi_reprint_revision_target_revision_id_84cff02c_fk_oi_story_` (`target_revision_id`),
  KEY `oi_reprint_revision_changeset_id_4ebeac7a_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_reprint_revision_origin_issue_id_4f21d8e7_fk_gcd_issue_id` (`origin_issue_id`),
  KEY `oi_reprint_revision_deleted_e78328ea` (`deleted`),
  KEY `oi_reprint_revision_created_f79447e2` (`created`),
  KEY `oi_reprint_revision_modified_68c60f55` (`modified`),
  KEY `oi_reprint_revision_committed_64aa3700` (`committed`),
  KEY `oi_reprint_revision_origin_id_e979a6e3_fk_gcd_story_id` (`origin_id`),
  KEY `oi_reprint_revision_target_id_0af97a2f_fk_gcd_story_id` (`target_id`),
  CONSTRAINT `oi_reprint_revision_changeset_id_4ebeac7a_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_reprint_revision_origin_id_e979a6e3_fk_gcd_story_id` FOREIGN KEY (`origin_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `oi_reprint_revision_origin_issue_id_4f21d8e7_fk_gcd_issue_id` FOREIGN KEY (`origin_issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `oi_reprint_revision_origin_revision_id_ae30303e_fk_oi_story_` FOREIGN KEY (`origin_revision_id`) REFERENCES `oi_story_revision` (`id`),
  CONSTRAINT `oi_reprint_revision_previous_revision_id_47aa608b_fk_oi_reprin` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_reprint_revision` (`id`),
  CONSTRAINT `oi_reprint_revision_reprint_id_31f0686a_fk_gcd_reprint_id` FOREIGN KEY (`reprint_id`) REFERENCES `gcd_reprint` (`id`),
  CONSTRAINT `oi_reprint_revision_target_id_0af97a2f_fk_gcd_story_id` FOREIGN KEY (`target_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `oi_reprint_revision_target_issue_id_d08d4b50_fk_gcd_issue_id` FOREIGN KEY (`target_issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `oi_reprint_revision_target_revision_id_84cff02c_fk_oi_story_` FOREIGN KEY (`target_revision_id`) REFERENCES `oi_story_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_reprint_revision` WRITE;
/*!40000 ALTER TABLE `oi_reprint_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_reprint_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_revision_lock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_revision_lock` (
  `id` int NOT NULL AUTO_INCREMENT,
  `object_id` int NOT NULL,
  `changeset_id` int DEFAULT NULL,
  `content_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_revision_lock_content_type_id_object_id_e37882b2_uniq` (`content_type_id`,`object_id`),
  KEY `oi_revision_lock_changeset_id_558b8deb_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_revision_lock_object_id_9879dd87` (`object_id`),
  CONSTRAINT `oi_revision_lock_changeset_id_558b8deb_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_revision_lock_content_type_id_81196190_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_revision_lock` WRITE;
/*!40000 ALTER TABLE `oi_revision_lock` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_revision_lock` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_series_bond_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_series_bond_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `bond_type_id` int DEFAULT NULL,
  `changeset_id` int NOT NULL,
  `origin_id` int DEFAULT NULL,
  `origin_issue_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `series_bond_id` int DEFAULT NULL,
  `target_id` int DEFAULT NULL,
  `target_issue_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_series_bond_revis_bond_type_id_4c69f273_fk_gcd_serie` (`bond_type_id`),
  KEY `oi_series_bond_revision_changeset_id_ef2e4a27_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_series_bond_revision_origin_id_8b4ed322_fk_gcd_series_id` (`origin_id`),
  KEY `oi_series_bond_revision_origin_issue_id_46aab260_fk_gcd_issue_id` (`origin_issue_id`),
  KEY `oi_series_bond_revis_series_bond_id_a0ba1bb9_fk_gcd_serie` (`series_bond_id`),
  KEY `oi_series_bond_revision_target_id_130d15b8_fk_gcd_series_id` (`target_id`),
  KEY `oi_series_bond_revision_target_issue_id_57a2be4d_fk_gcd_issue_id` (`target_issue_id`),
  KEY `oi_series_bond_revision_deleted_8d539f45` (`deleted`),
  KEY `oi_series_bond_revision_created_277ef5fb` (`created`),
  KEY `oi_series_bond_revision_modified_87cdf8ac` (`modified`),
  KEY `oi_series_bond_revision_committed_84bb1060` (`committed`),
  CONSTRAINT `oi_series_bond_revis_bond_type_id_4c69f273_fk_gcd_serie` FOREIGN KEY (`bond_type_id`) REFERENCES `gcd_series_bond_type` (`id`),
  CONSTRAINT `oi_series_bond_revis_previous_revision_id_301b9018_fk_oi_series` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_series_bond_revision` (`id`),
  CONSTRAINT `oi_series_bond_revis_series_bond_id_a0ba1bb9_fk_gcd_serie` FOREIGN KEY (`series_bond_id`) REFERENCES `gcd_series_bond` (`id`),
  CONSTRAINT `oi_series_bond_revision_changeset_id_ef2e4a27_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_series_bond_revision_origin_id_8b4ed322_fk_gcd_series_id` FOREIGN KEY (`origin_id`) REFERENCES `gcd_series` (`id`),
  CONSTRAINT `oi_series_bond_revision_origin_issue_id_46aab260_fk_gcd_issue_id` FOREIGN KEY (`origin_issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `oi_series_bond_revision_target_id_130d15b8_fk_gcd_series_id` FOREIGN KEY (`target_id`) REFERENCES `gcd_series` (`id`),
  CONSTRAINT `oi_series_bond_revision_target_issue_id_57a2be4d_fk_gcd_issue_id` FOREIGN KEY (`target_issue_id`) REFERENCES `gcd_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_series_bond_revision` WRITE;
/*!40000 ALTER TABLE `oi_series_bond_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_series_bond_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_series_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_series_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `reservation_requested` tinyint(1) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `leading_article` tinyint(1) NOT NULL,
  `format` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dimensions` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `paper_stock` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `binding` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `publishing_format` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_began` int NOT NULL,
  `year_ended` int DEFAULT NULL,
  `year_began_uncertain` tinyint(1) NOT NULL,
  `year_ended_uncertain` tinyint(1) NOT NULL,
  `is_current` tinyint(1) NOT NULL,
  `publication_notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `tracking_notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `has_barcode` tinyint(1) NOT NULL,
  `has_indicia_frequency` tinyint(1) NOT NULL,
  `has_isbn` tinyint(1) NOT NULL,
  `has_issue_title` tinyint(1) NOT NULL,
  `has_volume` tinyint(1) NOT NULL,
  `has_rating` tinyint(1) NOT NULL,
  `is_comics_publication` tinyint(1) NOT NULL,
  `is_singleton` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_inferred` tinyint(1) NOT NULL,
  `changeset_id` int NOT NULL,
  `country_id` int NOT NULL,
  `imprint_id` int DEFAULT NULL,
  `language_id` int NOT NULL,
  `publication_type_id` int DEFAULT NULL,
  `publisher_id` int NOT NULL,
  `series_id` int DEFAULT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `has_about_comics` tinyint(1) NOT NULL,
  `has_indicia_printer` tinyint(1) NOT NULL,
  `has_publisher_code_number` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_series_revision_changeset_id_4812c476_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_series_revision_country_id_8758e07c_fk_stddata_country_id` (`country_id`),
  KEY `oi_series_revision_imprint_id_c608dcf9_fk_gcd_publisher_id` (`imprint_id`),
  KEY `oi_series_revision_language_id_20909836_fk_stddata_language_id` (`language_id`),
  KEY `oi_series_revision_publication_type_id_01f571b4_fk_gcd_serie` (`publication_type_id`),
  KEY `oi_series_revision_publisher_id_36387475_fk_gcd_publisher_id` (`publisher_id`),
  KEY `oi_series_revision_series_id_7afe7cf5_fk_gcd_series_id` (`series_id`),
  KEY `oi_series_revision_deleted_2cb5f47d` (`deleted`),
  KEY `oi_series_revision_created_02a62f74` (`created`),
  KEY `oi_series_revision_modified_6bf6583b` (`modified`),
  KEY `oi_series_revision_committed_eb5dd8f4` (`committed`),
  CONSTRAINT `oi_series_revision_changeset_id_4812c476_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_series_revision_country_id_8758e07c_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `oi_series_revision_imprint_id_c608dcf9_fk_gcd_publisher_id` FOREIGN KEY (`imprint_id`) REFERENCES `gcd_publisher` (`id`),
  CONSTRAINT `oi_series_revision_language_id_20909836_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `oi_series_revision_previous_revision_id_0e67f39d_fk_oi_series` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_series_revision` (`id`),
  CONSTRAINT `oi_series_revision_publication_type_id_01f571b4_fk_gcd_serie` FOREIGN KEY (`publication_type_id`) REFERENCES `gcd_series_publication_type` (`id`),
  CONSTRAINT `oi_series_revision_publisher_id_36387475_fk_gcd_publisher_id` FOREIGN KEY (`publisher_id`) REFERENCES `gcd_publisher` (`id`),
  CONSTRAINT `oi_series_revision_series_id_7afe7cf5_fk_gcd_series_id` FOREIGN KEY (`series_id`) REFERENCES `gcd_series` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_series_revision` WRITE;
/*!40000 ALTER TABLE `oi_series_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_series_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_arc_relation_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_arc_relation_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `from_story_arc_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `relation_type_id` int NOT NULL,
  `story_arc_relation_id` int DEFAULT NULL,
  `to_story_arc_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_story_arc_relatio_changeset_id_cab21555_fk_oi_change` (`changeset_id`),
  KEY `oi_story_arc_relatio_from_story_arc_id_c3a78f05_fk_gcd_story` (`from_story_arc_id`),
  KEY `oi_story_arc_relatio_relation_type_id_d86a49fc_fk_gcd_story` (`relation_type_id`),
  KEY `oi_story_arc_relatio_story_arc_relation_i_5318da83_fk_gcd_story` (`story_arc_relation_id`),
  KEY `oi_story_arc_relatio_to_story_arc_id_8731fc73_fk_gcd_story` (`to_story_arc_id`),
  KEY `oi_story_arc_relation_revision_deleted_0e456f97` (`deleted`),
  KEY `oi_story_arc_relation_revision_committed_e080f978` (`committed`),
  KEY `oi_story_arc_relation_revision_created_fef08cec` (`created`),
  KEY `oi_story_arc_relation_revision_modified_6551296f` (`modified`),
  CONSTRAINT `oi_story_arc_relatio_changeset_id_cab21555_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_story_arc_relatio_from_story_arc_id_c3a78f05_fk_gcd_story` FOREIGN KEY (`from_story_arc_id`) REFERENCES `gcd_story_arc` (`id`),
  CONSTRAINT `oi_story_arc_relatio_previous_revision_id_a52faa2b_fk_oi_story_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_story_arc_relation_revision` (`id`),
  CONSTRAINT `oi_story_arc_relatio_relation_type_id_d86a49fc_fk_gcd_story` FOREIGN KEY (`relation_type_id`) REFERENCES `gcd_story_arc_relation_type` (`id`),
  CONSTRAINT `oi_story_arc_relatio_story_arc_relation_i_5318da83_fk_gcd_story` FOREIGN KEY (`story_arc_relation_id`) REFERENCES `gcd_story_arc_relation` (`id`),
  CONSTRAINT `oi_story_arc_relatio_to_story_arc_id_8731fc73_fk_gcd_story` FOREIGN KEY (`to_story_arc_id`) REFERENCES `gcd_story_arc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_arc_relation_revision` WRITE;
/*!40000 ALTER TABLE `oi_story_arc_relation_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_arc_relation_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_arc_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_arc_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `leading_article` tinyint(1) NOT NULL,
  `disambiguation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `language_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `story_arc_id` int DEFAULT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_story_arc_revision_changeset_id_2f02e0ff_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_story_arc_revisio_language_id_f6ebb9f6_fk_stddata_l` (`language_id`),
  KEY `oi_story_arc_revision_story_arc_id_7d08a010_fk_gcd_story_arc_id` (`story_arc_id`),
  KEY `oi_story_arc_revision_deleted_d73e124a` (`deleted`),
  KEY `oi_story_arc_revision_committed_5d500bbb` (`committed`),
  KEY `oi_story_arc_revision_created_c0f7465d` (`created`),
  KEY `oi_story_arc_revision_modified_f484e185` (`modified`),
  KEY `oi_story_arc_revision_disambiguation_d9aff4e5` (`disambiguation`),
  KEY `oi_story_arc_revision_year_first_published_2c81d1f4` (`year_first_published`),
  CONSTRAINT `oi_story_arc_revisio_language_id_f6ebb9f6_fk_stddata_l` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`),
  CONSTRAINT `oi_story_arc_revisio_previous_revision_id_874c695c_fk_oi_story_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_story_arc_revision` (`id`),
  CONSTRAINT `oi_story_arc_revision_changeset_id_2f02e0ff_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_story_arc_revision_story_arc_id_7d08a010_fk_gcd_story_arc_id` FOREIGN KEY (`story_arc_id`) REFERENCES `gcd_story_arc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_arc_revision` WRITE;
/*!40000 ALTER TABLE `oi_story_arc_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_arc_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_character_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_character_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `is_flashback` tinyint(1) NOT NULL,
  `is_origin` tinyint(1) NOT NULL,
  `is_death` tinyint(1) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `character_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `story_character_id` int DEFAULT NULL,
  `story_revision_id` int NOT NULL,
  `universe_id` int DEFAULT NULL,
  `group_universe_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_story_character_r_changeset_id_41795b23_fk_oi_change` (`changeset_id`),
  KEY `oi_story_character_r_character_id_2e5fed89_fk_gcd_chara` (`character_id`),
  KEY `oi_story_character_r_role_id_8bbd5c79_fk_gcd_chara` (`role_id`),
  KEY `oi_story_character_r_story_character_id_66306bb0_fk_gcd_story` (`story_character_id`),
  KEY `oi_story_character_r_story_revision_id_177e6329_fk_oi_story_` (`story_revision_id`),
  KEY `oi_story_character_revision_deleted_0d36b786` (`deleted`),
  KEY `oi_story_character_revision_committed_121acbf2` (`committed`),
  KEY `oi_story_character_revision_created_c2adfc58` (`created`),
  KEY `oi_story_character_revision_modified_8e455bf8` (`modified`),
  KEY `oi_story_character_r_universe_id_add102c5_fk_gcd_unive` (`universe_id`),
  KEY `oi_story_character_r_group_universe_id_e892067b_fk_gcd_unive` (`group_universe_id`),
  CONSTRAINT `oi_story_character_r_changeset_id_41795b23_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_story_character_r_character_id_2e5fed89_fk_gcd_chara` FOREIGN KEY (`character_id`) REFERENCES `gcd_character_name_detail` (`id`),
  CONSTRAINT `oi_story_character_r_group_universe_id_e892067b_fk_gcd_unive` FOREIGN KEY (`group_universe_id`) REFERENCES `gcd_universe` (`id`),
  CONSTRAINT `oi_story_character_r_previous_revision_id_357e421f_fk_oi_story_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_story_character_revision` (`id`),
  CONSTRAINT `oi_story_character_r_role_id_8bbd5c79_fk_gcd_chara` FOREIGN KEY (`role_id`) REFERENCES `gcd_character_role` (`id`),
  CONSTRAINT `oi_story_character_r_story_character_id_66306bb0_fk_gcd_story` FOREIGN KEY (`story_character_id`) REFERENCES `gcd_story_character` (`id`),
  CONSTRAINT `oi_story_character_r_story_revision_id_177e6329_fk_oi_story_` FOREIGN KEY (`story_revision_id`) REFERENCES `oi_story_revision` (`id`),
  CONSTRAINT `oi_story_character_r_universe_id_add102c5_fk_gcd_unive` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_character_revision` WRITE;
/*!40000 ALTER TABLE `oi_story_character_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_character_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_character_revision_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_character_revision_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storycharacterrevision_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_story_character_revis_storycharacterrevision_i_cae116ba_uniq` (`storycharacterrevision_id`,`group_id`),
  KEY `oi_story_character_r_group_id_98155fb0_fk_gcd_group` (`group_id`),
  CONSTRAINT `oi_story_character_r_group_id_98155fb0_fk_gcd_group` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`),
  CONSTRAINT `oi_story_character_r_storycharacterrevisi_cc3ec1f8_fk_oi_story_` FOREIGN KEY (`storycharacterrevision_id`) REFERENCES `oi_story_character_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_character_revision_group` WRITE;
/*!40000 ALTER TABLE `oi_story_character_revision_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_character_revision_group` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_character_revision_group_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_character_revision_group_name` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storycharacterrevision_id` int NOT NULL,
  `groupnamedetail_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_story_character_revis_storycharacterrevision_i_943e766f_uniq` (`storycharacterrevision_id`,`groupnamedetail_id`),
  KEY `oi_story_character_r_groupnamedetail_id_67f92951_fk_gcd_group` (`groupnamedetail_id`),
  CONSTRAINT `oi_story_character_r_groupnamedetail_id_67f92951_fk_gcd_group` FOREIGN KEY (`groupnamedetail_id`) REFERENCES `gcd_group_name_detail` (`id`),
  CONSTRAINT `oi_story_character_r_storycharacterrevisi_893d3534_fk_oi_story_` FOREIGN KEY (`storycharacterrevision_id`) REFERENCES `oi_story_character_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_character_revision_group_name` WRITE;
/*!40000 ALTER TABLE `oi_story_character_revision_group_name` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_character_revision_group_name` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_credit_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_credit_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `is_credited` tinyint(1) NOT NULL,
  `is_signed` tinyint(1) NOT NULL,
  `uncertain` tinyint(1) NOT NULL,
  `signed_as` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credited_as` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credit_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `credit_type_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `story_revision_id` int NOT NULL,
  `story_credit_id` int DEFAULT NULL,
  `signature_id` int DEFAULT NULL,
  `is_sourced` tinyint(1) NOT NULL,
  `sourced_by` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_story_credit_revi_changeset_id_68350477_fk_oi_change` (`changeset_id`),
  KEY `oi_story_credit_revi_creator_id_c8d6ae94_fk_gcd_creat` (`creator_id`),
  KEY `oi_story_credit_revi_credit_type_id_e36f27b9_fk_gcd_credi` (`credit_type_id`),
  KEY `oi_story_credit_revi_story_revision_id_7c2e4ca8_fk_oi_story_` (`story_revision_id`),
  KEY `oi_story_credit_revi_story_credit_id_be5b4a8a_fk_gcd_story` (`story_credit_id`),
  KEY `oi_story_credit_revision_deleted_7b16cd90` (`deleted`),
  KEY `oi_story_credit_revision_committed_c3d4a156` (`committed`),
  KEY `oi_story_credit_revision_created_3857529d` (`created`),
  KEY `oi_story_credit_revision_modified_8127e80e` (`modified`),
  KEY `oi_story_credit_revision_is_credited_7e5de410` (`is_credited`),
  KEY `oi_story_credit_revision_is_signed_80685b17` (`is_signed`),
  KEY `oi_story_credit_revision_uncertain_d3ecf0ff` (`uncertain`),
  KEY `oi_story_credit_revi_signature_id_bed7fb8a_fk_gcd_creat` (`signature_id`),
  KEY `oi_story_credit_revision_is_sourced_07a98329` (`is_sourced`),
  CONSTRAINT `oi_story_credit_revi_changeset_id_68350477_fk_oi_change` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_story_credit_revi_creator_id_c8d6ae94_fk_gcd_creat` FOREIGN KEY (`creator_id`) REFERENCES `gcd_creator_name_detail` (`id`),
  CONSTRAINT `oi_story_credit_revi_credit_type_id_e36f27b9_fk_gcd_credi` FOREIGN KEY (`credit_type_id`) REFERENCES `gcd_credit_type` (`id`),
  CONSTRAINT `oi_story_credit_revi_previous_revision_id_ea3c0e29_fk_oi_story_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_story_credit_revision` (`id`),
  CONSTRAINT `oi_story_credit_revi_signature_id_bed7fb8a_fk_gcd_creat` FOREIGN KEY (`signature_id`) REFERENCES `gcd_creator_signature` (`id`),
  CONSTRAINT `oi_story_credit_revi_story_credit_id_be5b4a8a_fk_gcd_story` FOREIGN KEY (`story_credit_id`) REFERENCES `gcd_story_credit` (`id`),
  CONSTRAINT `oi_story_credit_revi_story_revision_id_7c2e4ca8_fk_oi_story_` FOREIGN KEY (`story_revision_id`) REFERENCES `oi_story_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_credit_revision` WRITE;
/*!40000 ALTER TABLE `oi_story_credit_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_credit_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_group_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_group_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `group_id` int DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `story_group_id` int DEFAULT NULL,
  `story_revision_id` int NOT NULL,
  `universe_id` int DEFAULT NULL,
  `group_name_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_story_group_revision_changeset_id_aecb2c11_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_story_group_revis_story_group_id_019b0ffa_fk_gcd_group` (`story_group_id`),
  KEY `oi_story_group_revis_story_revision_id_8dd1ded6_fk_oi_story_` (`story_revision_id`),
  KEY `oi_story_group_revision_deleted_34ace785` (`deleted`),
  KEY `oi_story_group_revision_committed_7d728b78` (`committed`),
  KEY `oi_story_group_revision_created_03faaead` (`created`),
  KEY `oi_story_group_revision_modified_57186f40` (`modified`),
  KEY `oi_story_group_revision_universe_id_dfc7024d_fk_gcd_universe_id` (`universe_id`),
  KEY `oi_story_group_revis_group_name_id_87a40e0d_fk_gcd_group` (`group_name_id`),
  KEY `oi_story_group_revision_group_id_5a01a70c_fk_gcd_group_id` (`group_id`),
  CONSTRAINT `oi_story_group_revis_group_name_id_87a40e0d_fk_gcd_group` FOREIGN KEY (`group_name_id`) REFERENCES `gcd_group_name_detail` (`id`),
  CONSTRAINT `oi_story_group_revis_previous_revision_id_11523c35_fk_oi_story_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_story_group_revision` (`id`),
  CONSTRAINT `oi_story_group_revis_story_group_id_019b0ffa_fk_gcd_group` FOREIGN KEY (`story_group_id`) REFERENCES `gcd_group_character` (`id`),
  CONSTRAINT `oi_story_group_revis_story_revision_id_8dd1ded6_fk_oi_story_` FOREIGN KEY (`story_revision_id`) REFERENCES `oi_story_revision` (`id`),
  CONSTRAINT `oi_story_group_revision_changeset_id_aecb2c11_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_story_group_revision_group_id_5a01a70c_fk_gcd_group_id` FOREIGN KEY (`group_id`) REFERENCES `gcd_group` (`id`),
  CONSTRAINT `oi_story_group_revision_universe_id_dfc7024d_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_group_revision` WRITE;
/*!40000 ALTER TABLE `oi_story_group_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_group_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_inferred` tinyint(1) NOT NULL,
  `feature` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sequence_number` int NOT NULL,
  `page_count` decimal(10,3) DEFAULT NULL,
  `page_count_uncertain` tinyint(1) NOT NULL,
  `script` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `pencils` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `inks` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `colors` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `letters` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `editing` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `no_script` tinyint(1) NOT NULL,
  `no_pencils` tinyint(1) NOT NULL,
  `no_inks` tinyint(1) NOT NULL,
  `no_colors` tinyint(1) NOT NULL,
  `no_letters` tinyint(1) NOT NULL,
  `no_editing` tinyint(1) NOT NULL,
  `job_number` varchar(25) COLLATE utf8mb4_unicode_ci NOT NULL,
  `genre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `characters` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `synopsis` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `reprint_notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_inferred` tinyint(1) NOT NULL,
  `changeset_id` int NOT NULL,
  `issue_id` int DEFAULT NULL,
  `story_id` int DEFAULT NULL,
  `type_id` int NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `first_line` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_story_revision_changeset_id_2417deb0_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_story_revision_issue_id_0bd5240c_fk_gcd_issue_id` (`issue_id`),
  KEY `oi_story_revision_story_id_7247055c_fk_gcd_story_id` (`story_id`),
  KEY `oi_story_revision_type_id_4455ead0_fk_gcd_story_type_id` (`type_id`),
  KEY `oi_story_revision_deleted_6faf4955` (`deleted`),
  KEY `oi_story_revision_created_f180d7eb` (`created`),
  KEY `oi_story_revision_modified_e6bc0134` (`modified`),
  KEY `oi_story_revision_committed_635386df` (`committed`),
  CONSTRAINT `oi_story_revision_changeset_id_2417deb0_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_story_revision_issue_id_0bd5240c_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `oi_story_revision_previous_revision_id_cb61c354_fk_oi_story_` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_story_revision` (`id`),
  CONSTRAINT `oi_story_revision_story_id_7247055c_fk_gcd_story_id` FOREIGN KEY (`story_id`) REFERENCES `gcd_story` (`id`),
  CONSTRAINT `oi_story_revision_type_id_4455ead0_fk_gcd_story_type_id` FOREIGN KEY (`type_id`) REFERENCES `gcd_story_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_revision` WRITE;
/*!40000 ALTER TABLE `oi_story_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_revision_feature_logo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_revision_feature_logo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storyrevision_id` int NOT NULL,
  `featurelogo_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_story_revision_featur_storyrevision_id_feature_3682daa1_uniq` (`storyrevision_id`,`featurelogo_id`),
  KEY `oi_story_revision_fe_featurelogo_id_1491d5ea_fk_gcd_featu` (`featurelogo_id`),
  CONSTRAINT `oi_story_revision_fe_featurelogo_id_1491d5ea_fk_gcd_featu` FOREIGN KEY (`featurelogo_id`) REFERENCES `gcd_feature_logo` (`id`),
  CONSTRAINT `oi_story_revision_fe_storyrevision_id_a68ffa5f_fk_oi_story_` FOREIGN KEY (`storyrevision_id`) REFERENCES `oi_story_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_revision_feature_logo` WRITE;
/*!40000 ALTER TABLE `oi_story_revision_feature_logo` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_revision_feature_logo` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_revision_feature_object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_revision_feature_object` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storyrevision_id` int NOT NULL,
  `feature_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_story_revision_featur_storyrevision_id_feature_d7f06bb2_uniq` (`storyrevision_id`,`feature_id`),
  KEY `oi_story_revision_fe_feature_id_d1807166_fk_gcd_featu` (`feature_id`),
  CONSTRAINT `oi_story_revision_fe_feature_id_d1807166_fk_gcd_featu` FOREIGN KEY (`feature_id`) REFERENCES `gcd_feature` (`id`),
  CONSTRAINT `oi_story_revision_fe_storyrevision_id_edcb3639_fk_oi_story_` FOREIGN KEY (`storyrevision_id`) REFERENCES `oi_story_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_revision_feature_object` WRITE;
/*!40000 ALTER TABLE `oi_story_revision_feature_object` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_revision_feature_object` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_revision_story_arc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_revision_story_arc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storyrevision_id` int NOT NULL,
  `storyarc_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_story_revision_story__storyrevision_id_storyar_1281b1f2_uniq` (`storyrevision_id`,`storyarc_id`),
  KEY `oi_story_revision_st_storyarc_id_0ae698e3_fk_gcd_story` (`storyarc_id`),
  CONSTRAINT `oi_story_revision_st_storyarc_id_0ae698e3_fk_gcd_story` FOREIGN KEY (`storyarc_id`) REFERENCES `gcd_story_arc` (`id`),
  CONSTRAINT `oi_story_revision_st_storyrevision_id_aafb0711_fk_oi_story_` FOREIGN KEY (`storyrevision_id`) REFERENCES `oi_story_revision` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_revision_story_arc` WRITE;
/*!40000 ALTER TABLE `oi_story_revision_story_arc` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_revision_story_arc` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_story_revision_universe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_story_revision_universe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `storyrevision_id` int NOT NULL,
  `universe_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oi_story_revision_univer_storyrevision_id_univers_e04a21be_uniq` (`storyrevision_id`,`universe_id`),
  KEY `oi_story_revision_un_universe_id_4a8fb173_fk_gcd_unive` (`universe_id`),
  CONSTRAINT `oi_story_revision_un_storyrevision_id_940962a2_fk_oi_story_` FOREIGN KEY (`storyrevision_id`) REFERENCES `oi_story_revision` (`id`),
  CONSTRAINT `oi_story_revision_un_universe_id_4a8fb173_fk_gcd_unive` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_story_revision_universe` WRITE;
/*!40000 ALTER TABLE `oi_story_revision_universe` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_story_revision_universe` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `oi_universe_revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oi_universe_revision` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deleted` tinyint(1) NOT NULL,
  `committed` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  `multiverse` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `designation` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_first_published` int DEFAULT NULL,
  `year_first_published_uncertain` tinyint(1) NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `changeset_id` int NOT NULL,
  `previous_revision_id` int DEFAULT NULL,
  `universe_id` int DEFAULT NULL,
  `verse_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `previous_revision_id` (`previous_revision_id`),
  KEY `oi_universe_revision_changeset_id_5f9f431b_fk_oi_changeset_id` (`changeset_id`),
  KEY `oi_universe_revision_universe_id_d427acaa_fk_gcd_universe_id` (`universe_id`),
  KEY `oi_universe_revision_deleted_3e0e5a74` (`deleted`),
  KEY `oi_universe_revision_committed_d69c0220` (`committed`),
  KEY `oi_universe_revision_created_ed898b0d` (`created`),
  KEY `oi_universe_revision_modified_1a130423` (`modified`),
  KEY `oi_universe_revision_multiverse_b24c7382` (`multiverse`),
  KEY `oi_universe_revision_name_ee589703` (`name`),
  KEY `oi_universe_revision_designation_a090170d` (`designation`),
  KEY `oi_universe_revision_year_first_published_ecff69aa` (`year_first_published`),
  KEY `oi_universe_revision_verse_id_63a52085_fk_gcd_multiverse_id` (`verse_id`),
  CONSTRAINT `oi_universe_revision_changeset_id_5f9f431b_fk_oi_changeset_id` FOREIGN KEY (`changeset_id`) REFERENCES `oi_changeset` (`id`),
  CONSTRAINT `oi_universe_revision_previous_revision_id_e20447ef_fk_oi_univer` FOREIGN KEY (`previous_revision_id`) REFERENCES `oi_universe_revision` (`id`),
  CONSTRAINT `oi_universe_revision_universe_id_d427acaa_fk_gcd_universe_id` FOREIGN KEY (`universe_id`) REFERENCES `gcd_universe` (`id`),
  CONSTRAINT `oi_universe_revision_verse_id_63a52085_fk_gcd_multiverse_id` FOREIGN KEY (`verse_id`) REFERENCES `gcd_multiverse` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `oi_universe_revision` WRITE;
/*!40000 ALTER TABLE `oi_universe_revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oi_universe_revision` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stats_count_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stats_count_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `count` int NOT NULL,
  `country_id` int DEFAULT NULL,
  `language_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stats_count_stats_country_id_cc9819eb_fk_stddata_country_id` (`country_id`),
  KEY `stats_count_stats_language_id_0a03ceac_fk_stddata_language_id` (`language_id`),
  KEY `stats_count_stats_name_7f14e915` (`name`),
  CONSTRAINT `stats_count_stats_country_id_cc9819eb_fk_stddata_country_id` FOREIGN KEY (`country_id`) REFERENCES `stddata_country` (`id`),
  CONSTRAINT `stats_count_stats_language_id_0a03ceac_fk_stddata_language_id` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stats_count_stats` WRITE;
/*!40000 ALTER TABLE `stats_count_stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `stats_count_stats` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stats_download`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stats_download` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `stats_download_user_id_6d9ef08b_fk_auth_user_id` (`user_id`),
  CONSTRAINT `stats_download_user_id_6d9ef08b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stats_download` WRITE;
/*!40000 ALTER TABLE `stats_download` DISABLE KEYS */;
/*!40000 ALTER TABLE `stats_download` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stats_recent_indexed_issue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stats_recent_indexed_issue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `issue_id` int NOT NULL,
  `language_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stats_recent_indexed_issue_issue_id_dd3c8a8b_fk_gcd_issue_id` (`issue_id`),
  KEY `stats_recent_indexed_language_id_f7c30f35_fk_stddata_l` (`language_id`),
  KEY `stats_recent_indexed_issue_created_98c45864` (`created`),
  CONSTRAINT `stats_recent_indexed_issue_issue_id_dd3c8a8b_fk_gcd_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `gcd_issue` (`id`),
  CONSTRAINT `stats_recent_indexed_language_id_f7c30f35_fk_stddata_l` FOREIGN KEY (`language_id`) REFERENCES `stddata_language` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stats_recent_indexed_issue` WRITE;
/*!40000 ALTER TABLE `stats_recent_indexed_issue` DISABLE KEYS */;
/*!40000 ALTER TABLE `stats_recent_indexed_issue` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stddata_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stddata_country` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `stddata_country_name_02e6d67b` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=250 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stddata_country` WRITE;
/*!40000 ALTER TABLE `stddata_country` DISABLE KEYS */;
INSERT INTO `stddata_country` VALUES (1,'ad','Andorra'),(2,'ae','United Arab Emirates'),(3,'af','Afghanistan'),(4,'ag','Antigua and Barbuda'),(5,'ai','Anguilla'),(6,'al','Albania'),(7,'am','Armenia'),(8,'an','Netherlands Antilles'),(9,'ao','Angola'),(10,'aq','Antarctica'),(11,'ar','Argentina'),(12,'as','American Samoa'),(13,'at','Austria'),(14,'au','Australia'),(15,'aw','Aruba'),(16,'az','Azerbaijan'),(17,'ba','Bosnia and Herzegovina'),(18,'bb','Barbados'),(19,'bd','Bangladesh'),(20,'be','Belgium'),(21,'bf','Burkina Faso'),(22,'bg','Bulgaria'),(23,'bh','Bahrain'),(24,'bi','Burundi'),(25,'bj','Benin'),(26,'bm','Bermuda'),(27,'bn','Brunei Darussalam'),(28,'bo','Bolivia'),(29,'br','Brazil'),(30,'bs','Bahamas'),(31,'bt','Bhutan'),(32,'bv','Bouvet Island'),(33,'bw','Botswana'),(34,'by','Belarus'),(35,'bz','Belize'),(36,'ca','Canada'),(37,'cc','Cocos (Keeling) Islands'),(38,'cf','Central African Republic'),(39,'cg','Congo'),(40,'ch','Switzerland'),(41,'ci','Cote D\'Ivoire (Ivory Coast)'),(42,'ck','Cook Islands'),(43,'cl','Chile'),(44,'cm','Cameroon'),(45,'cn','China'),(46,'co','Colombia'),(47,'cr','Costa Rica'),(48,'cshh','Czechoslovakia (former)'),(49,'cu','Cuba'),(50,'cv','Cape Verde'),(51,'cx','Christmas Island'),(52,'cy','Cyprus'),(53,'cz','Czech Republic'),(54,'de','Germany'),(55,'dj','Djibouti'),(56,'dk','Denmark'),(57,'dm','Dominica'),(58,'do','Dominican Republic'),(59,'dz','Algeria'),(60,'ec','Ecuador'),(61,'ee','Estonia'),(62,'eg','Egypt'),(63,'eh','Western Sahara'),(64,'er','Eritrea'),(65,'es','Spain'),(66,'et','Ethiopia'),(67,'fi','Finland'),(68,'fj','Fiji'),(69,'fk','Falkland Islands (Malvinas)'),(70,'fm','Micronesia'),(71,'fo','Faroe Islands'),(72,'fr','France'),(73,'fx','France, Metropolitan'),(74,'ga','Gabon'),(75,'gb','United Kingdom'),(76,'gd','Grenada'),(77,'ge','Georgia'),(78,'gf','French Guiana'),(79,'gh','Ghana'),(80,'gi','Gibraltar'),(81,'gl','Greenland'),(82,'gm','Gambia'),(83,'gn','Guinea'),(84,'gp','Guadeloupe'),(85,'gq','Equatorial Guinea'),(86,'gr','Greece'),(87,'gs','S. Georgia and S. Sandwich Isls.'),(88,'gt','Guatemala'),(89,'gu','Guam'),(90,'gw','Guinea-Bissau'),(91,'gy','Guyana'),(92,'hk','Hong Kong'),(93,'hm','Heard and McDonald Islands'),(94,'hn','Honduras'),(95,'hr','Croatia (Hrvatska)'),(96,'ht','Haiti'),(97,'hu','Hungary'),(98,'id','Indonesia'),(99,'ie','Ireland'),(100,'il','Israel'),(101,'in','India'),(102,'io','British Indian Ocean Territory'),(103,'iq','Iraq'),(104,'ir','Iran'),(105,'is','Iceland'),(106,'it','Italy'),(107,'jm','Jamaica'),(108,'jo','Jordan'),(109,'jp','Japan'),(110,'ke','Kenya'),(111,'kg','Kyrgyzstan'),(112,'kh','Cambodia'),(113,'ki','Kiribati'),(114,'km','Comoros'),(115,'kn','Saint Kitts and Nevis'),(116,'kp','Korea (North)'),(117,'kr','Korea (South)'),(118,'kw','Kuwait'),(119,'ky','Cayman Islands'),(120,'kz','Kazakhstan'),(121,'la','Laos'),(122,'lb','Lebanon'),(123,'lc','Saint Lucia'),(124,'li','Liechtenstein'),(125,'lk','Sri Lanka'),(126,'lr','Liberia'),(127,'ls','Lesotho'),(128,'lt','Lithuania'),(129,'lu','Luxembourg'),(130,'lv','Latvia'),(131,'ly','Libya'),(132,'ma','Morocco'),(133,'mc','Monaco'),(134,'md','Moldova'),(135,'mg','Madagascar'),(136,'mh','Marshall Islands'),(137,'mk','Macedonia'),(138,'ml','Mali'),(139,'mm','Myanmar'),(140,'mn','Mongolia'),(141,'mo','Macau'),(142,'mp','Northern Mariana Islands'),(143,'mq','Martinique'),(144,'mr','Mauritania'),(145,'ms','Montserrat'),(146,'mt','Malta'),(147,'mu','Mauritius'),(148,'mv','Maldives'),(149,'mw','Malawi'),(150,'mx','Mexico'),(151,'my','Malaysia'),(152,'mz','Mozambique'),(153,'na','Namibia'),(154,'nc','New Caledonia'),(155,'ne','Niger'),(156,'nf','Norfolk Island'),(157,'ng','Nigeria'),(158,'ni','Nicaragua'),(159,'nl','Netherlands'),(160,'no','Norway'),(161,'np','Nepal'),(162,'nr','Nauru'),(163,'nt','Neutral Zone'),(164,'nu','Niue'),(165,'nz','New Zealand (Aotearoa)'),(166,'om','Oman'),(167,'pa','Panama'),(168,'pe','Peru'),(169,'pf','French Polynesia'),(170,'pg','Papua New Guinea'),(171,'ph','Philippines'),(172,'pk','Pakistan'),(173,'pl','Poland'),(174,'pm','St. Pierre and Miquelon'),(175,'pn','Pitcairn'),(176,'pr','Puerto Rico'),(177,'pt','Portugal'),(178,'pw','Palau'),(179,'py','Paraguay'),(180,'qa','Qatar'),(181,'re','Reunion'),(182,'ro','Romania'),(183,'ru','Russian Federation'),(184,'rw','Rwanda'),(185,'sa','Saudi Arabia'),(186,'sb','Solomon Islands'),(187,'sc','Seychelles'),(188,'sd','Sudan'),(189,'se','Sweden'),(190,'sg','Singapore'),(191,'sh','St. Helena'),(192,'si','Slovenia'),(193,'sj','Svalbard and Jan Mayen Islands'),(194,'sk','Slovak Republic'),(195,'sl','Sierra Leone'),(196,'sm','San Marino'),(197,'sn','Senegal'),(198,'so','Somalia'),(199,'sr','Suriname'),(200,'st','Sao Tome and Principe'),(201,'suhh','USSR (former)'),(202,'sv','El Salvador'),(203,'sy','Syria'),(204,'sz','Swaziland'),(205,'tc','Turks and Caicos Islands'),(206,'td','Chad'),(207,'tf','French Southern Territories'),(208,'tg','Togo'),(209,'th','Thailand'),(210,'tj','Tajikistan'),(211,'tk','Tokelau'),(212,'tm','Turkmenistan'),(213,'tn','Tunisia'),(214,'to','Tonga'),(215,'tp','East Timor'),(216,'tr','Turkey'),(217,'tt','Trinidad and Tobago'),(218,'tv','Tuvalu'),(219,'tw','Taiwan'),(220,'tz','Tanzania'),(221,'ua','Ukraine'),(222,'ug','Uganda'),(224,'um','US Minor Outlying Islands'),(225,'us','United States'),(226,'uy','Uruguay'),(227,'uz','Uzbekistan'),(228,'va','Vatican City State (Holy See)'),(229,'vc','Saint Vincent and the Grenadines'),(230,'ve','Venezuela'),(231,'vg','Virgin Islands (British)'),(232,'vi','Virgin Islands (U.S.)'),(233,'vn','Viet Nam'),(234,'vu','Vanuatu'),(235,'wf','Wallis and Futuna Islands'),(236,'ws','Samoa'),(237,'ye','Yemen'),(238,'yt','Mayotte'),(239,'yu','Yugoslavia'),(240,'za','South Africa'),(241,'zm','Zambia'),(242,'zr','Zaire'),(243,'zw','Zimbabwe'),(247,'ddde','German Democratic Republic [former]'),(248,'xx','-- FIX ME --'),(249,'zz','(unknown)');
/*!40000 ALTER TABLE `stddata_country` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stddata_currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stddata_currency` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_decimal` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `stddata_currency_name_5e8afff0` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=175 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stddata_currency` WRITE;
/*!40000 ALTER TABLE `stddata_currency` DISABLE KEYS */;
INSERT INTO `stddata_currency` VALUES (1,'DZD','Algerian Dinar',1),(2,'NAD','Namibian Dollar',1),(3,'GHS','Ghana Cedi',1),(4,'EGP','Egyptian Pound',1),(5,'BGN','Bulgarian Lev',1),(6,'XBD','European Unit of Account 17(E.U.A.-17)',1),(7,'XAG','Silver',1),(8,'XBA','Bond Markets Units European Composite Unit (EURCO)',1),(9,'DKK','Danish Krone',1),(10,'XBC','European Unit of Account 9(E.U.A.-9)',1),(11,'XBB','European Monetary Unit (E.M.U.-6)',1),(12,'BWP','Pula',1),(13,'LBP','Lebanese Pound',1),(14,'TZS','Tanzanian Shilling',1),(15,'VND','Dong',1),(16,'AOA','Kwanza',1),(17,'KHR','Riel',1),(18,'MYR','Malaysian Ringgit',1),(19,'KYD','Cayman Islands Dollar',1),(20,'LYD','Libyan Dinar',1),(21,'UAH','Hryvnia',1),(22,'JOD','Jordanian Dinar',1),(23,'AWG','Aruban Guilder',1),(24,'SAR','Saudi Riyal',1),(25,'EUR','Euro',1),(26,'HKD','Hong Kong Dollar',1),(27,'CHF','Swiss Franc',1),(28,'GIP','Gibraltar Pound',1),(29,'BYR','Belarussian Ruble',1),(30,'ALL','Lek',1),(31,'XPD','Palladium',1),(32,'MRO','Ouguiya',1),(33,'HRK','Croatian Kuna',1),(34,'DJF','Djibouti Franc',1),(35,'SZL','Lilangeni',1),(36,'THB','Baht',1),(37,'XAF','CFA franc BEAC',1),(38,'BND','Brunei Dollar',1),(39,'ISK','Iceland Krona',1),(40,'UYU','Uruguayan peso',1),(41,'NIO','Cordoba Oro',1),(42,'LAK','Kip',1),(43,'XYZ','Default currency.',1),(44,'SYP','Syrian Pound',1),(45,'MAD','Moroccan Dirham',1),(46,'MZN','Metical',1),(47,'PHP','Philippine Peso',1),(48,'ZAR','Rand',1),(49,'NPR','Nepalese Rupee',1),(50,'ZWL','Zimbabwe dollar A/09',1),(51,'ZWN','Zimbabwe dollar A/08',1),(52,'NGN','Naira',1),(53,'ZWD','Zimbabwe Dollar A/06',1),(54,'CRC','Costa Rican Colon',1),(55,'AED','UAE Dirham',1),(56,'EEK','Kroon',1),(57,'MWK','Kwacha',1),(58,'LKR','Sri Lanka Rupee',1),(59,'SKK','Slovak Koruna',1),(60,'PKR','Pakistan Rupee',1),(61,'HUF','Forint',1),(62,'BMD','Bermudian Dollar (customarily known as Bermuda Dollar)',1),(63,'LSL','Lesotho loti',1),(64,'MNT','Tugrik',1),(65,'AMD','Armenian Dram',1),(66,'UGX','Uganda Shilling',1),(67,'QAR','Qatari Rial',1),(68,'XDR','SDR',1),(69,'JMD','Jamaican Dollar',1),(70,'GEL','Lari',1),(71,'SHP','Saint Helena Pound',1),(72,'AFN','Afghani',1),(73,'SBD','Solomon Islands Dollar',1),(74,'KPW','North Korean Won',1),(75,'TRY','Turkish Lira',1),(76,'BDT','Taka',1),(77,'YER','Yemeni Rial',1),(78,'HTG','Haitian gourde',1),(79,'XOF','CFA Franc BCEAO',1),(80,'MGA','Malagasy Ariary',1),(81,'ANG','Netherlands Antillian Guilder',1),(82,'LRD','Liberian Dollar',1),(83,'RWF','Rwanda Franc',1),(84,'NOK','Norwegian Krone',1),(85,'MOP','Pataca',1),(86,'INR','Indian Rupee',1),(87,'MXN','Mexixan peso',1),(88,'CZK','Czech Koruna',1),(89,'TJS','Somoni',1),(90,'BTN','Bhutanese ngultrum',1),(91,'COP','Colombian peso',1),(92,'MUR','Mauritius Rupee',1),(93,'IDR','Rupiah',1),(94,'HNL','Lempira',1),(95,'XPF','CFP Franc',1),(96,'FJD','Fiji Dollar',1),(97,'ETB','Ethiopian Birr',1),(98,'PEN','Nuevo Sol',1),(99,'BZD','Belize Dollar',1),(100,'ILS','New Israeli Sheqel',1),(101,'DOP','Dominican Peso',1),(102,'TMM','Manat',1),(103,'TWD','New Taiwan Dollar',1),(104,'MDL','Moldovan Leu',1),(105,'XPT','Platinum',1),(106,'BSD','Bahamian Dollar',1),(107,'TVD','Tuvalu dollar',1),(108,'SEK','Swedish Krona',1),(109,'ZMK','Kwacha',1),(110,'MVR','Rufiyaa',1),(111,'XTS','Codes specifically reserved for testing purposes',1),(112,'AUD','Australian Dollar',1),(113,'SRD','Surinam Dollar',1),(114,'CUP','Cuban Peso',1),(115,'BBD','Barbados Dollar',1),(116,'KMF','Comoro Franc',1),(117,'KRW','Won',1),(118,'GMD','Dalasi',1),(119,'VEF','Bolivar Fuerte',1),(120,'IMP','Isle of Man pount',1),(121,'CUC','Cuban convertible peso',1),(122,'CLP','Chilean peso',1),(123,'LTL','Lithuanian Litas',1),(124,'CDF','Congolese franc',1),(125,'XCD','East Caribbean Dollar',1),(126,'KZT','Tenge',1),(127,'RUB','Russian Ruble',1),(128,'XFU','UIC-Franc',1),(129,'TTD','Trinidad and Tobago Dollar',1),(130,'OMR','Rial Omani',1),(131,'BRL','Brazilian Real',1),(132,'MMK','Kyat',1),(133,'PLN','Zloty',1),(134,'PYG','Guarani',1),(135,'KES','Kenyan Shilling',1),(136,'MKD','Denar',1),(137,'GBP','Pound Sterling',1),(138,'AZN','Azerbaijanian Manat',1),(139,'TOP','Paanga',1),(140,'VUV','Vatu',1),(141,'GNF','Guinea Franc',1),(142,'WST','Tala',1),(143,'IQD','Iraqi Dinar',1),(144,'ERN','Nakfa',1),(145,'BAM','Convertible Marks',1),(146,'SCR','Seychelles Rupee',1),(147,'CAD','Canadian Dollar',1),(148,'CVE','Cape Verde Escudo',1),(149,'KWD','Kuwaiti Dinar',1),(150,'BIF','Burundi Franc',1),(151,'PGK','Kina',1),(152,'SOS','Somali Shilling',1),(153,'SGD','Singapore Dollar',1),(154,'UZS','Uzbekistan Sum',1),(155,'STD','Dobra',1),(156,'XFO','Gold-Franc',1),(157,'IRR','Iranian Rial',1),(158,'CNY','Yuan Renminbi',1),(159,'SLL','Leone',1),(160,'TND','Tunisian Dinar',1),(161,'GYD','Guyana Dollar',1),(162,'NZD','New Zealand Dollar',1),(163,'FKP','Falkland Islands Pound',1),(164,'LVL','Latvian Lats',1),(165,'USD','US Dollar',1),(166,'KGS','Som',1),(167,'ARS','Argentine Peso',1),(168,'RON','New Leu',1),(169,'GTQ','Quetzal',1),(170,'RSD','Serbian Dinar',1),(171,'BHD','Bahraini Dinar',1),(172,'JPY','Yen',1),(173,'SDG','Sudanese Pound',1),(174,'XAU','Gold',1);
/*!40000 ALTER TABLE `stddata_currency` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stddata_date`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stddata_date` (
  `id` int NOT NULL AUTO_INCREMENT,
  `year` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `month` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `day` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `year_uncertain` tinyint(1) NOT NULL,
  `month_uncertain` tinyint(1) NOT NULL,
  `day_uncertain` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `stddata_date_year_16787e34` (`year`),
  KEY `stddata_date_month_e7a8981a` (`month`),
  KEY `stddata_date_day_e19658a4` (`day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stddata_date` WRITE;
/*!40000 ALTER TABLE `stddata_date` DISABLE KEYS */;
/*!40000 ALTER TABLE `stddata_date` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stddata_language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stddata_language` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `native_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `stddata_language_name_1d33e8a6` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=147 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stddata_language` WRITE;
/*!40000 ALTER TABLE `stddata_language` DISABLE KEYS */;
INSERT INTO `stddata_language` VALUES (1,'aa','Afar',''),(2,'ab','Abkhazian',''),(3,'af','Afrikaans',''),(4,'am','Amharic',''),(5,'ar','Arabic',''),(6,'as','Assamese',''),(7,'ay','Aymara',''),(8,'az','Azerbaijani',''),(9,'ba','Bashkir',''),(10,'be','Byelorussian',''),(11,'bg','Bulgarian',''),(12,'bh','Bihari',''),(13,'bi','Bislama',''),(14,'bn','Bengali; Bangla',''),(15,'bo','Tibetan',''),(16,'br','Breton',''),(17,'ca','Catalan',''),(18,'co','Corsican',''),(19,'cs','Czech',''),(20,'cy','Welsh',''),(21,'da','Danish',''),(22,'de','German',''),(23,'dz','Bhutani',''),(24,'el','Greek',''),(25,'en','English',''),(26,'eo','Esperanto',''),(27,'es','Spanish',''),(28,'et','Estonian',''),(29,'eu','Basque',''),(30,'fa','Persian',''),(31,'fi','Finnish',''),(32,'fj','Fiji',''),(33,'fo','Faeroese',''),(34,'fr','French',''),(35,'fy','Frisian',''),(36,'ga','Irish',''),(37,'gd','Scots Gaelic',''),(38,'gl','Galician',''),(39,'gn','Guarani',''),(40,'gu','Gujarati',''),(41,'ha','Hausa',''),(42,'hi','Hindi',''),(43,'hr','Croatian',''),(44,'hu','Hungarian',''),(45,'hy','Armenian',''),(46,'ia','Interlingua',''),(47,'ie','Interlingue',''),(48,'ik','Inupiak',''),(49,'in','Indonesian',''),(50,'is','Icelandic',''),(51,'it','Italian',''),(52,'iw','Hebrew',''),(53,'ja','Japanese',''),(54,'ji','Yiddish',''),(55,'jw','Javanese',''),(56,'ka','Georgian',''),(57,'kk','Kazakh',''),(58,'kl','Greenlandic',''),(59,'km','Cambodian',''),(60,'kn','Kannada',''),(61,'ko','Korean',''),(62,'ks','Kashmiri',''),(63,'ku','Kurdish',''),(64,'ky','Kirghiz',''),(65,'la','Latin',''),(66,'ln','Lingala',''),(67,'lo','Laothian',''),(68,'lt','Lithuanian',''),(69,'lv','Latvian, Lettish',''),(70,'mg','Malagasy',''),(71,'mi','Maori',''),(72,'mk','Macedonian',''),(73,'ml','Malayalam',''),(74,'mn','Mongolian',''),(75,'mo','Moldavian',''),(76,'mr','Marathi',''),(77,'ms','Malay',''),(78,'mt','Maltese',''),(79,'my','Burmese',''),(80,'na','Nauru',''),(81,'ne','Nepali',''),(82,'nl','Dutch',''),(83,'no','Norwegian',''),(84,'oc','Occitan',''),(85,'om','Oromo (Afan)',''),(86,'or','Oriya',''),(87,'pa','Punjabi',''),(88,'pl','Polish',''),(89,'ps','Pashto, Pushto',''),(90,'pt','Portuguese',''),(91,'qu','Quechua',''),(92,'rm','Rhaeto-Romance',''),(93,'rn','Kirundi',''),(94,'ro','Romanian',''),(95,'ru','Russian',''),(96,'rw','Kinyarwanda',''),(97,'sa','Sanskrit',''),(98,'sd','Sindhi',''),(99,'sg','Sangro',''),(100,'sh','Serbo-Croatian',''),(101,'si','Singhalese',''),(102,'sk','Slovak',''),(103,'sl','Slovenian',''),(104,'sm','Samoan',''),(105,'sn','Shona',''),(106,'so','Somali',''),(107,'sq','Albanian',''),(108,'sr','Serbian',''),(109,'ss','Siswati',''),(110,'st','Sesotho',''),(111,'su','Sundanese',''),(112,'sv','Swedish',''),(113,'sw','Swahili',''),(114,'ta','Tamil',''),(115,'te','Telugu',''),(116,'tg','Tajik',''),(117,'th','Thai',''),(118,'ti','Tigrinya',''),(119,'tk','Turkmen',''),(120,'tl','Tagalog',''),(121,'tn','Setswana',''),(122,'to','Tonga',''),(123,'tr','Turkish',''),(124,'ts','Tsonga',''),(125,'tt','Tatar',''),(126,'tw','Twi',''),(127,'uk','Ukrainian',''),(128,'ur','Urdu',''),(129,'uz','Uzbek',''),(130,'vi','Vietnamese',''),(131,'vo','Volapuk',''),(132,'wo','Wolof',''),(133,'xh','Xhosa',''),(134,'yo','Yoruba',''),(135,'zh','Chinese',''),(136,'zu','Zulu',''),(137,'bs','Bosnian',''),(138,'se','Sami (Northern)',''),(139,'sma','Sami (Southern)',''),(140,'smj','Sami (Lule)',''),(141,'smn','Sami (Inari)',''),(142,'sms','Sami (Skolt)',''),(143,'smi','Sami languages',''),(144,'zxx','(no linguistic content)',''),(145,'fil','Filipino; Pilipino',''),(146,'und','(undetermined)','');
/*!40000 ALTER TABLE `stddata_language` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `stddata_script`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stddata_script` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `number` smallint unsigned NOT NULL,
  `name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `number` (`number`),
  CONSTRAINT `stddata_script_chk_1` CHECK ((`number` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `stddata_script` WRITE;
/*!40000 ALTER TABLE `stddata_script` DISABLE KEYS */;
/*!40000 ALTER TABLE `stddata_script` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `taggit_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `taggit_tag` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `taggit_tag` WRITE;
/*!40000 ALTER TABLE `taggit_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `taggit_tag` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `taggit_taggeditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `taggit_taggeditem` (
  `id` int NOT NULL AUTO_INCREMENT,
  `object_id` int NOT NULL,
  `content_type_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taggit_taggeditem_content_type_id_object_id_tag_id_4bb97a8e_uniq` (`content_type_id`,`object_id`,`tag_id`),
  KEY `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` (`tag_id`),
  KEY `taggit_taggeditem_object_id_e2d7d1df` (`object_id`),
  KEY `taggit_tagg_content_8fc721_idx` (`content_type_id`,`object_id`),
  CONSTRAINT `taggit_taggeditem_content_type_id_9957a03c_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `taggit_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `taggit_taggeditem` WRITE;
/*!40000 ALTER TABLE `taggit_taggeditem` DISABLE KEYS */;
/*!40000 ALTER TABLE `taggit_taggeditem` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_agenda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_agenda` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uses_tokens` tinyint(1) NOT NULL,
  `allows_abstentions` tinyint(1) NOT NULL,
  `quorum` int NOT NULL,
  `secret_ballot` tinyint(1) NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_agenda_permission_id_fbf53eaf_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `voting_agenda_permission_id_fbf53eaf_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_agenda` WRITE;
/*!40000 ALTER TABLE `voting_agenda` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_agenda` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_agenda_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_agenda_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci,
  `state` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `agenda_id` int NOT NULL,
  `owner_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_agenda_item_agenda_id_b343816f_fk_voting_agenda_id` (`agenda_id`),
  KEY `voting_agenda_item_owner_id_0bde06a6_fk_auth_user_id` (`owner_id`),
  KEY `voting_agenda_item_created_cb9a41e8` (`created`),
  CONSTRAINT `voting_agenda_item_agenda_id_b343816f_fk_voting_agenda_id` FOREIGN KEY (`agenda_id`) REFERENCES `voting_agenda` (`id`),
  CONSTRAINT `voting_agenda_item_owner_id_0bde06a6_fk_auth_user_id` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_agenda_item` WRITE;
/*!40000 ALTER TABLE `voting_agenda_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_agenda_item` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_agenda_item_subscribers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_agenda_item_subscribers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `agendaitem_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `voting_agenda_item_subsc_agendaitem_id_user_id_15c35195_uniq` (`agendaitem_id`,`user_id`),
  KEY `voting_agenda_item_subscribers_user_id_a572b45e_fk_auth_user_id` (`user_id`),
  CONSTRAINT `voting_agenda_item_s_agendaitem_id_d7baf7de_fk_voting_ag` FOREIGN KEY (`agendaitem_id`) REFERENCES `voting_agenda_item` (`id`),
  CONSTRAINT `voting_agenda_item_subscribers_user_id_a572b45e_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_agenda_item_subscribers` WRITE;
/*!40000 ALTER TABLE `voting_agenda_item_subscribers` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_agenda_item_subscribers` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_agenda_mailing_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_agenda_mailing_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `on_agenda_item_add` tinyint(1) NOT NULL,
  `on_agenda_item_open` tinyint(1) NOT NULL,
  `on_vote_open` tinyint(1) NOT NULL,
  `on_vote_close` tinyint(1) NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `reminder` tinyint(1) NOT NULL,
  `display_token` tinyint(1) NOT NULL,
  `agenda_id` int NOT NULL,
  `group_id` int DEFAULT NULL,
  `mailing_list_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_agenda_mailin_mailing_list_id_078a4e09_fk_voting_ma` (`mailing_list_id`),
  KEY `voting_agenda_mailin_agenda_id_cfc47a1e_fk_voting_ag` (`agenda_id`),
  KEY `voting_agenda_mailing_list_group_id_a0644fd9_fk_auth_group_id` (`group_id`),
  CONSTRAINT `voting_agenda_mailin_agenda_id_cfc47a1e_fk_voting_ag` FOREIGN KEY (`agenda_id`) REFERENCES `voting_agenda` (`id`),
  CONSTRAINT `voting_agenda_mailin_mailing_list_id_078a4e09_fk_voting_ma` FOREIGN KEY (`mailing_list_id`) REFERENCES `voting_mailing_list` (`id`),
  CONSTRAINT `voting_agenda_mailing_list_group_id_a0644fd9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_agenda_mailing_list` WRITE;
/*!40000 ALTER TABLE `voting_agenda_mailing_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_agenda_mailing_list` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_agenda_subscribers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_agenda_subscribers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `agenda_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `voting_agenda_subscribers_agenda_id_user_id_ad924c8c_uniq` (`agenda_id`,`user_id`),
  KEY `voting_agenda_subscribers_user_id_fc6ab270_fk_auth_user_id` (`user_id`),
  CONSTRAINT `voting_agenda_subscribers_agenda_id_a2c9ece8_fk_voting_agenda_id` FOREIGN KEY (`agenda_id`) REFERENCES `voting_agenda` (`id`),
  CONSTRAINT `voting_agenda_subscribers_user_id_fc6ab270_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_agenda_subscribers` WRITE;
/*!40000 ALTER TABLE `voting_agenda_subscribers` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_agenda_subscribers` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_expected_voter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_expected_voter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tenure_began` datetime(6) NOT NULL,
  `tenure_ended` datetime(6) DEFAULT NULL,
  `agenda_id` int NOT NULL,
  `voter_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_expected_voter_agenda_id_f25ffd96_fk_voting_agenda_id` (`agenda_id`),
  KEY `voting_expected_voter_voter_id_06da2dde_fk_auth_user_id` (`voter_id`),
  CONSTRAINT `voting_expected_voter_agenda_id_f25ffd96_fk_voting_agenda_id` FOREIGN KEY (`agenda_id`) REFERENCES `voting_agenda` (`id`),
  CONSTRAINT `voting_expected_voter_voter_id_06da2dde_fk_auth_user_id` FOREIGN KEY (`voter_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_expected_voter` WRITE;
/*!40000 ALTER TABLE `voting_expected_voter` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_expected_voter` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_mailing_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_mailing_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `address` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_mailing_list` WRITE;
/*!40000 ALTER TABLE `voting_mailing_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_mailing_list` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_option`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_option` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `text` longtext COLLATE utf8mb4_unicode_ci,
  `ballot_position` int DEFAULT NULL,
  `result` tinyint(1) DEFAULT NULL,
  `topic_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_option_topic_id_1b40fd69_fk_voting_topic_id` (`topic_id`),
  CONSTRAINT `voting_option_topic_id_1b40fd69_fk_voting_topic_id` FOREIGN KEY (`topic_id`) REFERENCES `voting_topic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_option` WRITE;
/*!40000 ALTER TABLE `voting_option` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_option` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_receipt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_receipt` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vote_key` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `topic_id` int NOT NULL,
  `voter_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_receipt_topic_id_133815b0_fk_voting_topic_id` (`topic_id`),
  KEY `voting_receipt_voter_id_51ccdc4e_fk_auth_user_id` (`voter_id`),
  CONSTRAINT `voting_receipt_topic_id_133815b0_fk_voting_topic_id` FOREIGN KEY (`topic_id`) REFERENCES `voting_topic` (`id`),
  CONSTRAINT `voting_receipt_voter_id_51ccdc4e_fk_auth_user_id` FOREIGN KEY (`voter_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_receipt` WRITE;
/*!40000 ALTER TABLE `voting_receipt` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_receipt` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_topic` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `text` longtext COLLATE utf8mb4_unicode_ci,
  `open` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `deadline` datetime(6) NOT NULL,
  `token` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `result_calculated` tinyint(1) NOT NULL,
  `invalid` tinyint(1) NOT NULL,
  `agenda_id` int NOT NULL,
  `author_id` int NOT NULL,
  `second_id` int DEFAULT NULL,
  `vote_type_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_topic_vote_type_id_84f2e99c_fk_voting_vote_type_id` (`vote_type_id`),
  KEY `voting_topic_agenda_id_9229ae91_fk_voting_agenda_id` (`agenda_id`),
  KEY `voting_topic_author_id_60e067f6_fk_auth_user_id` (`author_id`),
  KEY `voting_topic_second_id_9012e993_fk_auth_user_id` (`second_id`),
  KEY `voting_topic_created_5a7a676f` (`created`),
  KEY `voting_topic_deadline_5221c020` (`deadline`),
  KEY `voting_topic_result_calculated_312013df` (`result_calculated`),
  CONSTRAINT `voting_topic_agenda_id_9229ae91_fk_voting_agenda_id` FOREIGN KEY (`agenda_id`) REFERENCES `voting_agenda` (`id`),
  CONSTRAINT `voting_topic_author_id_60e067f6_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `voting_topic_second_id_9012e993_fk_auth_user_id` FOREIGN KEY (`second_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `voting_topic_vote_type_id_84f2e99c_fk_voting_vote_type_id` FOREIGN KEY (`vote_type_id`) REFERENCES `voting_vote_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_topic` WRITE;
/*!40000 ALTER TABLE `voting_topic` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_topic` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_topic_agenda_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_topic_agenda_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic_id` int NOT NULL,
  `agendaitem_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `voting_topic_agenda_items_topic_id_agendaitem_id_87f25526_uniq` (`topic_id`,`agendaitem_id`),
  KEY `voting_topic_agenda__agendaitem_id_482327f9_fk_voting_ag` (`agendaitem_id`),
  CONSTRAINT `voting_topic_agenda__agendaitem_id_482327f9_fk_voting_ag` FOREIGN KEY (`agendaitem_id`) REFERENCES `voting_agenda_item` (`id`),
  CONSTRAINT `voting_topic_agenda_items_topic_id_c8b0ad0e_fk_voting_topic_id` FOREIGN KEY (`topic_id`) REFERENCES `voting_topic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_topic_agenda_items` WRITE;
/*!40000 ALTER TABLE `voting_topic_agenda_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_topic_agenda_items` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_topic_subscribers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_topic_subscribers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `voting_topic_subscribers_topic_id_user_id_8b858b58_uniq` (`topic_id`,`user_id`),
  KEY `voting_topic_subscribers_user_id_8d1d406c_fk_auth_user_id` (`user_id`),
  CONSTRAINT `voting_topic_subscribers_topic_id_5ed93eaf_fk_voting_topic_id` FOREIGN KEY (`topic_id`) REFERENCES `voting_topic` (`id`),
  CONSTRAINT `voting_topic_subscribers_user_id_8d1d406c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_topic_subscribers` WRITE;
/*!40000 ALTER TABLE `voting_topic_subscribers` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_topic_subscribers` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_vote`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_vote` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rank` int DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `option_id` int NOT NULL,
  `voter_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `voting_vote_option_id_eabbceff_fk_voting_option_id` (`option_id`),
  KEY `voting_vote_voter_id_599434c4_fk_auth_user_id` (`voter_id`),
  CONSTRAINT `voting_vote_option_id_eabbceff_fk_voting_option_id` FOREIGN KEY (`option_id`) REFERENCES `voting_option` (`id`),
  CONSTRAINT `voting_vote_voter_id_599434c4_fk_auth_user_id` FOREIGN KEY (`voter_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_vote` WRITE;
/*!40000 ALTER TABLE `voting_vote` DISABLE KEYS */;
/*!40000 ALTER TABLE `voting_vote` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `voting_vote_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voting_vote_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `max_votes` int DEFAULT NULL,
  `max_winners` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `voting_vote_type` WRITE;
/*!40000 ALTER TABLE `voting_vote_type` DISABLE KEYS */;
INSERT INTO `voting_vote_type` VALUES (1,'Pass / Fail',1,1),(2,'Choose One',1,1),(3,'Ranked Choice',NULL,1),(4,'Board Election: Choose Four',4,4),(5,'Board Election: Choose Five',5,5);
/*!40000 ALTER TABLE `voting_vote_type` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

