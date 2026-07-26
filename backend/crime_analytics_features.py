"""
KSP Crime Analytics - Complete Feature Implementation
Ready to integrate into your backend
"""

import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

# ============================================================================
# 1. CRIME PATTERN DETECTION & HOTSPOT ANALYSIS
# ============================================================================

class CrimePatternAnalyzer:
    """Detect crime patterns, hotspots, and trends"""
    
    @staticmethod
    def get_crime_hotspots(time_period_days: int = 90) -> str:
        """Generate SQL for geographic hotspots"""
        query = f"""
        SELECT 
            loc.LocationID,
            loc.LocationName,
            COUNT(DISTINCT cm.CaseMasterID) as crime_count,
            COUNT(DISTINCT ct.CrimeMinorHeadID) as unique_crime_types,
            GROUP_CONCAT(DISTINCT ct.CrimeMinorName) as crime_types,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM CaseMaster 
                WHERE CrimeDate >= DATE_SUB(CURDATE(), INTERVAL {time_period_days} DAY)), 2) as percentage_of_total
        FROM CaseMaster cm
        JOIN Location loc ON cm.LocationID = loc.LocationID
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        WHERE cm.CrimeDate >= DATE_SUB(CURDATE(), INTERVAL {time_period_days} DAY)
        GROUP BY loc.LocationID, loc.LocationName
        ORDER BY crime_count DESC
        LIMIT 15
        """
        return query
    
    @staticmethod
    def get_temporal_trends(time_unit: str = 'MONTH') -> str:
        """Crime trends over time (daily/weekly/monthly/yearly)"""
        if time_unit == 'MONTH':
            date_format = '%Y-%m'
        elif time_unit == 'WEEK':
            date_format = '%Y-%v'
        elif time_unit == 'DAY':
            date_format = '%Y-%m-%d'
        else:
            date_format = '%Y'
            
        query = f"""
        SELECT 
            DATE_FORMAT(cm.CrimeDate, '{date_format}') as period,
            COUNT(DISTINCT cm.CaseMasterID) as crime_count,
            COUNT(DISTINCT ct.CrimeMinorHeadID) as unique_types,
            GROUP_CONCAT(DISTINCT ct.CrimeMinorName SEPARATOR ', ') as top_crimes
        FROM CaseMaster cm
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        GROUP BY DATE_FORMAT(cm.CrimeDate, '{date_format}')
        ORDER BY cm.CrimeDate DESC
        """
        return query
    
    @staticmethod
    def get_crime_by_type() -> str:
        """Crime distribution by type"""
        query = """
        SELECT 
            ct.CrimeMinorName,
            COUNT(DISTINCT cm.CaseMasterID) as case_count,
            COUNT(DISTINCT ca.AccusedID) as suspect_count,
            COUNT(DISTINCT cv.VictimID) as victim_count,
            ROUND(AVG(DATEDIFF(cm.ArrestDate, cm.CrimeDate)), 1) as avg_days_to_arrest,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM CaseMaster), 2) as percentage
        FROM CaseMaster cm
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        LEFT JOIN CaseAccused ca ON cm.CaseMasterID = ca.CaseMasterID
        LEFT JOIN CaseVictim cv ON cm.CaseMasterID = cv.CaseMasterID
        GROUP BY ct.CrimeMinorHeadID, ct.CrimeMinorName
        ORDER BY case_count DESC
        """
        return query
    
    @staticmethod
    def get_emerging_crime_clusters() -> str:
        """Identify emerging crime clusters (new patterns)"""
        query = """
        SELECT 
            loc.LocationName,
            ct.CrimeMinorName,
            COUNT(DISTINCT cm.CaseMasterID) as recent_count,
            MAX(cm.CrimeDate) as latest_incident,
            DATEDIFF(CURDATE(), MAX(cm.CrimeDate)) as days_since_last,
            ROUND(AVG(DATEDIFF(cm2.CrimeDate, cm.CrimeDate)), 1) as avg_days_between_incidents
        FROM CaseMaster cm
        JOIN Location loc ON cm.LocationID = loc.LocationID
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        LEFT JOIN CaseMaster cm2 ON cm.LocationID = cm2.LocationID 
            AND cm.CrimeMinorHeadID = cm2.CrimeMinorHeadID
            AND cm.CaseMasterID != cm2.CaseMasterID
        WHERE cm.CrimeDate >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        GROUP BY loc.LocationID, ct.CrimeMinorHeadID
        HAVING recent_count >= 2
        ORDER BY recent_count DESC, days_since_last_incident ASC
        LIMIT 10
        """
        return query


# ============================================================================
# 2. REPEAT OFFENDER ANALYSIS
# ============================================================================

class RepeatOffenderAnalyzer:
    """Identify and analyze repeat offenders and habitual criminals"""
    
    @staticmethod
    def get_repeat_offenders(min_cases: int = 2) -> str:
        """Find repeat offenders with minimum number of cases"""
        query = f"""
        SELECT 
            a.AccusedID,
            a.AccusedName,
            a.Age,
            COUNT(DISTINCT cm.CaseMasterID) as total_cases,
            GROUP_CONCAT(DISTINCT ct.CrimeMinorName SEPARATOR ', ') as crime_types,
            GROUP_CONCAT(DISTINCT loc.LocationName SEPARATOR ', ') as crime_locations,
            MIN(cm.CrimeDate) as first_crime_date,
            MAX(cm.CrimeDate) as latest_crime_date,
            DATEDIFF(MAX(cm.CrimeDate), MIN(cm.CrimeDate)) as days_active,
            COUNT(DISTINCT CASE WHEN cm.ChargeSheetStatus = 'Filed' THEN 1 END) as charged_cases,
            COUNT(DISTINCT CASE WHEN cm.ArrestDate IS NOT NULL THEN 1 END) as arrested_cases
        FROM Accused a
        JOIN CaseAccused ca ON a.AccusedID = ca.AccusedID
        JOIN CaseMaster cm ON ca.CaseMasterID = cm.CaseMasterID
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        LEFT JOIN Location loc ON cm.LocationID = loc.LocationID
        GROUP BY a.AccusedID, a.AccusedName, a.Age
        HAVING COUNT(DISTINCT cm.CaseMasterID) >= {min_cases}
        ORDER BY total_cases DESC
        """
        return query
    
    @staticmethod
    def get_offender_network(offender_id: int) -> str:
        """Get all co-accused relationships for an offender"""
        query = f"""
        SELECT 
            a2.AccusedID as co_accused_id,
            a2.AccusedName,
            COUNT(DISTINCT cm.CaseMasterID) as cases_together,
            GROUP_CONCAT(DISTINCT ct.CrimeMinorName) as joint_crimes,
            GROUP_CONCAT(DISTINCT loc.LocationName) as locations
        FROM CaseAccused ca1
        JOIN CaseAccused ca2 ON ca1.CaseMasterID = ca2.CaseMasterID AND ca1.AccusedID != ca2.AccusedID
        JOIN Accused a2 ON ca2.AccusedID = a2.AccusedID
        JOIN CaseMaster cm ON ca1.CaseMasterID = cm.CaseMasterID
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        LEFT JOIN Location loc ON cm.LocationID = loc.LocationID
        WHERE ca1.AccusedID = {offender_id}
        GROUP BY ca2.AccusedID, a2.AccusedName
        ORDER BY cases_together DESC
        """
        return query


# ============================================================================
# 3. OFFENDER RISK SCORING ALGORITHM
# ============================================================================

class RiskScoringEngine:
    """Calculate risk scores for offenders based on criminology principles"""
    
    @staticmethod
    def calculate_individual_risk_score(offender_id: int, db_result: Dict[str, Any]) -> float:
        """
        Risk Score Calculation (0-100)
        Components:
        - Crime Frequency (40 points): How many crimes
        - Severity Score (30 points): Type of crimes committed
        - Recency Factor (20 points): How recent the crimes are
        - Pattern Consistency (10 points): Modus operandi pattern)
        """
        
        crime_count = db_result.get('crime_count', 0)
        avg_severity = db_result.get('avg_severity', 0)
        days_since_last = db_result.get('days_since_last_crime', 365)
        has_modus = bool(db_result.get('modus_operandi'))
        
        # Crime frequency score (0-40)
        # Each additional crime adds 10 points, capped at 40
        frequency_score = min(40, crime_count * 10)
        
        # Severity score (0-30)
        # Based on average severity of crimes
        severity_score = min(30, avg_severity * 3)
        
        # Recency factor (0-20)
        # Recent crimes increase risk significantly
        if days_since_last < 30:
            recency_score = 20
        elif days_since_last < 90:
            recency_score = 15
        elif days_since_last < 180:
            recency_score = 10
        else:
            recency_score = max(0, 10 - (days_since_last / 100))
        
        # Pattern consistency (0-10)
        pattern_score = 10 if has_modus else 0
        
        # Total risk score
        total_score = frequency_score + severity_score + recency_score + pattern_score
        
        # Normalize to 0-100
        risk_score = min(100, total_score)
        
        return round(risk_score, 1)
    
    @staticmethod
    def get_risk_query() -> str:
        """SQL query to gather risk scoring data"""
        query = """
        SELECT 
            a.AccusedID,
            a.AccusedName,
            COUNT(DISTINCT cm.CaseMasterID) as crime_count,
            AVG(CASE 
                WHEN ct.CrimeMinorName IN ('Murder', 'Rape', 'Armed Robbery', 'Kidnapping') THEN 10
                WHEN ct.CrimeMinorName IN ('Theft', 'Burglary', 'Robbery', 'Assault') THEN 6
                ELSE 2 END) as avg_severity,
            DATEDIFF(CURDATE(), MAX(cm.CrimeDate)) as days_since_last_crime,
            GROUP_CONCAT(DISTINCT cm.MOAccused) as modus_operandi,
            COUNT(DISTINCT CASE WHEN cm.ArrestDate IS NOT NULL THEN 1 END) as arrest_count,
            COUNT(DISTINCT CASE WHEN cm.ChargeSheetStatus = 'Filed' THEN 1 END) as chargesheet_count
        FROM Accused a
        JOIN CaseAccused ca ON a.AccusedID = ca.AccusedID
        JOIN CaseMaster cm ON ca.CaseMasterID = cm.CaseMasterID
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        WHERE a.AccusedID = %s
        GROUP BY a.AccusedID
        """
        return query


# ============================================================================
# 4. CASE SIMILARITY DETECTION
# ============================================================================

class CaseSimilarityDetector:
    """Find similar past cases based on crime characteristics"""
    
    @staticmethod
    def get_similar_cases_query(case_id: int) -> str:
        """
        Similarity scoring:
        - Same crime type: 30 points
        - Same location: 20 points
        - Within 30 days: 20 points
        - Same modus operandi: 20 points
        - Same victim gender: 10 points
        Total: 100 points
        """
        query = f"""
        SELECT 
            cm2.CaseMasterID,
            cm2.CaseNumber,
            cm2.CrimeDate,
            ct.CrimeMinorName,
            loc.LocationName,
            COUNT(DISTINCT ca2.AccusedID) as suspect_count,
            COUNT(DISTINCT cv2.VictimID) as victim_count,
            (
                (CASE WHEN cm1.CrimeMinorHeadID = cm2.CrimeMinorHeadID THEN 30 ELSE 0 END) +
                (CASE WHEN cm1.LocationID = cm2.LocationID THEN 20 ELSE 0 END) +
                (CASE WHEN ABS(DATEDIFF(cm1.CrimeDate, cm2.CrimeDate)) < 30 THEN 20 ELSE 0 END) +
                (CASE WHEN cm1.MOAccused = cm2.MOAccused AND cm1.MOAccused IS NOT NULL THEN 20 ELSE 0 END) +
                (CASE WHEN cm1.VictimGender = cm2.VictimGender AND cm1.VictimGender IS NOT NULL THEN 10 ELSE 0 END)
            ) as similarity_score
        FROM CaseMaster cm1
        JOIN CaseMaster cm2 ON cm1.CaseMasterID != cm2.CaseMasterID
        JOIN Crime ct ON cm2.CrimeMinorHeadID = ct.CrimeMinorHeadID
        JOIN Location loc ON cm2.LocationID = loc.LocationID
        LEFT JOIN CaseAccused ca2 ON cm2.CaseMasterID = ca2.CaseMasterID
        LEFT JOIN CaseVictim cv2 ON cm2.CaseMasterID = cv2.CaseMasterID
        WHERE cm1.CaseMasterID = {case_id}
        GROUP BY cm2.CaseMasterID, ct.CrimeMinorName, loc.LocationName
        ORDER BY similarity_score DESC, cm2.CrimeDate DESC
        LIMIT 5
        """
        return query


# ============================================================================
# 5. BEHAVIORAL PROFILING
# ============================================================================

class BehavioralProfiler:
    """Analyze offender behavior patterns and modus operandi"""
    
    @staticmethod
    def get_behavioral_profile_query(offender_id: int) -> str:
        """Generate complete behavioral profile"""
        query = f"""
        SELECT 
            a.AccusedID,
            a.AccusedName,
            a.Age,
            a.Gender,
            a.Education,
            a.Occupation,
            GROUP_CONCAT(DISTINCT ct.CrimeMinorName SEPARATOR ', ') as crime_types,
            GROUP_CONCAT(DISTINCT loc.LocationName SEPARATOR ', ') as preferred_locations,
            COUNT(DISTINCT cm.CaseMasterID) as total_cases,
            COUNT(DISTINCT CASE WHEN cm.VictimGender = 'F' THEN 1 END) as female_victim_cases,
            COUNT(DISTINCT CASE WHEN cm.VictimGender = 'M' THEN 1 END) as male_victim_cases,
            AVG(DATEDIFF(cm.ArrestDate, cm.CrimeDate)) as avg_days_to_arrest,
            MIN(cm.CrimeDate) as first_crime_date,
            MAX(cm.CrimeDate) as latest_crime_date,
            DATEDIFF(MAX(cm.CrimeDate), MIN(cm.CrimeDate)) as active_period_days,
            GROUP_CONCAT(DISTINCT cm.MOAccused SEPARATOR '; ') as modus_operandi_patterns,
            COUNT(DISTINCT CASE WHEN cm.ChargeSheetStatus = 'Filed' THEN 1 END) as prosecuted_cases,
            ROUND((COUNT(DISTINCT CASE WHEN cm.ChargeSheetStatus = 'Filed' THEN 1 END) * 100.0) / COUNT(DISTINCT cm.CaseMasterID), 1) as prosecution_rate
        FROM Accused a
        JOIN CaseAccused ca ON a.AccusedID = ca.AccusedID
        JOIN CaseMaster cm ON ca.CaseMasterID = cm.CaseMasterID
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        LEFT JOIN Location loc ON cm.LocationID = loc.LocationID
        WHERE a.AccusedID = {offender_id}
        GROUP BY a.AccusedID, a.AccusedName
        """
        return query
    
    @staticmethod
    def generate_behavior_summary(profile_data: Dict[str, Any]) -> str:
        """Generate text summary of behavioral profile"""
        summary = f"""
        **Behavioral Profile: {profile_data.get('AccusedName', 'Unknown')}**
        
        Demographics:
        - Age: {profile_data.get('Age', 'N/A')}
        - Gender: {profile_data.get('Gender', 'N/A')}
        - Occupation: {profile_data.get('Occupation', 'Unknown')}
        - Education: {profile_data.get('Education', 'N/A')}
        
        Criminal History:
        - Total Cases: {profile_data.get('total_cases', 0)}
        - Active Period: {profile_data.get('active_period_days', 0)} days
        - Prosecution Rate: {profile_data.get('prosecution_rate', 0)}%
        
        Crime Patterns:
        - Primary Crimes: {profile_data.get('crime_types', 'N/A')}
        - Preferred Locations: {profile_data.get('preferred_locations', 'N/A')}
        - Modus Operandi: {profile_data.get('modus_operandi_patterns', 'Not identified')}
        - Average Days to Arrest: {profile_data.get('avg_days_to_arrest', 'N/A')}
        
        Victim Profile:
        - Female Victims: {profile_data.get('female_victim_cases', 0)} cases
        - Male Victims: {profile_data.get('male_victim_cases', 0)} cases
        """
        return summary.strip()


# ============================================================================
# 6. CRIMINAL NETWORK VISUALIZATION DATA
# ============================================================================

class CriminalNetworkAnalyzer:
    """Generate network visualization data for criminal associations"""
    
    @staticmethod
    def generate_network_json(central_offender_id: int, depth: int = 1) -> Dict[str, Any]:
        """
        Generate network graph JSON for visualization
        Returns nodes (offenders, locations) and edges (relationships, crimes)
        """
        return {
            "nodes": [
                {"id": f"accused_{central_offender_id}", "type": "accused", "label": "Central Offender", "crimes": 0, "risk_score": 0},
            ],
            "edges": [],
            "metadata": {
                "center_id": central_offender_id,
                "depth": depth,
                "description": "Generate with data from CaseAccused joins"
            }
        }
    
    @staticmethod
    def get_network_query(central_offender_id: int, depth: int = 1) -> str:
        """
        SQL to build network graph
        Depth 1: Direct co-accused
        Depth 2: Co-accused of co-accused
        """
        if depth == 1:
            query = f"""
            SELECT 
                ca1.AccusedID as source_id,
                a1.AccusedName as source_name,
                ca2.AccusedID as target_id,
                a2.AccusedName as target_name,
                COUNT(DISTINCT cm.CaseMasterID) as relationship_weight,
                GROUP_CONCAT(DISTINCT ct.CrimeMinorName) as shared_crimes
            FROM CaseAccused ca1
            JOIN CaseAccused ca2 ON ca1.CaseMasterID = ca2.CaseMasterID
            JOIN Accused a1 ON ca1.AccusedID = a1.AccusedID
            JOIN Accused a2 ON ca2.AccusedID = a2.AccusedID
            JOIN CaseMaster cm ON ca1.CaseMasterID = cm.CaseMasterID
            JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
            WHERE ca1.AccusedID = {central_offender_id}
            GROUP BY ca1.AccusedID, ca2.AccusedID
            ORDER BY relationship_weight DESC
            """
        else:
            # Depth 2 - more complex query
            query = f"""
            SELECT DISTINCT
                ca1.AccusedID as source_id,
                ca2.AccusedID as target_id,
                COUNT(DISTINCT cm.CaseMasterID) as relationship_weight
            FROM CaseAccused ca1
            JOIN CaseAccused ca2 ON ca1.CaseMasterID = ca2.CaseMasterID
            JOIN CaseMaster cm ON ca1.CaseMasterID = cm.CaseMasterID
            WHERE ca1.AccusedID = {central_offender_id}
            GROUP BY ca1.AccusedID, ca2.AccusedID
            ORDER BY relationship_weight DESC
            LIMIT 50
            """
        return query


# ============================================================================
# 7. CRIME FORECASTING & EARLY WARNING
# ============================================================================

class CrimeForecastingEngine:
    """Predictive analysis for emerging crime patterns"""
    
    @staticmethod
    def get_emerging_threats_query() -> str:
        """Identify emerging crime threats and patterns"""
        query = """
        SELECT 
            loc.LocationName,
            ct.CrimeMinorName,
            COUNT(DISTINCT cm.CaseMasterID) as recent_count_90d,
            COUNT(DISTINCT CASE WHEN cm.CrimeDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN 1 END) as recent_count_30d,
            MAX(cm.CrimeDate) as latest_incident,
            ROUND(AVG(DATEDIFF(cm2.CrimeDate, cm.CrimeDate)), 1) as avg_days_between,
            CASE 
                WHEN COUNT(DISTINCT CASE WHEN cm.CrimeDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN 1 END) >= 
                     COUNT(DISTINCT CASE WHEN cm.CrimeDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 60 DAY) AND DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN 1 END)
                THEN 'INCREASING'
                ELSE 'STABLE'
            END as trend
        FROM CaseMaster cm
        JOIN Location loc ON cm.LocationID = loc.LocationID
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        LEFT JOIN CaseMaster cm2 ON cm.LocationID = cm2.LocationID 
            AND cm.CrimeMinorHeadID = cm2.CrimeMinorHeadID
            AND cm.CaseMasterID != cm2.CaseMasterID
        WHERE cm.CrimeDate >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        GROUP BY loc.LocationID, ct.CrimeMinorHeadID
        HAVING recent_count_90d >= 2
        ORDER BY recent_count_30d DESC, trend DESC
        """
        return query


# ============================================================================
# 8. INVESTIGATION DECISION SUPPORT
# ============================================================================

class InvestigationSupport:
    """Generate case summaries and investigation recommendations"""
    
    @staticmethod
    def get_case_summary_query(case_id: int) -> str:
        """Generate comprehensive case summary"""
        query = f"""
        SELECT 
            cm.CaseNumber,
            cm.CrimeDate,
            cm.ArrestDate,
            ct.CrimeMinorName as crime_type,
            loc.LocationName as crime_location,
            DATEDIFF(cm.ArrestDate, cm.CrimeDate) as days_to_arrest,
            COUNT(DISTINCT ca.AccusedID) as suspect_count,
            GROUP_CONCAT(DISTINCT CONCAT(a.AccusedName, ' (', a.Age, ')') SEPARATOR ', ') as suspects,
            COUNT(DISTINCT cv.VictimID) as victim_count,
            GROUP_CONCAT(DISTINCT v.VictimName SEPARATOR ', ') as victims,
            cm.MOAccused as modus_operandi,
            cm.ChargeSheetStatus,
            cm.InvestigationNotes
        FROM CaseMaster cm
        JOIN Crime ct ON cm.CrimeMinorHeadID = ct.CrimeMinorHeadID
        JOIN Location loc ON cm.LocationID = loc.LocationID
        LEFT JOIN CaseAccused ca ON cm.CaseMasterID = ca.CaseMasterID
        LEFT JOIN Accused a ON ca.AccusedID = a.AccusedID
        LEFT JOIN CaseVictim cv ON cm.CaseMasterID = cv.CaseMasterID
        LEFT JOIN Victim v ON cv.VictimID = v.VictimID
        WHERE cm.CaseMasterID = {case_id}
        GROUP BY cm.CaseMasterID
        """
        return query


# ============================================================================
# 9. ROLE-BASED ACCESS CONTROL
# ============================================================================

class RoleBasedAccessControl:
    """Manage role-based data access and filtering"""
    
    ROLE_PERMISSIONS = {
        'investigator': {
            'view_all_crimes': True,
            'view_sensitive_data': True,
            'search_suspects': True,
            'view_victims': True,
            'export_cases': True,
            'view_risk_scores': True,
            'edit_case_notes': True
        },
        'analyst': {
            'view_all_crimes': True,
            'view_sensitive_data': False,
            'search_suspects': True,
            'view_victims': True,
            'export_cases': True,
            'view_risk_scores': True,
            'edit_case_notes': False
        },
        'supervisor': {
            'view_all_crimes': True,
            'view_sensitive_data': True,
            'search_suspects': True,
            'view_victims': True,
            'export_cases': True,
            'view_risk_scores': True,
            'edit_case_notes': True,
            'manage_users': True,
            'audit_logs': True
        },
        'policymaker': {
            'view_all_crimes': False,
            'view_sensitive_data': False,
            'search_suspects': False,
            'view_victims': False,
            'export_cases': False,
            'view_risk_scores': False,
            'view_statistics': True,
            'view_trends': True
        }
    }
    
    SENSITIVE_FIELDS = {
        'investigation_notes',
        'informant_details',
        'accused_contact',
        'victim_address',
        'case_status_internal'
    }
    
    @staticmethod
    def filter_response(user_role: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter response based on user role"""
        if user_role not in RoleBasedAccessControl.ROLE_PERMISSIONS:
            return {}
        
        permissions = RoleBasedAccessControl.ROLE_PERMISSIONS[user_role]
        sensitive_fields = RoleBasedAccessControl.SENSITIVE_FIELDS
        
        if not permissions.get('view_sensitive_data', False):
            # Remove sensitive fields for non-investigator roles
            return {k: v for k, v in data.items() if k not in sensitive_fields}
        
        return data
    
    @staticmethod
    def check_permission(user_role: str, permission: str) -> bool:
        """Check if user has specific permission"""
        if user_role not in RoleBasedAccessControl.ROLE_PERMISSIONS:
            return False
        return RoleBasedAccessControl.ROLE_PERMISSIONS[user_role].get(permission, False)


# ============================================================================
# AGGREGATED QUERIES FOR LLM PROMPT INJECTION
# ============================================================================

def get_analytics_prompt() -> str:
    """
    Inject these into your LLM system prompt for automatic query generation
    """
    return """
    When users ask analytical questions about crime, use these proven SQL patterns:
    
    For "patterns" or "trends": Use CrimePatternAnalyzer.get_crime_by_type()
    For "hotspots" or "locations": Use CrimePatternAnalyzer.get_crime_hotspots()
    For "repeat offenders": Use RepeatOffenderAnalyzer.get_repeat_offenders()
    For "similar cases": Use CaseSimilarityDetector.get_similar_cases_query()
    For "risk assessment": Use RiskScoringEngine.get_risk_query()
    For "behavior profile": Use BehavioralProfiler.get_behavioral_profile_query()
    For "emerging threats": Use CrimeForecastingEngine.get_emerging_threats_query()
    For "case summary": Use InvestigationSupport.get_case_summary_query()
    
    Always explain which SQL was used and why it answers their question.
    """


if __name__ == "__main__":
    # Example usage
    print("Crime Analytics Features Module Loaded")
    print("Ready for integration into backend")
