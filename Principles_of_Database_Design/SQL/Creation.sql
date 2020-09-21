CREATE TABLE `account` (
  `AccountNumber` int(11) NOT NULL,
  `Balance` int(11) NOT NULL DEFAULT '0',
  `NumberOfRequiredSignatures` int(11) NOT NULL DEFAULT '1',
  `KindOfAccount` varchar(45) NOT NULL,
  PRIMARY KEY (`AccountNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.account_BEFORE_INSERT$$
USE `electronicbankingsoftware`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`account_BEFORE_INSERT` BEFORE INSERT ON `account` FOR EACH ROW
BEGIN
if new.KindOfAccount not in('Loan','Savings','Current') then
SIGNAL sqlstate '45001'set message_text = "Invalid Kind Of Account !";
else 
INSERT INTO `electronicbankingsoftware`.`accountlog`
(
`AccountNumber`,
`Operation`,
`IDP`,
`Date`)
VALUES
(
new.AccountNumber,
'Account Created',
null,
now());

end if;
END$$
DELIMITER ;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.account_BEFORE_DELETE$$
USE `electronicbankingsoftware`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`account_BEFORE_DELETE` BEFORE DELETE ON `account` FOR EACH ROW
BEGIN
if not exists(select * from TheDeletedAccount where AccountNumber = old.accountnumber) then
INSERT INTO `electronicbankingsoftware`.`TheDeletedAccount`
(`AccountNumber`,
`Balance`,
`NumberOfRequiredSignatures`,
`KindOfAccount`)
select * from `account` where Accountnumber = old.accountnumber;
end if;
INSERT INTO `electronicbankingsoftware`.`accountlog`
(
`AccountNumber`,
`Operation`)
select AccountNumber,'Account Removed' from `account` where Accountnumber = old.accountnumber;

END$$
DELIMITER ;

CREATE TABLE `accountlog` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `AccountNumber` int(11) NOT NULL,
  `IDC` varchar(45) DEFAULT NULL,
  `Operation` varchar(45) DEFAULT NULL,
  `IDP` int(11) DEFAULT NULL,
  `Date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `accountowners` (
  `AccountNumber` int(11) NOT NULL,
  `IDAO` int(11) NOT NULL,
  `ViewAccess` tinyint(1) DEFAULT '0',
  `SignatureAccess` tinyint(1) DEFAULT '0',
  `PaymentAccess` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`AccountNumber`,`IDAO`),
  KEY `IDAO_idx` (`IDAO`),
  CONSTRAINT `AN` FOREIGN KEY (`AccountNumber`) REFERENCES `account` (`AccountNumber`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `IDAO` FOREIGN KEY (`IDAO`) REFERENCES `customer` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.accountowners_BEFORE_INSERT$$
USE `electronicbankingsoftware`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`accountowners_BEFORE_INSERT` BEFORE INSERT ON `accountowners` FOR EACH ROW
BEGIN
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(new.IDAO,new.accountnumber,'Insert ViewAccess',new.ViewAccess,now());
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(new.IDAO,new.accountnumber,'Insert SignatureAccess',new.SignatureAccess,now());
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(new.IDAO,new.accountnumber,'Insert PaymentAccess',new.PaymentAccess,now());
END$$
DELIMITER ; 

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.accountowners_BEFORE_UPDATE$$
USE `electronicbankingsoftware`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`accountowners_BEFORE_UPDATE` BEFORE UPDATE ON `accountowners` FOR EACH ROW
BEGIN
if old.ViewAccess<> new.ViewAccess then
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(new.IDAO,new.accountnumber,'Update ViewAccess',new.ViewAccess,now());
end if;
if old.SignatureAccess<> new.SignatureAccess then
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(new.IDAO,new.accountnumber,'Update SignatureAccess',new.SignatureAccess,now());
end if;
if old.PaymentAccess<> new.PaymentAccess then
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(new.IDAO,new.accountnumber,'Update PaymentAccess',new.PaymentAccess,now());
end if;
END $$
DELIMITER ; 

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.accountowners_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`accountowners_BEFORE_DELETE` BEFORE DELETE ON `accountowners` FOR EACH ROW
BEGIN
if not exists (select * from thedeletedaccountowners where AccountNumber = old.Accountnumber and IDAO = old.IDAO) then
INSERT INTO `electronicbankingsoftware`.`thedeletedaccountowners`
(`AccountNumber`,
`IDAO`,
`ViewAccess`,
`SignatureAccess`,
`PaymentAccess`)
select * from accountowners where IDAO = old.IDAO and AccountNumber = old.AccountNumber;
end if;

INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(old.IDAO,old.accountnumber,'Delete ViewAccess',null,now());
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(old.IDAO,old.accountnumber,'Delete SignatureAccess',null,now());
INSERT INTO `electronicbankingsoftware`.`customoraccesslog`
(`IDAO`,
 `AccountNumber`,
`Operation`,
`NewValue`,
`Date`) VALUES
(old.IDAO,old.accountnumber,'Delete PaymentAccess',null,now());
END $$
DELIMITER ;

CREATE TABLE `bill` (
  `AccountNumber` int(11) NOT NULL,
  `IDP` int(11) NOT NULL,
  `Amount` int(11) DEFAULT '0',
  `Notes` varchar(45) DEFAULT NULL,
  `KindOfBill` varchar(45) DEFAULT NULL,
  `Date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`AccountNumber`,`IDP`),
  KEY `IDPP_idx` (`IDP`),
  CONSTRAINT `ANB` FOREIGN KEY (`AccountNumber`) REFERENCES `account` (`AccountNumber`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `IDPP` FOREIGN KEY (`IDP`) REFERENCES `paymentorder` (`IDP`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.bill_BEFORE_INSERT$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`bill_BEFORE_INSERT` BEFORE INSERT ON `bill` FOR EACH ROW
BEGIN
if new.kindOfBill = 'Withdraw' then
update `account` set Balance = Balance - new.Amount where `account`.AccountNumber = new.AccountNumber;

elseif new.kindOfBill = 'Deposit' then
update `account` set Balance = Balance + new.Amount where `account`.AccountNumber = new.AccountNumber;

else
SIGNAL sqlstate '45001' set message_text = "Invalid Kind Of Bill !";

end if;

END $$
DELIMITER ;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.bill_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`bill_BEFORE_DELETE` BEFORE DELETE ON `bill` FOR EACH ROW
BEGIN
if not exists(select * from thedeletedbill where AccountNumber = old.AccountNumber and IDP = old.IDP) then
INSERT INTO `electronicbankingsoftware`.`thedeletedbill`
(`AccountNumber`,
`IDP`,
`Amount`,
`Notes`,
`KindOfBill`,
`Date`)
VALUES
(old.AccountNumber,
old.IDP,
old.Amount,
old.Notes,
old.KindOfBill,
old.`Date`);
end if;
END $$
DELIMITER ;

CREATE TABLE `customer` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NationalCode` varchar(20) CHARACTER SET utf8 NOT NULL,
  `FirstName` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `LastName` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `Password` blob NOT NULL,
  `Salt` varchar(20) CHARACTER SET latin1 DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `NationalCode_UNIQUE` (`NationalCode`),
  UNIQUE KEY `Salt_UNIQUE` (`Salt`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_general_mysql500_ci;
DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.customer_BEFORE_INSERT$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`customer_BEFORE_INSERT` BEFORE INSERT ON `customer` FOR EACH ROW
BEGIN
set new.Salt = conv(floor(rand() * 99999999999999), 20, 36) ;
set new.`Password` = cast(aes_encrypt(concat(`Password`,Salt),'Encryptmypassijfsffbchiedxa') as char(200));
END$$
DELIMITER ;

DELIMITER $$

CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`customer_BEFORE_UPDATE` BEFORE UPDATE ON `customer` FOR EACH ROW
BEGIN
set new.Salt = conv(floor(rand() * 99999999999999), 20, 36) ;
set new.`Password` = cast(aes_encrypt(concat(new.`Password`,new.Salt),'Encryptmypassijfsffbchiedxa') as char(200));

END$$
DELIMITER ;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.customer_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`customer_BEFORE_DELETE` BEFORE DELETE ON `customer` FOR EACH ROW
BEGIN
if not exists (select * from thedeletedcustomer where ID = old.ID) then
INSERT INTO `electronicbankingsoftware`.`thedeletedcustomer`
(`ID`,
`NationalCode`,
`FirstName`,
`LastName`,
`Password`)
VALUES
(old.ID,
old.NationalCode,
old.FirstName,
old.LastName,
old.Password);
end if;
END $$
DELIMITER ;

CREATE TABLE `customeraccount` (
  `ID` int(11) NOT NULL,
  `AccountNumber` int(11) NOT NULL,
  `AccountName` varchar(45) DEFAULT NULL,
  `AccountColor` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`,`AccountNumber`),
  KEY `ACN_idx` (`AccountNumber`),
  CONSTRAINT `ACN` FOREIGN KEY (`AccountNumber`) REFERENCES `account` (`AccountNumber`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `IDCU` FOREIGN KEY (`ID`) REFERENCES `customer` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.customeraccount_BEFORE_INSERT$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`customeraccount_BEFORE_INSERT` BEFORE INSERT ON `customeraccount` FOR EACH ROW
BEGIN
if new.ID not in(select IDAO from accountowners where Accountnumber = new.Accountnumber) then 
SIGNAL sqlstate '45001'set message_text = "You Are Not Owner Of The Account !";
end if;
END$$
DELIMITER ;

CREATE TABLE `customeraddresses` (
  `IDC` int(11) NOT NULL,
  `Streetnumber` int(11) NOT NULL,
  `StreetName` varchar(45) NOT NULL,
  `City` varchar(45) NOT NULL,
  `State` varchar(45) NOT NULL,
  PRIMARY KEY (`IDC`,`Streetnumber`,`StreetName`,`City`,`State`),
  CONSTRAINT `IDCA` FOREIGN KEY (`IDC`) REFERENCES `customer` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.customeraddresses_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`customeraddresses_BEFORE_DELETE` BEFORE DELETE ON `customeraddresses` FOR EACH ROW
BEGIN
if not exists (select * from TheDeletedcustomeraddresses where IDC = old.IDC and Streetnumber = old.Streetnumber and StreetName = old.StreetName and City = old.City and State = old.state) then
insert into TheDeletedcustomeraddresses (`IDC`,
`Streetnumber`,
`StreetName`,
`City`,
`State`)
select * from customeraddresses where IDC = old.IDC;
end if;
END$$
DELIMITER ;

CREATE TABLE `customerphonenumbers` (
  `IDC` int(11) NOT NULL,
  `PhoneNumber` varchar(20) NOT NULL,
  PRIMARY KEY (`IDC`,`PhoneNumber`),
  CONSTRAINT `IDC` FOREIGN KEY (`IDC`) REFERENCES `customer` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.customerphonenumbers_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`customerphonenumbers_BEFORE_DELETE` BEFORE DELETE ON `customerphonenumbers` FOR EACH ROW
BEGIN
if not exists (select * from TheDeletedcustomerphonenumbers where IDC = old.IDC and phonenumber = old.phonenumber) then
INSERT INTO `electronicbankingsoftware`.`TheDeletedcustomerphonenumbers`
(`IDC`,
`PhoneNumber`)
select * from customerphonenumbers where IDC = old.IDC;
end if;
END$$
DELIMITER ;

CREATE TABLE `customoraccesslog` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `IDAO` int(11) NOT NULL,
  `AccountNumber` int(11) NOT NULL,
  `Operation` varchar(45) NOT NULL,
  `NewValue` tinyint(1) DEFAULT NULL,
  `Date` datetime NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `paymentorder` (
  `IDP` int(11) NOT NULL AUTO_INCREMENT,
  `NCCreator` varchar(20) NOT NULL,
  `FullPrice` int(11) DEFAULT '0',
  `SourceAccount` int(11) NOT NULL,
  `IDPaymentVerifier` int(11) DEFAULT NULL,
  `NoteOfCreator` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`IDP`),
  KEY `IDCreator_idx` (`NCCreator`),
  KEY `SA_idx` (`SourceAccount`),
  KEY `IDPV_idx` (`IDPaymentVerifier`),
  CONSTRAINT `IDPV` FOREIGN KEY (`IDPaymentVerifier`) REFERENCES `customer` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `NCC` FOREIGN KEY (`NCCreator`) REFERENCES `customer` (`NationalCode`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `SA` FOREIGN KEY (`SourceAccount`) REFERENCES `account` (`AccountNumber`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.paymentorder_BEFORE_INSERT$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`paymentorder_BEFORE_INSERT` BEFORE INSERT ON `paymentorder` FOR EACH ROW
BEGIN
Set new.IDPaymentVerifier = Null;
Set new.FullPrice = 0;
if  new.NCCreator not in (select nationalcode from accountowners inner join customer on IDAO = ID where PaymentAccess = 1 and  accountowners.AccountNumber = new.SourceAccount)
then 
SIGNAL sqlstate '45001' set message_text = "Dont Have Access To Pay !";
end if;

END$$
DELIMITER ;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.paymentorder_BEFORE_UPDATE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`paymentorder_BEFORE_UPDATE` BEFORE UPDATE ON `paymentorder` FOR EACH ROW
BEGIN
declare numOfSigns int;
declare numOfRequiredSigns int;
set numOfSigns = (select numOfSigns(new.IDP));
set numOfRequiredSigns = (select NumberOfRequiredSignatures from electronicbankingsoftware.`account` where AccountNumber = new.SourceAccount);
if old.NCCreator <> new.NCCreator then
 SIGNAL sqlstate '45001' set message_text = "You Cant Creat PaymentOrder !";
end if;

if new.IDPaymentVerifier is not null then
begin

if new.IDPaymentVerifier  not in (select IDAO from accountowners where PaymentAccess = 1 and  accountowners.AccountNumber = new.SourceAccount)
then 
SIGNAL sqlstate '45001' set message_text = "Dont Have Access To Pay !";

elseif numOfSigns < numOfRequiredSigns then
SIGNAL sqlstate '45001' set message_text = "Not Enough Signs !";

elseif  numOfSigns > 0 and old.IDPaymentVerifier is not null 
then
 SIGNAL sqlstate '45001' set message_text = "You Cant Edit PaymentOrder !";
elseif old.IDPaymentVerifier is null 
then
begin

INSERT INTO `electronicbankingsoftware`.`bill`
(`AccountNumber`,
`IDP`,
`Amount`,
`Notes`,
`KindOfBill`,
`Date`)
VALUES
(new.SourceAccount,
new.IDP,
new.FullPrice,
new.NoteOfCreator,
'Withdraw',
CURRENT_TIMESTAMP);

INSERT INTO `electronicbankingsoftware`.`bill`
(`AccountNumber`,
`IDP`,
`Amount`,
`Notes`,
`KindOfBill`)
select DestAccountNumber,new.IDP,Price,new.NoteOfCreator,'Deposit'  from paymentOrder  natural join `transaction` where `transaction`.IDP = new.IDP;
end;
INSERT INTO `electronicbankingsoftware`.`accountlog`
(
`AccountNumber`,
`IDC`,
`Operation`,
`IDP`)
VALUES
(
new.SourceAccount,
new.IDPaymentVerifier ,
'Payed',
new.IDP);

end if;

end;
end if;

END$$
DELIMITER ;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.paymentorder_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`paymentorder_BEFORE_DELETE` BEFORE DELETE ON `paymentorder` FOR EACH ROW
BEGIN
if not exists(select * from thedeletedpaymentorder where IDP = old.IDP) then
INSERT INTO `electronicbankingsoftware`.`thedeletedpaymentorder`
(`IDP`,
`NCCreator`,
`FullPrice`,
`SourceAccount`,
`IDPaymentVerifier`,
`NoteOfCreator`)
VALUES
(old.IDP,
old.NCCreator,
old.FullPrice,
old.SourceAccount,
old.IDPaymentVerifier,
old.NoteOfCreator);
end if;
END$$
DELIMITER ;

CREATE TABLE `signers` (
  `IDS` int(11) NOT NULL,
  `IDPO` int(11) NOT NULL,
  PRIMARY KEY (`IDS`,`IDPO`),
  KEY `IDPO_idx` (`IDPO`),
  CONSTRAINT `IDPO` FOREIGN KEY (`IDPO`) REFERENCES `paymentorder` (`IDP`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `IDS` FOREIGN KEY (`IDS`) REFERENCES `accountowners` (`IDAO`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.signers_BEFORE_INSERT$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`signers_BEFORE_INSERT` BEFORE INSERT ON `signers` FOR EACH ROW
BEGIN
if new.IDS not in(select IDAO from accountowners where SignatureAccess = 1  and  AccountNumber in (select SourceAccount from PaymentOrder where PaymentOrder.IDP = new.IDPO)) then
SIGNAL sqlstate '45001' set message_text = "Dont Have Access To Sign !";
else
INSERT INTO `electronicbankingsoftware`.`accountlog`
(
`AccountNumber`,
`IDC`,
`Operation`,
`IDP`
)
VALUES
(
(select sourceAccount from paymentorder where IDP = new.IDPO),
new.IDS,
'Signed',
new.IDPO);
end if;
END$$
DELIMITER ;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.signers_BEFORE_UPDATE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`signers_BEFORE_UPDATE` BEFORE UPDATE ON `signers` FOR EACH ROW
BEGIN
call checkSignatureAccess(new.IDS, new.IDPO,old.IDS,old.IDPO);
if new.IDS not in(select IDAO from accountowners where SignatureAccess = 1  and AccountNumber in (select SourceAccount from PaymentOrder where PaymentOrder.IDP = new.IDPO)) then
SIGNAL sqlstate '45001' set message_text = "Dont Have Access To Sign !";
else 
update accountlog set IDC = new.IDS, IDP = new.IDPO where IDC = old.IDS and IDP = old.IDPO;
end if;
END$$
DELIMITER ;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.signers_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`signers_BEFORE_DELETE` BEFORE DELETE ON `signers` FOR EACH ROW
BEGIN

if PaymentOrderIsPayed(old.IDPO) then
SIGNAL sqlstate '45001' set message_text = "You Cant Remove Your Sign The Order Is Payed !";
else
INSERT INTO `electronicbankingsoftware`.`accountlog`
(
`AccountNumber`,
`IDC`,
`Operation`,
`IDP`
)
VALUES
(
(select sourceAccount from paymentorder where IDP = old.IDPO),
old.IDS,
'UnSigned',
old.IDPO);
if not exists(select * from thedeletedsigners where IDS = old.IDS and IDPO = old.IDPO) then
INSERT INTO `electronicbankingsoftware`.`thedeletedsigners`
(`IDS`,
`IDPO`)
VALUES
(old.IDS,
old.IDPO);
end if;
end if;
END$$
DELIMITER ;

CREATE TABLE `thedeletedaccount` (
  `AccountNumber` int(11) NOT NULL,
  `Balance` int(11) NOT NULL DEFAULT '0',
  `NumberOfRequiredSignatures` int(11) NOT NULL DEFAULT '1',
  `KindOfAccount` varchar(45) NOT NULL,
  PRIMARY KEY (`AccountNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedaccountowners` (
  `AccountNumber` int(11) NOT NULL,
  `IDAO` int(11) NOT NULL,
  `ViewAccess` tinyint(1) DEFAULT '0',
  `SignatureAccess` tinyint(1) DEFAULT '0',
  `PaymentAccess` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`AccountNumber`,`IDAO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedbill` (
  `AccountNumber` int(11) NOT NULL,
  `IDP` int(11) NOT NULL,
  `Amount` int(11) NOT NULL,
  `Notes` varchar(45) DEFAULT NULL,
  `KindOfBill` varchar(45) DEFAULT NULL,
  `Date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`AccountNumber`,`IDP`,`Amount`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedcustomer` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NationalCode` varchar(20) NOT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `LastName` varchar(45) DEFAULT NULL,
  `Password` varchar(45) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `NationalCode_UNIQUE` (`NationalCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedcustomeraddresses` (
  `IDC` int(11) NOT NULL,
  `Streetnumber` int(11) NOT NULL,
  `StreetName` varchar(45) NOT NULL,
  `City` varchar(45) NOT NULL,
  `State` varchar(45) NOT NULL,
  PRIMARY KEY (`IDC`,`Streetnumber`,`StreetName`,`City`,`State`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedcustomerphonenumbers` (
  `IDC` int(11) NOT NULL,
  `PhoneNumber` varchar(20) NOT NULL,
  PRIMARY KEY (`IDC`,`PhoneNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedpaymentorder` (
  `IDP` int(11) NOT NULL AUTO_INCREMENT,
  `NCCreator` varchar(20) NOT NULL,
  `FullPrice` int(11) DEFAULT '0',
  `SourceAccount` int(11) NOT NULL,
  `IDPaymentVerifier` int(11) DEFAULT NULL,
  `NoteOfCreator` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`IDP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedsigners` (
  `IDS` int(11) NOT NULL,
  `IDPO` int(11) NOT NULL,
  PRIMARY KEY (`IDS`,`IDPO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `thedeletedtransaction` (
  `IDP` int(11) NOT NULL,
  `DestAccountNumber` int(11) NOT NULL,
  `Price` int(11) DEFAULT '0',
  PRIMARY KEY (`IDP`,`DestAccountNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `transaction` (
  `IDP` int(11) NOT NULL,
  `DestAccountNumber` int(11) NOT NULL,
  `Price` int(11) DEFAULT '0',
  PRIMARY KEY (`IDP`,`DestAccountNumber`),
  KEY `DA_idx` (`DestAccountNumber`),
  CONSTRAINT `DA` FOREIGN KEY (`DestAccountNumber`) REFERENCES `account` (`AccountNumber`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `IDPT` FOREIGN KEY (`IDP`) REFERENCES `paymentorder` (`IDP`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DELIMITER $$

DROP TRIGGER IF EXISTS electronicbankingsoftware.transaction_BEFORE_INSERT$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`transaction_BEFORE_INSERT` BEFORE INSERT ON `transaction` FOR EACH ROW
BEGIN
update PaymentOrder set FullPrice = FullPrice + new.Price where PaymentOrder.IDP = new.IDP;
END$$
DELIMITER ;

DELIMITER $$
DROP TRIGGER IF EXISTS electronicbankingsoftware.transaction_BEFORE_UPDATE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`transaction_BEFORE_UPDATE` BEFORE UPDATE ON `transaction` FOR EACH ROW
BEGIN
if new.Price <> old.Price  then
update PaymentOrder set FullPrice = FullPrice + (new.Price - old.Price) where PaymentOrder.IDP = new.IDP;
end if;
if PaymentOrderIsPayed(old.IDP )  and  numOfSigns(old.IDP) > 0 then
SIGNAL sqlstate '45001' set message_text = "You Cant Edit Transaction !";

end if;
END$$
DELIMITER ;

DELIMITER $$
DROP TRIGGER IF EXISTS electronicbankingsoftware.transaction_BEFORE_DELETE$$
CREATE DEFINER=`root`@`localhost` TRIGGER `electronicbankingsoftware`.`transaction_BEFORE_DELETE` BEFORE DELETE ON `transaction` FOR EACH ROW
BEGIN
if  PaymentOrderIsPayed(old.IDP) and  numOfSigns(old.IDP) > 0  then
SIGNAL sqlstate '45001' set message_text = "You Cant Delete Transaction !";
else
begin
update PaymentOrder set FullPrice = FullPrice - old.Price where PaymentOrder.IDP = old.IDP;
INSERT INTO `electronicbankingsoftware`.`thedeletedtransaction`
(`IDP`,
`DestAccountNumber`,
`Price`)
VALUES
(old.IDP,
old.DestAccountNumber,
old.Price);
end;
end if;
END$$
DELIMITER ;

select TABLE_NAME,CREATE_TIME,UPDATE_TIME from information_schema.TABLES where Table_Schema = 'electronicbankingsoftware';
