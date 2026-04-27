"""
Pet Care Knowledge Base

Contains breed-specific care guidelines organized by pet type and care category.
Used by the RAG engine to provide accurate, context-aware pet care information.
"""

KNOWLEDGE_BASE = {
    "dog": {
        "feeding": "Dogs typically need 1-2 meals per day. Puppies (under 1 year) need 3-4 meals daily. Adult dogs: 1-2 meals. Senior dogs (7+ years): 1-2 meals. Portion sizes depend on breed size and activity level. Use high-quality dog food and provide fresh water at all times.",
        "exercise": "Dogs need 30 minutes to 2+ hours of daily exercise depending on breed. High-energy breeds (Border Collie, Husky) need 1-2 hours. Medium-energy breeds (Beagle, Cocker Spaniel) need 30-60 minutes. Low-energy breeds (Bulldog, Pug) need 20-30 minutes. Daily walks are essential for physical health and mental stimulation.",
        "grooming": "Brush your dog's coat 2-3 times per week depending on coat type. Long-haired breeds need daily brushing. Bathe your dog every 4-12 weeks. Trim nails every 4-6 weeks or when you hear them clicking. Clean ears weekly, especially for floppy-eared breeds. Brush teeth daily for optimal dental health.",
        "training": "Start training puppies at 8 weeks old. Spend 15-20 minutes on training sessions daily. Use positive reinforcement with treats and praise. Focus on basic commands (sit, stay, come). Socialize puppies with other dogs and people between 3-16 weeks for best results.",
        "health": "Visit the vet annually for checkups. Puppies and senior dogs (7+ years) should see a vet every 6 months. Keep vaccinations current. Watch for signs of illness: lethargy, loss of appetite, vomiting, diarrhea. Maintain healthy weight to prevent joint and heart problems."
    },
    "cat": {
        "feeding": "Adult cats need 1-2 meals per day (200-250 calories per meal). Kittens (8 weeks to 1 year) need 3-4 meals per day. Senior cats (11+ years) may benefit from 2-3 smaller meals. Always provide fresh water. Wet food (1-2 times daily) combined with dry food keeps cats hydrated and satisfied.",
        "exercise": "Indoor cats need 15-30 minutes of play per day spread throughout the day. Use interactive toys like feather wands or laser pointers. Climbing trees and vertical spaces encourage natural behavior. Outdoor or catio time (if safe) provides enrichment. Bored cats become obese and develop behavioral issues.",
        "grooming": "Brush long-haired cats 2-3 times per week to prevent matting. Short-haired cats benefit from weekly brushing. Trim nails every 2-4 weeks. Clean ears monthly, especially if they go outdoors. Brush teeth daily (or 3-4 times weekly minimum). Provide a scratching post to maintain claw health.",
        "litter": "Provide 1 litter box per cat plus 1 extra (e.g., 3 cats = 4 boxes). Scoop litter daily. Change litter weekly (more often in warm climates). Place boxes away from food and water. Consider multiple locations, especially in multi-story homes.",
        "health": "Annual vet visits for healthy adult cats. Kittens and seniors (11+ years) need visits every 6 months. Watch for signs of illness: loss of appetite, lethargy, hiding, changes in litter box habits. Provide dental care and keep vaccinations current. Indoor cats typically live 12-18 years."
    },
    "goldfish": {
        "feeding": "Feed goldfish once or twice daily. Feed only what they can eat in 2-3 minutes. Overfeeding is the most common cause of goldfish death. Young goldfish (under 1 year) can be fed twice daily. Adult goldfish only need 1 feeding per day. Vary their diet with pellets, flakes, and occasional vegetables.",
        "tank_maintenance": "Goldfish produce a lot of waste. Do a 25% water change weekly to remove nitrates and ammonia. Check water temperature (65-72°F is ideal). Ensure proper filtration (rule of thumb: 20 gallons for first fish, 10 gallons for each additional). Test water chemistry weekly: pH 7-7.4, ammonia 0 ppm, nitrite 0 ppm.",
        "environment": "Goldfish need at least 20 gallons per fish (not 1 gallon as commonly believed). Provide plants, rocks, and hiding spots. Ensure good water circulation and aeration. Avoid sudden temperature changes. Keep the tank away from direct sunlight and drafts. Goldfish are social and can live 10-20 years with proper care.",
        "health": "Watch for signs of illness: loss of appetite, floating or sinking, torn fins, white spots, or gasping at surface. Quarantine sick fish immediately. Perform regular water changes to prevent disease. Maintain consistent temperature and water quality. Most health issues stem from poor water conditions or overfeeding.",
        "tank_setup": "Use a proper-sized aquarium (minimum 20 gallons). Install a filter rated for at least twice the tank volume (40+ gallons per hour for 20-gallon tank). Add an air pump for oxygenation. Use gravel substrate. Include decorations and plants (real or artificial). Condition tap water with dechlorinator before adding to tank."
    },
    "hamster": {
        "feeding": "Feed hamsters once daily in the evening (they're nocturnal). Provide 1-2 tablespoons of hamster pellets daily. Include fresh vegetables like carrots, cucumber, and broccoli 2-3 times per week. Offer fresh water daily in a water bottle. Avoid toxic foods: chocolate, onions, garlic, raw beans. Remove uneaten fresh food after 24 hours.",
        "cage_maintenance": "Spot-clean the cage daily (remove wet bedding, uneaten food). Do a full bedding change weekly. Use aspen shavings, paper-based bedding, or wood pellets (avoid cedar/pine - they're toxic). Maintain a clean water bottle and food dishes. Check for signs of illness or injury during cleaning.",
        "environment": "Provide a cage at least 450 square inches of continuous floor space (larger is better). Include a deep bedding layer (6+ inches) for burrowing. Add a solid-surface exercise wheel (8-12 inch diameter). Provide hideouts, tunnels, and chew toys. Maintain temperature between 65-75°F. Keep away from direct sunlight and drafts.",
        "health": "Syrian hamsters live 2-3 years. Dwarf hamsters live 1.5-3 years. Watch for sneezing, discharge from eyes/nose, or unusual behavior. Respiratory infections are common and serious. Take your hamster to an exotic vet if you notice health issues. Handle gently to avoid stress.",
        "behavior": "Hamsters are solitary and territorial. Most species should be housed alone (Syrian hamsters MUST be alone). Handle for 10-15 minutes daily to build trust, starting when young. Provide enrichment: tunnels, multi-level cage designs, foraging opportunities. Avoid sudden loud noises and keep them away from other pets."
    },
    "rabbit": {
        "feeding": "The foundation of rabbit diet is unlimited timothy hay (or other grass hay). Adult rabbits need 1/4 cup of pellets per 5 pounds of body weight daily. Provide fresh leafy greens daily (kale, romaine, parsley). Limit treats and vegetables high in sugar. Fresh water must be available at all times (water bottle or bowl). Gradually introduce new foods to avoid digestive upset.",
        "exercise": "Rabbits need 3+ hours of exercise daily outside their cage. Provide a safe, rabbit-proofed play area. Set up a large exercise pen (at least 4'x8'). Rabbits binky (jump for joy) when happy. Provide tunnels, boxes, and hiding spots. Without adequate exercise, rabbits develop behavioral and health problems.",
        "grooming": "Brush rabbits 2-3 times per week to prevent matting and reduce shedding. Long-haired breeds need daily brushing. Trim nails every 6-8 weeks. Clean ears monthly. Rabbits cannot be bathed (they groom themselves). Watch for overgrown teeth - they grow continuously and need proper hay diet to wear down.",
        "habitat": "Provide a cage/hutch at least 4 ft x 2 ft (larger is better). Include hiding spots, separate area for bathroom. Use aspen shavings or paper-based bedding (avoid cedar/pine). Provide multiple levels if space allows. Keep in cool, quiet environment (60-65°F). Avoid direct sunlight and drafts. Rabbits can be litter-trained.",
        "health": "Rabbits are prey animals and hide illness until critical. Take to exotic vet annually. Watch for: loss of appetite, soft stool, discharge, labored breathing. Dental disease is common - diet high in hay prevents this. Spay/neuter at 5-6 months to prevent cancer and behavioral issues. Rabbits live 8-12 years with proper care."
    },
    "bird": {
        "feeding": "Provide a varied diet: high-quality pellets as base, fresh fruits and vegetables daily. Most birds need about 1/4 to 1/2 cup of food daily. Avoid toxic foods: avocado, chocolate, caffeine, salt. Offer fresh water daily (change 1-2 times daily in warm weather). Some birds enjoy seeds as treats but seeds are high in fat.",
        "cage_maintenance": "Clean food and water dishes daily. Spot-clean the cage 3-4 times weekly (remove droppings, uneaten food). Full cage cleaning weekly or biweekly depending on cage size. Use bird-safe bedding or paper. Ensure good ventilation to avoid respiratory issues. Never use non-stick cookware (PTFE fumes are toxic to birds).",
        "environment": "Provide a large cage - bigger is always better for bird health. Include multiple perches of different thicknesses. Add toys for enrichment and mental stimulation (rotate them). Position cage away from kitchen (fumes), windows (drafts), and direct sunlight. Maintain temperature 65-75°F. Birds need 10-12 hours of sleep daily.",
        "health": "Annual vet checkups with an avian veterinarian. Watch for: ruffled feathers, wheezing, discharge from eyes/nose, loss of appetite, change in droppings. Birds hide illness well - see vet if you notice any behavioral change. Respiratory infections are common and serious. Provide proper nutrition and mental enrichment for long, healthy life.",
        "socialization": "Most birds are highly social and need daily interaction. Spend 1-2 hours daily with your bird (talking, training, play). Birds can live 20-80+ years depending on species and need constant companionship. Provide training and mental challenges. A lonely bird may develop behavioral problems like feather plucking or screaming."
    },
}


def get_knowledge_for_breed(breed: str) -> dict:
    """
    Retrieve all knowledge categories for a given breed.
    
    Args:
        breed: Pet breed/type (e.g., 'dog', 'cat', 'goldfish')
    
    Returns:
        Dictionary of care categories and guidelines. Empty dict if breed not found.
    """
    return KNOWLEDGE_BASE.get(breed.lower(), {})


def get_available_breeds() -> list:
    """Return list of all available pet types in the knowledge base."""
    return list(KNOWLEDGE_BASE.keys())


def get_care_category(breed: str, category: str) -> str:
    """
    Retrieve specific care guideline for a breed/category combination.
    
    Args:
        breed: Pet breed/type
        category: Care category (e.g., 'feeding', 'exercise', 'grooming')
    
    Returns:
        Care guideline text. Empty string if not found.
    """
    breed_data = get_knowledge_for_breed(breed)
    return breed_data.get(category.lower(), "")
