from .models import Competition, Team 
import os

def global_site_context(request):
    """
    Globally making 'competition' and 'team' available in all templates safely.
    """
    # 1. SAFELY Extract slugs from the URL (only if resolver_match exists)
    if request.resolver_match is not None:
        kwargs = request.resolver_match.kwargs
        comp_slug = kwargs.get('competition_slug')
        team_slug = kwargs.get('team_slug')
    else:
        comp_slug = None
        team_slug = None

    # 2. Try to fetch from URL first (Priority: Specific page context)
    competition = Competition.objects.filter(slug=comp_slug).first() if comp_slug else None
    
    # Use 'competitions' (plural) to match your model's field name
    current_team = Team.objects.filter(slug=team_slug, competitions=competition).first() if team_slug else None

    # 3. Fallback: If no URL slugs found, use the 'is_current' database flag
    if not competition:
        competition = Competition.objects.filter(is_current_competition=True).first()
        
    if not current_team and competition:
        # Check if the competition object has 'team' or fallback to the reverse set
        if hasattr(competition, 'team'):
            current_team = competition.team
        elif hasattr(competition, 'team_set'):
            current_team = competition.team_set.first()

    # Return the dictionary to be injected into the template context
    return {
        'competition': competition,
        'team': current_team,
        'SITE_VERSION': '1.0',
        'SUPPORT_EMAIL': os.getenv('SUPPORT_EMAIL'),
        'WHATSAPP_NUMBER': os.getenv('WHATSAPP_NUMBER'),
        'PHONE_NUMBER': os.getenv('PHONE_NUMBER'), 
    }