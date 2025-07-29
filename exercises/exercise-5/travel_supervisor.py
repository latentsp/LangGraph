
from rich import print


def calculate_trip_cost(destination: str, days: int, people: int) -> str:
    """Calculate estimated travel costs for a trip."""
    daily_cost = 120  # Cost per person per day
    total_accommodation = daily_cost * days * people
    flight_cost = people * 800  # Flight cost per person
    total_cost = total_accommodation + flight_cost
    
    return (
        f"Cost breakdown for {destination} ({days} days, {people} people):\n"
        f"- Accommodation & meals: ${total_accommodation:,}\n"
        f"- Flights: ${flight_cost:,}\n"
        f"- Total estimated cost: ${total_cost:,}"
    )

def compare_costs(destination1: str, destination2: str, days: int) -> str:
    """Compare costs between two destinations."""
    cost1 = (120 * days) + 800
    cost2 = (120 * days) + 800
    
    # Add variation for expensive cities
    if "paris" in destination1.lower() or "london" in destination1.lower():
        cost1 += 200
    if "paris" in destination2.lower() or "london" in destination2.lower():
        cost2 += 200
        
    return (
        f"Cost comparison for {days} days:\n"
        f"- {destination1}: ${cost1:,}\n"
        f"- {destination2}: ${cost2:,}\n"
        f"- Difference: ${abs(cost1 - cost2):,}"
    )

def plan_trip_itinerary(city: str, days: int) -> str:
    """Create a detailed trip itinerary for a city."""
    # Mock itinerary data
    itineraries = {
        "paris": [
            "Day 1: Eiffel Tower, Seine River cruise",
            "Day 2: Louvre Museum, Notre-Dame area", 
            "Day 3: Montmartre, Sacré-Cœur",
            "Day 4: Versailles day trip",
            "Day 5: Champs-Élysées, Arc de Triomphe"
        ],
        "tokyo": [
            "Day 1: Shibuya, Harajuku districts",
            "Day 2: Senso-ji Temple, Asakusa",
            "Day 3: Imperial Palace, Ginza",
            "Day 4: Day trip to Mount Fuji",
            "Day 5: Tsukiji Market, Tokyo Tower"
        ],
        "rome": [
            "Day 1: Colosseum, Roman Forum",
            "Day 2: Vatican City, St. Peter's",
            "Day 3: Trevi Fountain, Spanish Steps",
            "Day 4: Tivoli Gardens day trip", 
            "Day 5: Trastevere neighborhood"
        ]
    }
    
    city_plans = itineraries.get(city.lower(), [
        f"Day 1: Explore {city} city center",
        f"Day 2: Visit {city} museums",
        f"Day 3: Local attractions in {city}",
        f"Day 4: Day trip from {city}",
        f"Day 5: Shopping and relaxation"
    ])
    
    # Return only the requested number of days
    selected_days = city_plans[:days]
    
    return (
        f"{days}-day itinerary for {city.title()}:\n" +
        "\n".join(selected_days)
    )

def suggest_activities(city: str, interest: str) -> str:
    """Suggest activities based on interests."""
    suggestions = {
        "food": f"Food experiences in {city}: Local markets, cooking classes, food tours, traditional restaurants",
        "culture": f"Cultural activities in {city}: Museums, historical sites, art galleries, local festivals", 
        "nature": f"Nature activities near {city}: Parks, gardens, hiking trails, scenic viewpoints",
        "shopping": f"Shopping in {city}: Local markets, boutiques, shopping districts, souvenir shops"
    }
    
    return suggestions.get(interest.lower(), f"General activities in {city}: Sightseeing, local experiences, guided tours")

#TODO: Create budget agent that has tools to calculate trip cost and compare costs


# TODO: Create planner agent that has tools to plan a trip itinerary and suggest activities

# TODO: Create supervisor workflow

# TODO: Compile and run

print(result) 