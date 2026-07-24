# Catalyst Data Store — Table Creation Checklist

Create these in the console: **Cloud Scale → Data Store → Create a New Table**,
then add columns one by one (**New Column** button, pick data type + max length,
tick "Mandatory" for NOT NULL columns marked below).

Build in this exact order — each table only references ones already created,
so you never hit a "referenced table doesn't exist yet" dead end.

Catalyst data types you'll use: **Var Char** (text), **Text** (long text, use
NVARCHAR MAX equivalent), **Big Int** (INT/PK/FK), **Date**, **Date Time**,
**Decimal**, **Boolean** (BIT).

## Batch 1 — Independent lookups (no FK dependencies)

| Table | Columns (name : type : notes) |
|---|---|
| State | StateID: BigInt (mandatory, unique) · StateName: VarChar(100) · NationalityID: BigInt · Active: Boolean |
| UnitType | UnitTypeID: BigInt (mandatory, unique) · UnitTypeName: VarChar(100) · CityDistState: VarChar(20) · Hierarchy: BigInt · Active: Boolean |
| Rank | RankID: BigInt (mandatory, unique) · RankName: VarChar(100) · Hierarchy: BigInt · Active: Boolean |
| Designation | DesignationID: BigInt (mandatory, unique) · DesignationName: VarChar(100) · Active: Boolean · SortOrder: BigInt |
| CaseCategory | CaseCategoryID: BigInt (mandatory, unique) · LookupValue: VarChar(50) |
| GravityOffence | GravityOffenceID: BigInt (mandatory, unique) · LookupValue: VarChar(50) |
| CaseStatusMaster | CaseStatusID: BigInt (mandatory, unique) · CaseStatusName: VarChar(100) |
| CrimeHead | CrimeHeadID: BigInt (mandatory, unique) · CrimeGroupName: VarChar(150) · Active: Boolean |
| Act | ActCode: VarChar(20) (mandatory, unique — this is the PK) · ActDescription: VarChar(200) · ShortName: VarChar(50) · Active: Boolean |
| CasteMaster | caste_master_id: BigInt (mandatory, unique) · caste_master_name: VarChar(100) |
| ReligionMaster | ReligionID: BigInt (mandatory, unique) · ReligionName: VarChar(100) |
| OccupationMaster | OccupationID: BigInt (mandatory, unique) · OccupationName: VarChar(100) |

## Batch 2 — Depends on Batch 1

| Table | Columns |
|---|---|
| District | DistrictID: BigInt (mandatory, unique) · DistrictName: VarChar(100) · StateID: BigInt (FK→State) · Active: Boolean |
| CrimeSubHead | CrimeSubHeadID: BigInt (mandatory, unique) · CrimeHeadID: BigInt (FK→CrimeHead) · CrimeHeadName: VarChar(150) · SeqID: BigInt |
| Section | ActCode: VarChar(20) (FK→Act) · SectionCode: VarChar(20) · SectionDescription: VarChar(300) · Active: Boolean — *composite key ActCode+SectionCode, but Catalyst Data Store needs a single unique column: add a surrogate `SectionRowKey` VarChar(40) as mandatory/unique = ActCode+"_"+SectionCode* |

## Batch 3 — Depends on Batch 2

| Table | Columns |
|---|---|
| Unit | UnitID: BigInt (mandatory, unique) · UnitName: VarChar(150) · TypeID: BigInt (FK→UnitType) · ParentUnit: BigInt · NationalityID: BigInt · StateID: BigInt (FK→State) · DistrictID: BigInt (FK→District) · Active: Boolean |
| Court | CourtID: BigInt (mandatory, unique) · CourtName: VarChar(150) · DistrictID: BigInt (FK→District) · StateID: BigInt (FK→State) · Active: Boolean |
| CrimeHeadActSection | RowKey: VarChar(60) (mandatory, unique, surrogate) · CrimeHeadID: BigInt (FK→CrimeHead) · ActCode: VarChar(20) · SectionCode: VarChar(20) |

## Batch 4 — Depends on Batch 3

| Table | Columns |
|---|---|
| Employee | EmployeeID: BigInt (mandatory, unique) · DistrictID: BigInt (FK→District) · UnitID: BigInt (FK→Unit) · RankID: BigInt (FK→Rank) · DesignationID: BigInt (FK→Designation) · KGID: VarChar(50) · FirstName: VarChar(100) · EmployeeDOB: Date · GenderID: BigInt · BloodGroupID: BigInt · PhysicallyChallenged: Boolean · AppointmentDate: Date |

## Batch 5 — The core FIR table (depends on almost everything above)

| Table | Columns |
|---|---|
| CaseMaster | CaseMasterID: BigInt (mandatory, unique) · CrimeNo: VarChar(30) · CaseNo: VarChar(20) · CrimeRegisteredDate: Date · PolicePersonID: BigInt (FK→Employee) · PoliceStationID: BigInt (FK→Unit) · CaseCategoryID: BigInt (FK→CaseCategory) · GravityOffenceID: BigInt (FK→GravityOffence) · CrimeMajorHeadID: BigInt (FK→CrimeHead) · CrimeMinorHeadID: BigInt (FK→CrimeSubHead) · CaseStatusID: BigInt (FK→CaseStatusMaster) · CourtID: BigInt (FK→Court) · IncidentFromDate: DateTime · IncidentToDate: DateTime · InfoReceivedPSDate: DateTime · latitude: Decimal · longitude: Decimal · BriefFacts: Text |

## Batch 6 — Case children (all FK→CaseMaster)

| Table | Columns |
|---|---|
| ComplainantDetails | ComplainantID: BigInt (mandatory, unique) · CaseMasterID: BigInt (FK→CaseMaster) · ComplainantName: VarChar(150) · AgeYear: BigInt · OccupationID: BigInt (FK) · ReligionID: BigInt (FK) · CasteID: BigInt (FK→CasteMaster) · GenderID: BigInt |
| Victim | VictimMasterID: BigInt (mandatory, unique) · CaseMasterID: BigInt (FK→CaseMaster) · VictimName: VarChar(150) · AgeYear: BigInt · GenderID: VarChar(1) · VictimPolice: Boolean |
| Accused | AccusedMasterID: BigInt (mandatory, unique) · CaseMasterID: BigInt (FK→CaseMaster) · AccusedName: VarChar(150) · AgeYear: BigInt · GenderID: VarChar(1) · PersonID: VarChar(10) |
| ActSectionAssociation | RowKey: VarChar(60) (mandatory, unique, surrogate) · CaseMasterID: BigInt (FK→CaseMaster) · ActID: VarChar(20) · SectionID: VarChar(20) · ActOrderID: BigInt · SectionOrderID: BigInt |

## Batch 7 — Depends on Accused/CaseMaster

| Table | Columns |
|---|---|
| ArrestSurrender | ArrestSurrenderID: BigInt (mandatory, unique) · CaseMasterID: BigInt (FK) · ArrestSurrenderTypeID: BigInt · ArrestSurrenderDate: Date · ArrestSurrenderStateId: BigInt (FK→State) · ArrestSurrenderDistrictId: BigInt (FK→District) · PoliceStationID: BigInt (FK→Unit) · IOID: BigInt (FK→Employee) · CourtID: BigInt (FK→Court) · AccusedMasterID: BigInt (FK→Accused) · IsAccused: Boolean · IsComplainantAccused: Boolean |
| ChargesheetDetails | CSID: BigInt (mandatory, unique) · CaseMasterID: BigInt (FK) · csdate: DateTime · cstype: VarChar(1) · PolicePersonID: BigInt (FK→Employee) |

**Important note on the CSVs I generated:** they use plain `ActCode+SectionCode`
composite keys and `CrimeHeadID+ActCode+SectionCode` for junction tables, matching
the ER diagram exactly. Since Catalyst tables need one unique column, add the
surrogate key columns noted above (`SectionRowKey`, `RowKey`) and I'll regenerate
those two CSV files with the extra concatenated column — just tell me once your
tables are created and I'll patch the generator.

## After tables exist: bulk import the CSVs

Install Data Store CLI plugin if not already active, then for each table run:

```
catalyst import --table <TableName> --file ./dataset/output/<TableName>.csv
```

(Exact flag names: run `catalyst import --help` to confirm your CLI version's
syntax — some versions want a `--config` JSON instead of inline flags.)

Import strictly in this order (same as the batches above) so foreign keys never
reference a row that doesn't exist yet:

```
State, UnitType, Rank, Designation, CaseCategory, GravityOffence,
CaseStatusMaster, CrimeHead, Act, CasteMaster, ReligionMaster, OccupationMaster,
District, CrimeSubHead, Section,
Unit, Court, CrimeHeadActSection,
Employee,
CaseMaster,
ComplainantDetails, Victim, Accused, ActSectionAssociation,
ArrestSurrender, ChargesheetDetails
```
