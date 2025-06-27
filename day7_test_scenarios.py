"""
Day 7: Test Scenarios for Course Recommendation System

This module implements comprehensive test scenarios for the Day 7 requirements:
✅ Student with STEM major and interest in humanities
✅ Someone missing graduation credits
✅ Various edge cases and real-world scenarios

Author: Course Recommendation System
Date: Day 7 Implementation
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from day5_guardrails import Day5GuardedRAGPipeline, ValidatedRecommendationResponse
from src.data_manager import load_courses

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StudentProfile:
    """Student profile for testing scenarios"""
    name: str
    major: str
    year: str
    completed_courses: List[str]
    interests: List[str]
    career_goals: str
    constraints: List[str]
    graduation_requirements: Dict[str, int]
    missing_credits: Optional[Dict[str, int]] = None


@dataclass
class TestScenario:
    """Test scenario definition"""
    name: str
    description: str
    student_profile: StudentProfile
    query: str
    expected_outcomes: List[str]
    success_criteria: Dict[str, Any]


class Day7TestScenarios:
    """Day 7 comprehensive test scenarios"""
    
    def __init__(self):
        """Initialize test scenarios"""
        self.pipeline = Day5GuardedRAGPipeline(confidence_threshold=0.6)
        self.courses = load_courses()
        self.test_results = []
        
    def create_test_scenarios(self) -> List[TestScenario]:
        """Create comprehensive test scenarios"""
        
        # Scenario 1: STEM major with humanities interest
        stem_humanities_student = StudentProfile(
            name="Alex Chen",
            major="Computer Science",
            year="Junior",
            completed_courses=["CS101", "CS201", "MATH301"],
            interests=["machine learning", "philosophy", "ethics in technology", "writing"],
            career_goals="I want to work in AI ethics and responsible technology development",
            constraints=["prefer online courses", "need courses that count toward graduation"],
            graduation_requirements={
                "Core CS": 18,
                "CS Electives": 12,
                "Math/Science": 12,
                "Humanities": 6,
                "General Electives": 6
            },
            missing_credits={
                "CS Electives": 9,
                "Humanities": 6,
                "General Electives": 3
            }
        )
        
        # Scenario 2: Student missing graduation credits
        missing_credits_student = StudentProfile(
            name="Jordan Smith",
            major="Computer Science", 
            year="Senior",
            completed_courses=["CS101", "CS201", "CS301", "CS302"],
            interests=["software engineering", "databases", "algorithms"],
            career_goals="I need to graduate this semester and get a software engineering job",
            constraints=["must graduate this semester", "need exactly 12 credits", "avoid difficult courses"],
            graduation_requirements={
                "Core CS": 18,
                "CS Electives": 12,
                "Math/Science": 12,
                "Humanities": 6,
                "General Electives": 6
            },
            missing_credits={
                "Core CS": 4,  # Need CS306 (4 credits)
                "CS Electives": 6,  # Need 2 more electives
                "Math/Science": 0,
                "Humanities": 0,
                "General Electives": 2
            }
        )
        
        # Scenario 3: Career changer - non-traditional student
        career_changer_student = StudentProfile(
            name="Maria Rodriguez",
            major="Computer Science",
            year="Sophomore",
            completed_courses=["CS101"],
            interests=["web development", "user experience", "business applications"],
            career_goals="I'm changing careers from marketing to tech, want practical skills quickly",
            constraints=["prefer practical courses", "limited time", "need job-ready skills"],
            graduation_requirements={
                "Core CS": 18,
                "CS Electives": 12,
                "Math/Science": 12,
                "Humanities": 6,
                "General Electives": 6
            },
            missing_credits={
                "Core CS": 14,
                "CS Electives": 12,
                "Math/Science": 12,
                "Humanities": 6,
                "General Electives": 6
            }
        )
        
        # Scenario 4: High achiever seeking advanced courses
        high_achiever_student = StudentProfile(
            name="David Kim",
            major="Computer Science",
            year="Junior",
            completed_courses=["CS101", "CS201", "CS301", "CS304", "MATH301"],
            interests=["advanced algorithms", "research", "machine learning", "theoretical computer science"],
            career_goals="I want to pursue graduate school and research in AI/ML",
            constraints=["only interested in challenging courses", "want research opportunities"],
            graduation_requirements={
                "Core CS": 18,
                "CS Electives": 12,
                "Math/Science": 12,
                "Humanities": 6,
                "General Electives": 6
            },
            missing_credits={
                "Core CS": 4,  # Need CS306 or CS401
                "CS Electives": 3,  # Almost done
                "Humanities": 6,
                "General Electives": 3
            }
        )
        
        # Scenario 5: Student with learning preferences
        learning_preference_student = StudentProfile(
            name="Sarah Johnson",
            major="Computer Science",
            year="Sophomore", 
            completed_courses=["CS101", "CS201"],
            interests=["programming", "visual design", "user interfaces"],
            career_goals="I want to become a frontend developer with strong programming skills",
            constraints=["learn better with visual/practical approaches", "avoid heavy math", "prefer group projects"],
            graduation_requirements={
                "Core CS": 18,
                "CS Electives": 12,
                "Math/Science": 12,
                "Humanities": 6,
                "General Electives": 6
            },
            missing_credits={
                "Core CS": 10,
                "CS Electives": 12,
                "Math/Science": 9,  # Completed some
                "Humanities": 6,
                "General Electives": 6
            }
        )
        
        # Create test scenarios
        scenarios = [
            TestScenario(
                name="STEM Major with Humanities Interest",
                description="Computer Science student interested in AI ethics and humanities",
                student_profile=stem_humanities_student,
                query="I'm a CS major interested in AI ethics and responsible technology. I need courses that combine technical skills with humanities perspectives. I prefer online courses and need credits toward graduation.",
                expected_outcomes=[
                    "Should recommend CS courses with ethical components",
                    "Should suggest interdisciplinary approaches",
                    "Should consider graduation requirements",
                    "Should acknowledge humanities interest"
                ],
                success_criteria={
                    "min_recommendations": 2,
                    "min_confidence": 0.5,
                    "should_mention_ethics": True,
                    "should_consider_graduation": True
                }
            ),
            
            TestScenario(
                name="Missing Graduation Credits",
                description="Senior student needing specific credits to graduate this semester",
                student_profile=missing_credits_student,
                query="I'm a senior who needs to graduate this semester. I need exactly 12 credits including CS306 (Software Engineering) for core requirements, plus 6 credits of CS electives and 2 general electives. Please recommend courses that will help me graduate on time without being too difficult.",
                expected_outcomes=[
                    "Should prioritize required courses",
                    "Should suggest appropriate credit combinations",
                    "Should consider difficulty constraints",
                    "Should address graduation timeline"
                ],
                success_criteria={
                    "min_recommendations": 3,
                    "min_confidence": 0.6,
                    "should_include_required": True,
                    "should_consider_difficulty": True
                }
            ),
            
            TestScenario(
                name="Career Changer - Practical Focus",
                description="Non-traditional student changing careers, needs practical skills",
                student_profile=career_changer_student,
                query="I'm changing careers from marketing to tech. I need practical courses that will give me job-ready skills quickly. I'm especially interested in web development and want courses with real-world applications and projects.",
                expected_outcomes=[
                    "Should recommend practical courses",
                    "Should focus on web development",
                    "Should consider career change context",
                    "Should emphasize job readiness"
                ],
                success_criteria={
                    "min_recommendations": 3,
                    "min_confidence": 0.5,
                    "should_emphasize_practical": True,
                    "should_mention_web_dev": True
                }
            ),
            
            TestScenario(
                name="High Achiever - Advanced Courses",
                description="Advanced student seeking challenging courses and research opportunities",
                student_profile=high_achiever_student,
                query="I'm a high-achieving junior interested in graduate school and AI research. I want the most challenging and theoretical courses available. I've already completed machine learning and AI courses, so I need advanced algorithms, research opportunities, and courses that will prepare me for graduate-level work.",
                expected_outcomes=[
                    "Should recommend advanced courses",
                    "Should suggest research-oriented options",
                    "Should consider graduate preparation",
                    "Should acknowledge high achievement level"
                ],
                success_criteria={
                    "min_recommendations": 2,
                    "min_confidence": 0.6,
                    "should_recommend_advanced": True,
                    "should_mention_research": True
                }
            ),
            
            TestScenario(
                name="Learning Preferences - Visual/Practical",
                description="Student with specific learning preferences and career focus",
                student_profile=learning_preference_student,
                query="I learn best through visual and practical approaches rather than heavy theory. I want to become a frontend developer and am interested in courses with lots of hands-on projects, visual components, and group work. I prefer to avoid courses that are primarily mathematical or theoretical.",
                expected_outcomes=[
                    "Should recommend practical courses",
                    "Should suggest frontend-focused options",
                    "Should consider learning style",
                    "Should avoid heavy math courses"
                ],
                success_criteria={
                    "min_recommendations": 3,
                    "min_confidence": 0.5,
                    "should_emphasize_practical": True,
                    "should_avoid_heavy_math": True
                }
            )
        ]
        
        return scenarios
    
    def run_test_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """Run a single test scenario"""
        logger.info(f"🧪 Running scenario: {scenario.name}")
        
        try:
            # Process the query
            response = self.pipeline.process_query_with_validation(
                scenario.query, 
                top_k=5
            )
            
            # Analyze results
            analysis = self.analyze_scenario_results(scenario, response)
            
            # Log results
            logger.info(f"   📊 Generated {len(response.recommendations)} recommendations")
            logger.info(f"   📈 Confidence: {response.overall_confidence:.3f}")
            logger.info(f"   ✅ Success criteria met: {analysis['criteria_met']}/{analysis['total_criteria']}")
            
            return {
                "scenario": scenario.name,
                "response": response,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"   ❌ Scenario failed: {e}")
            return {
                "scenario": scenario.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_scenario_results(self, scenario: TestScenario, response: ValidatedRecommendationResponse) -> Dict[str, Any]:
        """Analyze test scenario results against success criteria"""
        criteria = scenario.success_criteria
        results = {}
        criteria_met = 0
        
        # Check minimum recommendations
        if "min_recommendations" in criteria:
            met = len(response.recommendations) >= criteria["min_recommendations"]
            results["min_recommendations"] = met
            if met:
                criteria_met += 1
        
        # Check minimum confidence
        if "min_confidence" in criteria:
            met = response.overall_confidence >= criteria["min_confidence"]
            results["min_confidence"] = met
            if met:
                criteria_met += 1
        
        # Check content-specific criteria
        response_text = " ".join([
            rec.justification + " " + rec.title 
            for rec in response.recommendations
        ]).lower()
        
        content_checks = [
            ("should_mention_ethics", ["ethic", "responsible", "social", "impact"]),
            ("should_consider_graduation", ["graduation", "requirement", "credit", "degree"]),
            ("should_include_required", ["software engineering", "cs306", "required", "core"]),
            ("should_consider_difficulty", ["difficulty", "manageable", "challenging", "level"]),
            ("should_emphasize_practical", ["practical", "hands-on", "project", "real-world"]),
            ("should_mention_web_dev", ["web", "frontend", "html", "css", "javascript"]),
            ("should_recommend_advanced", ["advanced", "algorithms", "cs401", "graduate"]),
            ("should_mention_research", ["research", "graduate", "thesis", "advanced"]),
            ("should_avoid_heavy_math", True)  # Special case - check if math courses are NOT recommended
        ]
        
        for check_name, keywords in content_checks:
            if check_name in criteria:
                if check_name == "should_avoid_heavy_math":
                    # Check if any math courses were recommended
                    math_courses = [rec for rec in response.recommendations if "MATH" in rec.course_id]
                    met = len(math_courses) == 0
                else:
                    # Check if any keywords appear in response
                    met = any(keyword in response_text for keyword in keywords)
                
                results[check_name] = met
                if met:
                    criteria_met += 1
        
        return {
            "results": results,
            "criteria_met": criteria_met,
            "total_criteria": len(criteria),
            "success_rate": criteria_met / len(criteria) if criteria else 0,
            "recommendations_count": len(response.recommendations),
            "confidence": response.overall_confidence,
            "validation_passed": response.validation_passed
        }
    
    def run_all_scenarios(self) -> List[Dict[str, Any]]:
        """Run all test scenarios"""
        print("🎓 Day 7: Comprehensive Test Scenarios")
        print("="*60)
        
        scenarios = self.create_test_scenarios()
        results = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\\n{i}️⃣ Test Scenario: {scenario.name}")
            print(f"   📝 Description: {scenario.description}")
            print(f"   👤 Student: {scenario.student_profile.name} ({scenario.student_profile.year} {scenario.student_profile.major})")
            print(f"   🎯 Query: {scenario.query[:100]}...")
            
            result = self.run_test_scenario(scenario)
            results.append(result)
            
            if "error" not in result:
                analysis = result["analysis"]
                print(f"   📊 Success Rate: {analysis['success_rate']:.1%}")
                print(f"   📈 Confidence: {analysis['confidence']:.3f}")
                print(f"   📚 Recommendations: {analysis['recommendations_count']}")
                
                # Show top recommendation
                if result["response"].recommendations:
                    top_rec = result["response"].recommendations[0]
                    print(f"   🎯 Top Recommendation: {top_rec.course_id} - {top_rec.title}")
                    print(f"      💡 Reasoning: {top_rec.justification[:100]}...")
            else:
                print(f"   ❌ Error: {result['error']}")
        
        # Summary
        print(f"\\n📊 Test Scenarios Summary")
        print("="*30)
        
        successful_scenarios = [r for r in results if "error" not in r]
        total_scenarios = len(results)
        success_rate = len(successful_scenarios) / total_scenarios if total_scenarios > 0 else 0
        
        print(f"✅ Successful Scenarios: {len(successful_scenarios)}/{total_scenarios} ({success_rate:.1%})")
        
        if successful_scenarios:
            avg_confidence = sum(r["analysis"]["confidence"] for r in successful_scenarios) / len(successful_scenarios)
            avg_success_rate = sum(r["analysis"]["success_rate"] for r in successful_scenarios) / len(successful_scenarios)
            total_recommendations = sum(r["analysis"]["recommendations_count"] for r in successful_scenarios)
            
            print(f"📈 Average Confidence: {avg_confidence:.3f}")
            print(f"🎯 Average Success Rate: {avg_success_rate:.1%}")
            print(f"📚 Total Recommendations: {total_recommendations}")
        
        # Save results
        self.save_test_results(results)
        
        return results
    
    def save_test_results(self, results: List[Dict[str, Any]]):
        """Save test results to file"""
        try:
            # Create simplified results for JSON serialization
            simplified_results = []
            for result in results:
                simplified = {
                    "scenario": result["scenario"],
                    "timestamp": result["timestamp"]
                }
                
                if "error" in result:
                    simplified["error"] = result["error"]
                else:
                    simplified["analysis"] = result["analysis"]
                    simplified["recommendations"] = [
                        {
                            "course_id": rec.course_id,
                            "title": rec.title,
                            "match_score": rec.match_score,
                            "justification": rec.justification
                        }
                        for rec in result["response"].recommendations
                    ]
                    simplified["overall_confidence"] = result["response"].overall_confidence
                    simplified["validation_passed"] = result["response"].validation_passed
                
                simplified_results.append(simplified)
            
            # Save to file
            results_file = Path("data/day7_test_results.json")
            results_file.parent.mkdir(exist_ok=True)
            
            with open(results_file, "w") as f:
                json.dump(simplified_results, f, indent=2)
            
            logger.info(f"💾 Test results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Error saving test results: {e}")


def main():
    """Main test runner"""
    test_runner = Day7TestScenarios()
    results = test_runner.run_all_scenarios()
    
    print("\\n🎉 Day 7 test scenarios completed!")
    print("📋 Results saved to data/day7_test_results.json")
    
    return len([r for r in results if "error" not in r]) == len(results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
