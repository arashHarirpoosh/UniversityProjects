CALL `electronicbankingsoftware`.`addCustomer`(<{NC varchar(45)}>, <{FN Varchar(45)}>, <{LN Varchar(45)}>, <{P Varchar(45)}>); /* 1 */

CALL `electronicbankingsoftware`.`addAccount`(<{AN Int}>, <{B Int}>, <{NORS Int}>, <{KOA Varchar(45)}>); /* 2 */

CALL `electronicbankingsoftware`.`AddOwnerToTheAccount`(<{AN Int}>, <{IDA Int}>, <{VA tinyint(1)}>, <{SA tinyint(1)}>, <{PA tinyint(1)}>); /* 3 */

CALL `electronicbankingsoftware`.`EditAccess`(<{AN Int}>, <{IDA Int}>, <{KindOfAccess varchar(45)}>, <{AccessValue tinyint(1)}>); /* 3 */

CALL `electronicbankingsoftware`.`EditAllAccess`(<{AN Int}>, <{IDA Int}>, <{VA tinyint(1)}>, <{SA tinyint(1)}>, <{PA tinyint(1)}>); /* 3 */

CALL `electronicbankingsoftware`.`removeAccess`(<{AN Int}>, <{IDA Int}>, <{KindOfAccess varchar(45)}>); /* 3 */

CALL `electronicbankingsoftware`.`createPaymentOrder`(<{NCC VarChar(20)}>, <{SA Int}>, <{NOC Varchar(45)}>); /* 4 */

CALL `electronicbankingsoftware`.`EditOrDeletePaymentOrder`(<{IDPO Int}>, <{kindOfOperation Varchar(45)}>, <{NCC Varchar(20)}>, <{SA Int}>, <{IDPV Int}>, <{NOC varchar(45)}>); /* 5 */

CALL `electronicbankingsoftware`.`updateNCCreator`(<{IDPO Int}>, <{ANCC VArchar(20)}>, <{NNCC Varchar(20)}>); /* 5 */

CALL `electronicbankingsoftware`.`SignedAndUnsignedPayment`(<{IDC Int}>, <{IDP Int}>, <{kindOfOperation Varchar(45)}>); /* 6 */

CALL `electronicbankingsoftware`.`EditDeleteCreateTransaction`(<{ID Int}>, <{DAN Int}>, <{P Int}>, <{kindOfOperation varchar(45)}>, <{NIDP Int}>, <{NDAN Int}>); /* 7 */

CALL `electronicbankingsoftware`.`PayPaymentOrder`(<{IDPO Int}>, <{IDPV Int}>); /* 8 */

CALL `electronicbankingsoftware`.`ADDBill`(<{ANB Int}>, <{IDPB Int}>, <{price Int}>, <{kind varchar(45)}>, <{NB varchar(45)}>, <{BD datetime}>); /* 9 */
