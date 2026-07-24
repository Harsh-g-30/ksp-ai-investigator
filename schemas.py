TABLES = {

    "State": [
        {"name":"StateID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"StateName","type":"Var Char(100)"},
        {"name":"NationalityID","type":"Big Int"},
        {"name":"Active","type":"Boolean"},
    ],

    "UnitType": [
        {"name":"UnitTypeID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"UnitTypeName","type":"Var Char(100)"},
        {"name":"CityDistState","type":"Var Char(20)"},
        {"name":"Hierarchy","type":"Big Int"},
        {"name":"Active","type":"Boolean"},
    ],

    "Rank": [
        {"name":"RankID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"RankName","type":"Var Char(100)"},
        {"name":"Hierarchy","type":"Big Int"},
        {"name":"Active","type":"Boolean"},
    ],

    "Designation": [
        {"name":"DesignationID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"DesignationName","type":"Var Char(100)"},
        {"name":"Active","type":"Boolean"},
        {"name":"SortOrder","type":"Big Int"},
    ],

    "CaseCategory": [
        {"name":"CaseCategoryID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"LookupValue","type":"Var Char(50)"},
    ],

    "GravityOffence": [
        {"name":"GravityOffenceID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"LookupValue","type":"Var Char(50)"},
    ],

    "CaseStatusMaster": [
        {"name":"CaseStatusID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CaseStatusName","type":"Var Char(100)"},
    ],

    "CrimeHead": [
        {"name":"CrimeHeadID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CrimeGroupName","type":"Var Char(150)"},
        {"name":"Active","type":"Boolean"},
    ],

    "Act": [
        {"name":"ActCode","type":"Var Char(20)","mandatory":True,"unique":True},
        {"name":"ActDescription","type":"Var Char(200)"},
        {"name":"ShortName","type":"Var Char(50)"},
        {"name":"Active","type":"Boolean"},
    ],

    "CasteMaster": [
        {"name":"caste_master_id","type":"Big Int","mandatory":True,"unique":True},
        {"name":"caste_master_name","type":"Var Char(100)"},
    ],

    "ReligionMaster": [
        {"name":"ReligionID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"ReligionName","type":"Var Char(100)"},
    ],

    "OccupationMaster": [
        {"name":"OccupationID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"OccupationName","type":"Var Char(100)"},
    ],

    "District": [
        {"name":"DistrictID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"DistrictName","type":"Var Char(100)"},
        {"name":"StateID","type":"Big Int"},
        {"name":"Active","type":"Boolean"},
    ],

    "CrimeSubHead": [
        {"name":"CrimeSubHeadID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CrimeHeadID","type":"Big Int"},
        {"name":"CrimeHeadName","type":"Var Char(150)"},
        {"name":"SeqID","type":"Big Int"},
    ],

    "Section": [
        {"name":"SectionRowKey","type":"Var Char(40)","mandatory":True,"unique":True},
        {"name":"ActCode","type":"Var Char(20)"},
        {"name":"SectionCode","type":"Var Char(20)"},
        {"name":"SectionDescription","type":"Var Char(300)"},
        {"name":"Active","type":"Boolean"},
    ],

        "Unit": [
        {"name":"UnitID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"UnitName","type":"Var Char(150)"},
        {"name":"TypeID","type":"Big Int"},
        {"name":"ParentUnit","type":"Big Int"},
        {"name":"NationalityID","type":"Big Int"},
        {"name":"StateID","type":"Big Int"},
        {"name":"DistrictID","type":"Big Int"},
        {"name":"Active","type":"Boolean"},
    ],

    "Court": [
        {"name":"CourtID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CourtName","type":"Var Char(150)"},
        {"name":"DistrictID","type":"Big Int"},
        {"name":"StateID","type":"Big Int"},
        {"name":"Active","type":"Boolean"},
    ],

    "CrimeHeadActSection": [
        {"name":"RowKey","type":"Var Char(60)","mandatory":True,"unique":True},
        {"name":"CrimeHeadID","type":"Big Int"},
        {"name":"ActCode","type":"Var Char(20)"},
        {"name":"SectionCode","type":"Var Char(20)"},
    ],

        "Employee": [
        {"name":"EmployeeID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"DistrictID","type":"Big Int"},
        {"name":"UnitID","type":"Big Int"},
        {"name":"RankID","type":"Big Int"},
        {"name":"DesignationID","type":"Big Int"},
        {"name":"KGID","type":"Var Char(50)"},
        {"name":"FirstName","type":"Var Char(100)"},
        {"name":"EmployeeDOB","type":"Date"},
        {"name":"GenderID","type":"Big Int"},
        {"name":"BloodGroupID","type":"Big Int"},
        {"name":"PhysicallyChallenged","type":"Boolean"},
        {"name":"AppointmentDate","type":"Date"},
    ],

        "CaseMaster": [
        {"name":"CaseMasterID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CrimeNo","type":"Var Char(30)"},
        {"name":"CaseNo","type":"Var Char(20)"},
        {"name":"CrimeRegisteredDate","type":"Date"},
        {"name":"PolicePersonID","type":"Big Int"},
        {"name":"PoliceStationID","type":"Big Int"},
        {"name":"CaseCategoryID","type":"Big Int"},
        {"name":"GravityOffenceID","type":"Big Int"},
        {"name":"CrimeMajorHeadID","type":"Big Int"},
        {"name":"CrimeMinorHeadID","type":"Big Int"},
        {"name":"CaseStatusID","type":"Big Int"},
        {"name":"CourtID","type":"Big Int"},
        {"name":"IncidentFromDate","type":"Date Time"},
        {"name":"IncidentToDate","type":"Date Time"},
        {"name":"InfoReceivedPSDate","type":"Date Time"},
        {"name":"latitude","type":"Decimal"},
        {"name":"longitude","type":"Decimal"},
        {"name":"BriefFacts","type":"Text"},
    ],

        "ComplainantDetails": [
        {"name":"ComplainantID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CaseMasterID","type":"Big Int"},
        {"name":"ComplainantName","type":"Var Char(150)"},
        {"name":"AgeYear","type":"Big Int"},
        {"name":"OccupationID","type":"Big Int"},
        {"name":"ReligionID","type":"Big Int"},
        {"name":"CasteID","type":"Big Int"},
        {"name":"GenderID","type":"Big Int"},
    ],

        "Victim": [
        {"name":"VictimMasterID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CaseMasterID","type":"Big Int"},
        {"name":"VictimName","type":"Var Char(150)"},
        {"name":"AgeYear","type":"Big Int"},
        {"name":"GenderID","type":"Var Char(1)"},
        {"name":"VictimPolice","type":"Boolean"},
    ],

        "Accused": [
        {"name":"AccusedMasterID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CaseMasterID","type":"Big Int"},
        {"name":"AccusedName","type":"Var Char(150)"},
        {"name":"AgeYear","type":"Big Int"},
        {"name":"GenderID","type":"Var Char(1)"},
        {"name":"PersonID","type":"Var Char(10)"},
    ],

        "ActSectionAssociation": [
        {"name":"RowKey","type":"Var Char(60)","mandatory":True,"unique":True},
        {"name":"CaseMasterID","type":"Big Int"},
        {"name":"ActID","type":"Var Char(20)"},
        {"name":"SectionID","type":"Var Char(20)"},
        {"name":"ActOrderID","type":"Big Int"},
        {"name":"SectionOrderID","type":"Big Int"},
    ],

        "ArrestSurrender": [
        {"name":"ArrestSurrenderID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CaseMasterID","type":"Big Int"},
        {"name":"ArrestSurrenderTypeID","type":"Big Int"},
        {"name":"ArrestSurrenderDate","type":"Date"},
        {"name":"ArrestSurrenderStateId","type":"Big Int"},
        {"name":"ArrestSurrenderDistrictId","type":"Big Int"},
        {"name":"PoliceStationID","type":"Big Int"},
        {"name":"IOID","type":"Big Int"},
        {"name":"CourtID","type":"Big Int"},
        {"name":"AccusedMasterID","type":"Big Int"},
        {"name":"IsAccused","type":"Boolean"},
        {"name":"IsComplainantAccused","type":"Boolean"},
    ],

        "ChargesheetDetails": [
        {"name":"CSID","type":"Big Int","mandatory":True,"unique":True},
        {"name":"CaseMasterID","type":"Big Int"},
        {"name":"csdate","type":"Date Time"},
        {"name":"cstype","type":"Var Char(1)"},
        {"name":"PolicePersonID","type":"Big Int"},
    ],

}


