from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvaluationCase:
    key: str
    query: str
    category: str
    intent: dict
    expected: dict
    relevant_item_keys: tuple[str, ...] = ()
    relevance_labels: dict[str, int] = field(default_factory=dict)
    user_profile: str = "cold_start"


EVALUATION_CASES = (
    EvaluationCase(
        key="vegetarian_pizza_under_300",
        query="I want a vegetarian pizza under 300 UAH.",
        category="hard_constraints",
        intent={"max_price": 300, "is_vegetarian": True, "is_vegan": None, "keywords": ["pizza"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "max_price": 300, "is_vegetarian": True},
        relevant_item_keys=("margherita", "vegetarian_pizza"),
    ),
    EvaluationCase(
        key="vegan_food",
        query="Find me something vegan.",
        category="hard_constraints",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": True, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1, "is_vegan": True},
        relevant_item_keys=("vegan_bowl", "vegan_roll"),
    ),
    EvaluationCase(
        key="chicken_and_spicy",
        query="I want chicken and something spicy.",
        category="hard_constraints",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["chicken", "spicy"], "categories": [], "cuisines": []},
        expected={"min_results": 1},
        relevant_item_keys=("fire_chicken",),
    ),
    EvaluationCase(
        key="under_250",
        query="Give me something under 250 UAH.",
        category="hard_constraints",
        intent={"max_price": 250, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1, "max_price": 250},
        relevant_item_keys=("vegan_bowl", "margherita", "ramen", "garden_salad"),
    ),
    EvaluationCase(
        key="comforting",
        query="I want something comforting.",
        category="semantic",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["comforting"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "semantic_relevance": True},
        relevant_item_keys=("ramen", "cheese_pasta", "vegetarian_pizza"),
        relevance_labels={"ramen": 2, "cheese_pasta": 2, "vegetarian_pizza": 1},
    ),
    EvaluationCase(
        key="light_but_filling",
        query="Something light but filling.",
        category="semantic",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["light", "filling"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "semantic_relevance": True},
        relevant_item_keys=("vegan_bowl", "chicken_salad"),
        relevance_labels={"vegan_bowl": 2, "chicken_salad": 2, "garden_salad": 1},
    ),
    EvaluationCase(
        key="greasy",
        query="I want something greasy.",
        category="semantic",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["greasy"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "semantic_relevance": True},
        relevant_item_keys=("beef_burger", "fries"),
        relevance_labels={"beef_burger": 2, "fries": 2},
    ),
    EvaluationCase(
        key="bad_day",
        query="I had a bad day. Give me something good.",
        category="semantic",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["comforting"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "semantic_relevance": True},
        relevant_item_keys=("ramen", "cheese_pasta"),
        relevance_labels={"ramen": 2, "cheese_pasta": 2},
    ),
    EvaluationCase(
        key="fresh_healthy",
        query="I want something fresh and healthy.",
        category="semantic",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["fresh", "healthy"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "semantic_relevance": True},
        relevant_item_keys=("garden_salad", "vegan_bowl"),
        relevance_labels={"garden_salad": 2, "vegan_bowl": 2},
    ),
    EvaluationCase(
        key="indulgent",
        query="I want something indulgent.",
        category="semantic",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["indulgent"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "semantic_relevance": True},
        relevant_item_keys=("beef_burger", "cheese_pasta"),
        relevance_labels={"beef_burger": 2, "cheese_pasta": 2},
    ),
    EvaluationCase(
        key="cozy_tonight",
        query="I want a cozy meal for tonight.",
        category="semantic",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": ["cozy"], "categories": [], "cuisines": []},
        expected={"min_results": 1, "semantic_relevance": True},
        relevant_item_keys=("ramen", "cheese_pasta"),
        relevance_labels={"ramen": 2, "cheese_pasta": 2},
    ),
    EvaluationCase(
        key="discovery_unsure",
        query="I don't know what I want.",
        category="discovery",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1},
        relevant_item_keys=("ramen", "vegetarian_pizza", "sushi_set"),
    ),
    EvaluationCase(
        key="surprise_cold_start",
        query="Surprise me.",
        category="discovery",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1},
        relevant_item_keys=("ramen", "sushi_set", "vegetarian_pizza"),
    ),
    EvaluationCase(
        key="interesting",
        query="Give me something interesting.",
        category="discovery",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1},
        relevant_item_keys=("ramen", "vegan_roll", "fire_chicken"),
    ),
    EvaluationCase(
        key="usual_italian",
        query="What should I eat tonight?",
        category="personalization",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1, "personalized": True},
        relevant_item_keys=("margherita", "cheese_pasta", "beef_burger"),
        user_profile="italian_burger",
    ),
    EvaluationCase(
        key="usual_japanese",
        query="What should I eat tonight?",
        category="personalization",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1, "personalized": True},
        relevant_item_keys=("sushi_set", "ramen", "vegan_roll"),
        user_profile="japanese",
    ),
    EvaluationCase(
        key="usual_vegetarian",
        query="What should I eat tonight?",
        category="personalization",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1, "personalized": True},
        relevant_item_keys=("vegan_bowl", "vegetarian_pizza", "garden_salad"),
        user_profile="vegetarian",
    ),
    EvaluationCase(
        key="cold_start_fallback",
        query="What should I eat tonight?",
        category="personalization",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": None, "keywords": [], "categories": [], "cuisines": []},
        expected={"min_results": 1, "cold_start": True},
        relevant_item_keys=("ramen", "sushi_set", "vegetarian_pizza"),
    ),
    EvaluationCase(
        key="vegan_with_chicken",
        query="I want vegan food with chicken.",
        category="conflict",
        intent={"max_price": None, "is_vegetarian": None, "is_vegan": True, "keywords": ["chicken"], "categories": [], "cuisines": []},
        expected={"should_return_results": False},
    ),
    EvaluationCase(
        key="missing_restaurant",
        query="I want something under 100 UAH from a restaurant that doesn't exist.",
        category="conflict",
        intent={"max_price": 100, "is_vegetarian": None, "is_vegan": None, "keywords": ["restaurant-that-does-not-exist"], "categories": [], "cuisines": []},
        expected={"should_return_results": False},
    ),
    EvaluationCase(
        key="vegetarian_but_beef",
        query="I want something vegetarian but I really want beef.",
        category="conflict",
        intent={"max_price": None, "is_vegetarian": True, "is_vegan": None, "keywords": ["beef"], "categories": [], "cuisines": []},
        expected={"should_return_results": False},
    ),
)