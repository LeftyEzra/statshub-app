from .models import Competition, Team 


def global_competition_and_team(request):
    """
    Provides the currently active competition and its associated team 
    to the template context globally.
    """
    competition = None
    current_team = None

    # Safely finding the current competition
    try:
        # Fetch the competition marked as current
        competition = Competition.objects.get(is_current_competition=True)
    except Competition.DoesNotExist:
        # If none exist, keep competition as None
        pass 
    except Competition.MultipleObjectsReturned:
        # If multiple are marked, take the first one found
        competition = Competition.objects.filter(is_current_competition=True).first()

    # 2. If a competition was found, fetch the linked team
    if competition and competition.team:
        # Access the Team object directly via the Foreign Key attribute
        current_team = competition.team
    
    # Return the dictionary with both objects for global use in templates
    return {
        'competition': competition, 
        'current_team': current_team,
        'SITE_VERSION': '1.0'  
    }


