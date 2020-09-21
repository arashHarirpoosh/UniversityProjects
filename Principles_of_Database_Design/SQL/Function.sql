DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `getNC`(IDP Int) RETURNS varchar(20) CHARSET utf8
BEGIN
RETURN (select NCCreator from PaymentOrder where IDP = IDPO);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `NUMOFPAYMENTACCESS`(AN Int) RETURNS int(11)
BEGIN

RETURN (select count(*) from accountowners where PaymentAccess = true and accountnumber = AN);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `NUMOFREQUIERDSIGNS`(AN varchar(20)) RETURNS int(11)
BEGIN
RETURN (select NumberOfRequiredSignatures from `account` where AccountNumber = AN);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `NUMOFSIGNERACCESS`(AN Int) RETURNS int(11)
BEGIN

RETURN (select count(*) from accountowners where AccountNumber = AN  and SignatureAccess = 1);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `numOfSigns`(IDP Int) RETURNS int(11)
BEGIN
declare num int;
select count(*) into num  from signers where  signers.IDPO = IDP;
RETURN num;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `PaymentOrderIsPayed`(NIDP Int) RETURNS tinyint(1)
BEGIN

RETURN (select IDPaymentVerifier  from paymentorder where NIDP = IDP ) is not null;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `DecryptPassword`(Pass blob, Salt varchar(20)) RETURNS char(200) CHARSET utf8
BEGIN
RETURN (select replace(cast(Aes_decrypt(cast(Pass as char(200)),'Encryptmypassijfsffbchiedxa') as char(200)),Salt,''));
END$$
DELIMITER ;
