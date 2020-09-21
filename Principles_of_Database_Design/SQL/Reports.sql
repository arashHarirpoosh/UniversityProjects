select * from customersignedatleastone;	/* 1 */

select * from moresigneraccess;	/* 2 */

/*select * from moresigners; /* 2 */

select * from readytopayed; /* 3 */

CALL `electronicbankingsoftware`.`TransactionOfDestAccount`(<{AN Int}>); /* 4 */

CALL `electronicbankingsoftware`.`CustomorUnsigned`(<{IDCC Int}>); /* 5 */

CALL `electronicbankingsoftware`.`CommonAccountBetween2Customer`(<{IDAO1 Int}>, <{IDAO2 Int}>); /* 6 */

CALL `electronicbankingsoftware`.`PaymentOrderSignAccessCustomer`(<{ID Int}>); /* 7 */

/*select * from `onesigneraccessforsignpayment`; /* 7 */

select * from transactionthatcreatercantsign; /* 8 */

CALL `electronicbankingsoftware`.`DepositForAccountMoreThanCertainAmaount`(<{An Int}>, <{Am Int}>); /* 9 */




