from .models import Competition, Team 
import os


def global_site_context(request):
    """
    Globally makeing 'competition' and 'team' available in all templates.
    """
    # 1. Extract slugs from the URL (if the current page has them)
    kwargs = request.resolver_match.kwargs
    comp_slug = kwargs.get('competition_slug')
    team_slug = kwargs.get('team_slug')

    # 2. Try to fetch from URL first (Priority: Specific page context)
    competition = Competition.objects.filter(slug=comp_slug).first() if comp_slug else None
    
    # FIX: Use 'competitions' (plural) to match your model's field name
    current_team = Team.objects.filter(slug=team_slug, competitions=competition).first() if team_slug else None

    # 3. Fallback: If no URL slugs found, use the 'is_current' database flag
    if not competition or not current_team:
        competition = Competition.objects.filter(is_current_competition=True).first()
        # Access the team via the competition model (ensure this matches your model)
        current_team = competition.team if competition and hasattr(competition, 'team') else None

    # Return the dictionary to be injected into the template context
    return {
        'competition': competition,
        'team': current_team,
        'SITE_VERSION': '1.0',
        'SUPPORT_EMAIL': os.getenv('SUPPORT_EMAIL'),
        'WHATSAPP_NUMBER': os.getenv('WHATSAPP_NUMBER'),
        'PHONE_NUMBER': os.getenv('PHONE_NUMBER'), 
    }