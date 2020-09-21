DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `addAccount`(AN Int, B Int, NORS Int, KOA Varchar(45))
BEGIN
INSERT INTO `electronicbankingsoftware`.`account`
(`AccountNumber`,
`Balance`,
`NumberOfRequiredSignatures`,
`KindOfAccount`)
VALUES
(AN,
B,
NORS,
KOA);

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `ADDBill`(ANB Int, IDPB Int, price Int, kind varchar(45), NB varchar(45), BD datetime)
BEGIN
if kind = 'Withdraw' then
INSERT INTO `electronicbankingsoftware`.`bill`
(`AccountNumber`,
`IDP`,
`Amount`,
`Notes`,
`KindOfBill`,
`Date`)
VALUES
(ANB,
IDPB,
price,
NB,
'Withdraw',
BD);

elseif kind = 'Deposit' then
INSERT INTO `electronicbankingsoftware`.`bill`
(`AccountNumber`,
`IDP`,
`Amount`,
`Notes`,
`KindOfBill`,
`Date`)
VALUES
(ANB,
IDPB,
price,
NB,
'Deposit',
BD);
end if;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `addCustomer`(NC varchar(45), FN Varchar(45), LN Varchar(45), P Varchar(45) )
BEGIN
INSERT INTO `electronicbankingsoftware`.`customer`
(
`NationalCode`,
`FirstName`,
`LastName`,
`Password`)
VALUES
(NC,
FN,
LN,
P);

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `AddOwnerToTheAccount`(AN Int, IDA Int,VA tinyint(1),SA tinyint(1), PA tinyint(1))
BEGIN
INSERT INTO `electronicbankingsoftware`.`accountowners`
(`AccountNumber`,
`IDAO`,
`ViewAccess`,
`SignatureAccess`,
`PaymentAccess`)
VALUES
(AN,
IDA,
VA,
SA,
PA);

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `checkSignatureAccess`(NIDS Int, NIDPO Int,OIDS Int,OIDPO Int)
BEGIN
if NIDS not in(select IDAO from accountowners where SignatureAccess = 1  and AccountNumber in (select SourceAccount from PaymentOrder where PaymentOrder.IDP = NIDPO)) then
rollback;
else
update accountlog set IDC = OIDS, IDP = OIDPO where IDC = OIDS and IDP = OIDPO;
end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `CommonAccountBetween2Customer`(IDAO1 Int, IDAO2 Int)
BEGIN
select a1.AccountNumber, a1.IDAO,a2.AccountNumber,a2.IDAO from accountowners as a1 , accountowners as a2 where a1.IDAO = IDAO1 and a2.IDAO = IDAO2 and a1.accountnumber = a2.accountnumber;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `createPaymentOrder`(NCC VarChar(20), SA Int, NOC Varchar(45))
BEGIN
INSERT INTO `electronicbankingsoftware`.`paymentorder`
(
`NCCreator`,
`SourceAccount`,
`NoteOfCreator`)
VALUES
(
NCC,
SA,
NOC);

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `CustomorUnsigned`(IDCC Int)
BEGIN
select AccountNumber, IDC, IDP from accountlog where Operation = 'UnSigned' and IDC = IDCC;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `DepositForAccountMoreThanCertainAmaount`(An Int, Am Int)
BEGIN
select * from bill where (KindOfBill = 'Deposit' and Amount > AM and AccountNumber = An);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `EditAccess`(AN Int, IDA Int, KindOfAccess varchar(45), AccessValue tinyint(1))
BEGIN
if KindOfAccess = 'View' then

UPDATE `electronicbankingsoftware`.`accountowners`
SET
`ViewAccess` = AccessValue
WHERE `AccountNumber` = AN AND `IDAO` = IDA;

elseif KindOfAccess = 'SignatureAccess' then

UPDATE `electronicbankingsoftware`.`accountowners`
SET
`SignatureAccess` = AccessValue
WHERE `AccountNumber` = AN AND `IDAO` = IDA;

elseif KindOfAccess = 'PaymentAccess' then
UPDATE `electronicbankingsoftware`.`accountowners`
SET
`PaymentAccess` = AccessValue
WHERE `AccountNumber` = AN AND `IDAO` = IDA;

end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `EditAllAccess`(AN Int, IDA Int,VA tinyint(1),SA tinyint(1), PA tinyint(1))
BEGIN
UPDATE `electronicbankingsoftware`.`accountowners`
SET
`AccountNumber` = AN,
`IDAO` = IDA,
`ViewAccess` = VA,
`SignatureAccess` = SA,
`PaymentAccess` = PA
WHERE `AccountNumber` = AN AND `IDAO` = IDA;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `EditDeleteCreateTransaction`(ID Int, DAN Int,P Int,kindOfOperation varchar(45), NIDP Int, NDAN Int)
BEGIN
if kindOfOperation = 'Create' then
	INSERT INTO `electronicbankingsoftware`.`transaction`
	(`IDP`,
	`DestAccountNumber`,
	`Price`)
	VALUES
	(ID,
	DAN,
	P);
elseif kindOfOperation = 'Edit'  then
	if PaymentOrderIsPayed(ID )  and  numOfSigns(ID) > 0 then
		rollback;
	else
		UPDATE `electronicbankingsoftware`.`transaction`
		SET
		`IDP` = NIDP,
		`DestAccountNumber` = NDAN,
		`Price` = P
		WHERE `IDP` = ID AND `DestAccountNumber` = DAN;
    end if;
elseif kindOfOperation = 'Deleted' then
	if PaymentOrderIsPayed(ID )  and  numOfSigns(ID) > 0 then
		rollback;
	else
		DELETE FROM `electronicbankingsoftware`.`transaction`
		WHERE `IDP` = ID AND `DestAccountNumber` = DAN;
	end if;
end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `EditOrDeletePaymentOrder`(IDPO Int,kindOfOperation Varchar(45), NCC Varchar(20), SA Int, IDPV Int, NOC varchar(45))
BEGIN
if kindOfOperation = 'Edit' and NCC = getNC(IDPO)  then
UPDATE `electronicbankingsoftware`.`paymentorder`
SET
`NCCreator` = NCC,
`SourceAccount` = SA,
`IDPaymentVerifier` = IDPV,
`NoteOfCreator` = NOC
WHERE `IDP` = IDPO;

elseif kindOfOperation = 'Delete' then 
DELETE FROM `electronicbankingsoftware`.`paymentorder`
WHERE `IDP` = IDPO;
end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `new_procedure`(An Int, Am Int)
BEGIN
select * from bill where (KindOfBill = 'Deposit' and Amount > AM and AccountNumber = An);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `PaymentOrderSignAccessCustomer`(ID Int)
BEGIN
select * from paymentorder where SourceAccount in(
select AccountNumber from accountowners where SignatureAccess = true and IDAO = ID);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `PayPaymentOrder`(IDPO Int, IDPV Int)
BEGIN
UPDATE `electronicbankingsoftware`.`paymentorder`
SET
`IDPaymentVerifier` = IDPV
WHERE `IDP` = IDPO;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `removeAccess`(AN Int, IDA Int, KindOfAccess varchar(45))
BEGIN
if KindOfAccess = 'View' then
UPDATE `electronicbankingsoftware`.`accountowners`
SET
`ViewAccess` = false
WHERE `AccountNumber` = AN AND `IDAO` = IDA;

elseif KindOfAccess = 'SignatureAccess' then
UPDATE `electronicbankingsoftware`.`accountowners`
SET
`SignatureAccess` = false
WHERE `AccountNumber` = AN AND `IDAO` = IDA;

elseif KindOfAccess = 'PaymentAccess' then
UPDATE `electronicbankingsoftware`.`accountowners`
SET
`PaymentAccess` = false
WHERE `AccountNumber` = AN AND `IDAO` = IDA;
end if;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `SignedAndUnsignedPayment`(IDC Int, IDP Int,kindOfOperation Varchar(45))
BEGIN
if kindOfOperation = 'Signed' then
INSERT INTO `electronicbankingsoftware`.`signers`
(`IDS`,
`IDPO`)
VALUES
(IDC,
IDP);

elseif kindOfOperation = 'Unsigned' then
DELETE FROM `electronicbankingsoftware`.`signers`
WHERE `IDS` = IDC and `IDPO` = IDP;

end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `TransactionOfDestAccount`(AN Int)
BEGIN
select readytopayed.IDP,DestAccountNumber,Price from readytopayed inner join `transaction` on readytopayed.IDP = `transaction`.IDP where DestAccountNumber = AN;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `updateNCCreator`(IDPO Int, ANCC VArchar(20), NNCC Varchar(20))
BEGIN
/* Get The NCC Person Who Wants To Update The NCCreator */
if ANCC = getNC(IDPO) then
UPDATE `electronicbankingsoftware`.`paymentorder`
SET
`NCCreator` = NNCC
WHERE `IDP` = IDPO;
else
rollback;
end if;
END$$
DELIMITER ;
