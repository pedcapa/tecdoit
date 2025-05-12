-- MySQL dump 10.13  Distrib 9.2.0, for macos15.2 (arm64)
--
-- Host: localhost    Database: juego_matematicas
-- ------------------------------------------------------
-- Server version	9.2.0

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

USE juego_matematicas;

--
-- Table structure for table `Categoria`
--

DROP TABLE IF EXISTS `Categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Categoria` (
  `idCategoria` int NOT NULL AUTO_INCREMENT,
  `nombreCategoria` varchar(100) NOT NULL,
  PRIMARY KEY (`idCategoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Categoria`
--

LOCK TABLES `Categoria` WRITE;
/*!40000 ALTER TABLE `Categoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `Categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Estadistica`
--

DROP TABLE IF EXISTS `Estadistica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Estadistica` (
  `idEstadistica` int NOT NULL AUTO_INCREMENT,
  `reportePadre` int DEFAULT NULL,
  `nombreEstadistica` varchar(255) DEFAULT NULL,
  `valorEstadistica` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idEstadistica`),
  KEY `reportePadre` (`reportePadre`),
  CONSTRAINT `estadistica_ibfk_1` FOREIGN KEY (`reportePadre`) REFERENCES `Reporte` (`idReporte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Dumping data for table `Estadistica`
--

LOCK TABLES `Estadistica` WRITE;
/*!40000 ALTER TABLE `Estadistica` DISABLE KEYS */;
/*!40000 ALTER TABLE `Estadistica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Evaluacion`
--

DROP TABLE IF EXISTS `Evaluacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Evaluacion` (
  `idEvaluacion` int NOT NULL AUTO_INCREMENT,
  `usuario` int DEFAULT NULL,
  `fecha` datetime DEFAULT NULL,
  `puntuacion` int DEFAULT NULL,
  PRIMARY KEY (`idEvaluacion`),
  KEY `usuario` (`usuario`),
  CONSTRAINT `evaluacion_ibfk_1` FOREIGN KEY (`usuario`) REFERENCES `Usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Evaluacion`
--

LOCK TABLES `Evaluacion` WRITE;
/*!40000 ALTER TABLE `Evaluacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `Evaluacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EvaluacionPregunta`
--

DROP TABLE IF EXISTS `EvaluacionPregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EvaluacionPregunta` (
  `idEvaluacion` int NOT NULL,
  `idPregunta` int NOT NULL,
  PRIMARY KEY (`idEvaluacion`,`idPregunta`),
  KEY `idPregunta` (`idPregunta`),
  CONSTRAINT `evaluacionpregunta_ibfk_1` FOREIGN KEY (`idEvaluacion`) REFERENCES `Evaluacion` (`idEvaluacion`),
  CONSTRAINT `evaluacionpregunta_ibfk_2` FOREIGN KEY (`idPregunta`) REFERENCES `Pregunta` (`idPregunta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EvaluacionPregunta`
--

LOCK TABLES `EvaluacionPregunta` WRITE;
/*!40000 ALTER TABLE `EvaluacionPregunta` DISABLE KEYS */;
/*!40000 ALTER TABLE `EvaluacionPregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LogCambios`
--

DROP TABLE IF EXISTS `LogCambios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LogCambios` (
  `idLogCambio` int NOT NULL AUTO_INCREMENT,
  `usuarioCambio` int DEFAULT NULL,
  `preguntaCambiada` int DEFAULT NULL,
  `fechaCambio` datetime DEFAULT NULL,
  `cambio` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idLogCambio`),
  KEY `usuarioCambio` (`usuarioCambio`),
  KEY `preguntaCambiada` (`preguntaCambiada`),
  CONSTRAINT `logcambios_ibfk_1` FOREIGN KEY (`usuarioCambio`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `logcambios_ibfk_2` FOREIGN KEY (`preguntaCambiada`) REFERENCES `Pregunta` (`idPregunta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LogCambios`
--

LOCK TABLES `LogCambios` WRITE;
/*!40000 ALTER TABLE `LogCambios` DISABLE KEYS */;
/*!40000 ALTER TABLE `LogCambios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Opcion`
--

DROP TABLE IF EXISTS `Opcion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Opcion` (
  `idOpcion` int NOT NULL AUTO_INCREMENT,
  `textoOpcion` varchar(255) NOT NULL,
  `esCorrecta` tinyint(1) NOT NULL,
  `pregunta` int DEFAULT NULL,
  PRIMARY KEY (`idOpcion`),
  KEY `pregunta` (`pregunta`),
  CONSTRAINT `opcion_ibfk_1` FOREIGN KEY (`pregunta`) REFERENCES `Pregunta` (`idPregunta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Opcion`
--

LOCK TABLES `Opcion` WRITE;
/*!40000 ALTER TABLE `Opcion` DISABLE KEYS */;
/*!40000 ALTER TABLE `Opcion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Permisos`
--

DROP TABLE IF EXISTS `Permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Permisos` (
  `idPermiso` int NOT NULL AUTO_INCREMENT,
  `usuarioPermitido` int DEFAULT NULL,
  `permiso` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idPermiso`),
  KEY `usuarioPermitido` (`usuarioPermitido`),
  CONSTRAINT `permisos_ibfk_1` FOREIGN KEY (`usuarioPermitido`) REFERENCES `Usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Permisos`
--

LOCK TABLES `Permisos` WRITE;
/*!40000 ALTER TABLE `Permisos` DISABLE KEYS */;
/*!40000 ALTER TABLE `Permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Pregunta`
--

DROP TABLE IF EXISTS `Pregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Pregunta` (
  `idPregunta` int NOT NULL AUTO_INCREMENT,
  `textoPregunta` text NOT NULL,
  `nivelDificultad` varchar(50) NOT NULL,
  `tema` varchar(100) DEFAULT NULL,
  `creador` int DEFAULT NULL,
  `categoria` int DEFAULT NULL,
  `isla` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`idPregunta`),
  KEY `creador` (`creador`),
  KEY `categoria` (`categoria`),
  CONSTRAINT `pregunta_ibfk_1` FOREIGN KEY (`creador`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `pregunta_ibfk_2` FOREIGN KEY (`categoria`) REFERENCES `Categoria` (`idCategoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Pregunta`
--

LOCK TABLES `Pregunta` WRITE;
/*!40000 ALTER TABLE `Pregunta` DISABLE KEYS */;
/*!40000 ALTER TABLE `Pregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Reporte`
--

DROP TABLE IF EXISTS `Reporte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Reporte` (
  `idReporte` int NOT NULL AUTO_INCREMENT,
  `fechaCreacion` datetime DEFAULT NULL,
  `usuarioCreador` int DEFAULT NULL,
  PRIMARY KEY (`idReporte`),
  KEY `usuarioCreador` (`usuarioCreador`),
  CONSTRAINT `reporte_ibfk_1` FOREIGN KEY (`usuarioCreador`) REFERENCES `Usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Reporte`
--

LOCK TABLES `Reporte` WRITE;
/*!40000 ALTER TABLE `Reporte` DISABLE KEYS */;
/*!40000 ALTER TABLE `Reporte` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Usuario`
--

DROP TABLE IF EXISTS `Usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Usuario` (
  `idUsuario` int NOT NULL AUTO_INCREMENT,
  `nombreUsuario` varchar(255) NOT NULL,
  `correoElectronico` varchar(255) NOT NULL,
  `contraseña` varchar(255) NOT NULL,
  `rol` varchar(50) NOT NULL,
  `nivelEducativo` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  UNIQUE KEY `correoElectronico` (`correoElectronico`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Usuario`
--

LOCK TABLES `Usuario` WRITE;
/*!40000 ALTER TABLE `Usuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `Usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-24 16:35:03
