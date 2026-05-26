
GOAL_ANALYZER_TEST_CASES = [
    {
        "id": "g1",
        "request": "I want to lose 5kg in 3 months. I have 30 min per day, no gym access.",
        "expected_keywords": ["weight loss", "3 months", "30 min", "no gym"],
        "must_mention": ["goal", "constraint"],
    },
    {
        "id": "g2",
        "request": "Help me run a 5K. I'm a complete beginner, can train 4 days a week.",
        "expected_keywords": ["5K", "beginner", "4 days", "endurance"],
        "must_mention": ["goal", "fitness level"],
    },
    {
        "id": "g3",
        "request": "I want to build muscle. I'm intermediate, have a home gym, 1 hour per day, 5 days a week.",
        "expected_keywords": ["muscle", "intermediate", "home gym", "1 hour"],
        "must_mention": ["goal", "equipment"],
    },
]

WORKOUT_DESIGNER_TEST_CASES = [
    {
        "id": "w1",
        "request": "Weight loss plan, 30 min/day, no equipment",
        "must_have": ["Day 1", "Day 2", "rest"],
        "must_not_have": ["barbell", "deadlift"],
    },
    {
        "id": "w2",
        "request": "Muscle gain, home gym, 5 days/week",
        "must_have": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "must_not_have": [],
    },
]
