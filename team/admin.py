from django.contrib import admin
from .models import Venue
from .models import Season
from .models import Team
from .models import Game
from .models import Player
from .models import PlayerStatLine
from .models import QuarterlyScores
from .models import Competition
from .models import CompetitionSeason
from .models import Opponent
from .models import TeamStaff

from .models import GalleryImages, ShotCharts
from .models import TeamNews
from .models import Sponsor
from .models import CareerRecords
from .models import Standing
from .models import Awards
from .models import Contact
from .models import NewsletterSubscriber



# Register your models here.
class PlayerInline(admin.TabularInline):
    model = Player
    extra = 1

class TeamStaffInline(admin.TabularInline):
    model = TeamStaff
    extra = 1    

class CompetitionSeasonInline(admin.TabularInline):
    model = CompetitionSeason
    extra = 1 # Adds an extra empty form for additional team entries by default    

class NewsSectionInline(admin.TabularInline):
    model = TeamNews
    extra = 1 # Adds an extra empty form for additional team entries by default   

class GalleryImagesInline(admin.TabularInline):
    model = GalleryImages
    extra = 1

class CompetitionInline(admin.TabularInline):
    model = Competition
    extra = 1    

class QuarterlyScoresInline(admin.TabularInline):
    model = QuarterlyScores
    extra = 1 # Adds an extra empty form for additional team entries by default         


#Register Venue in the Admin area
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    
    list_display = ('name','city', 'state_province', 'country', 'capacity', 'established_date')
    search_fields = ('name', 'city', 'state_province',)
    ordering = ('name',)


#Register Season in the Admin area
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    
    list_display = ('year','name', 'is_current_season',)
    search_fields = ('year','name',)
    ordering = ('year',)
    inline = [CompetitionInline] 
    
#Register Competition in the Admin area
@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name','competition_type', 'is_current_competition', 'year','start_date', 'end_date', 'team',  'description','created_at' )
    search_fields = ('name', 'competition_type', 'year')
    list_filter = ('name', 'competition_type', 'year')
    ordering = ('name',)
    inlines = [CompetitionSeasonInline]  # Includes inline editing for teams in the competition admin panel
    

    def get_opponents(self, obj):
        if obj.opponents:
            return ", ".join([team.name for team in obj.opponents.all()])
        return "No teams"
    get_opponents.short_description = 'Opponents'




#Register Team in the Admin area
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    
    inlines = [PlayerInline,  TeamStaffInline, GalleryImagesInline]
    list_display = ('name', 'team_logo', 'abbreviation', 'home_jersey_color', 'away_jersey_color', 'get_players', 'get_staff',
                  'twitter_link', 'facebook_link', 'instagram_link','youtube_link', 'tiktok_link', 'competitions' )
    ordering = ('name',)
    search_fields = ('name', 'abbreviation',)

    def get_players(self, obj):
        return ", ".join([player.player_name for player in obj.team.players.all()])
    get_players.short_description = 'Players'

    def get_staff(self, obj):
        return ", ".join([staff.full_name  for staff in obj.team_staff.all()])
    get_staff.short_description = 'Team Staff'


#Register Team Staff in the Admin area
@admin.register(TeamStaff)
class TeamStaffAdmin(admin.ModelAdmin):
    
    list_display = ('full_name','role', 'staff_image', 'team', )
    ordering = ('full_name',)
    search_fields = ('role', 'full_name',)

     
#Register Opponent in the Admin area
@admin.register(Opponent)
class OpponentAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    list_display = ('name', 'abbreviation','logo', 'city',  'competitions' )
    search_fields = ('name', 'abbreviation',)

    def get_players(self, obj):
        return ", ".join([player.player_name for player in obj.opponent.players.all()])
    get_players.short_description = 'Players'

#Register Competition Champions in the Admin area
@admin.register(CompetitionSeason)
class CompetitionSeasonAdmin(admin.ModelAdmin):
    list_display = ('competition','season', 'champion')
    list_filter = ('competition','season', 'champion')
    search_fields = ('competition__name', 'season__name')
    raw_id_fields = ('competition','season', 'champion')

#Register Players in the Admin area    
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    inlines = [GalleryImagesInline]
    list_display = ('jersey_number', 'player_name', 'player_image', 'get_teams', 'get_opponents', 'position', 'date_of_birth', 
                    'height_cm', 'weight_kg',  'country',  'biography','career_awards', 'award_year', 'experience', 'draft_info', 'active_status', 'is_starter',
                    'twitter_link', 'facebook_link', 'instagram_link','youtube_link', 'tiktok_link',)
    ordering = ('jersey_number',)
    search_fields = ('player_name', 'position',)

    def get_teams(self, obj):
        return obj.team.name if obj.team else ""
    get_teams.short_description = 'Teams'

    def get_opponents(self, obj):
        return obj.opponent.name if obj.opponent else ""
    get_opponents.short_description = 'Opponents'

    def get_players_images(self, obj):
        return ", ".join([image.title for image in obj.player_pictures.all()])
     





#Register Players Stats in the Admin area
@admin.register(PlayerStatLine)
class PlayerStatLineAdmin(admin.ModelAdmin):
    list_display = ( 'game_schedule','player_name','team','opponent','minutes', 'starter','points','field_goal_attempts',
                    'field_goal_made','point_3_attempts','point_3_made',
                    'point_2_attempts','point_2_made','ft_attempts','ft_made',
                    'offensive_rebs','defensive_rebs','blocks', 'assists',
                    'steals','turnovers','personal_fouls',
                    )
    #list_filter = ('event_date', 'venue')
    ordering = ('game_schedule', )
    search_fields = ('player_name','jersey_numbers','team')
    search_help_text = ('player_name',)


#Register Games  in the Admin area
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [QuarterlyScoresInline]
    list_display = ('date','time','competition','game_type', 'team',
                    'indicator', 'opponent', 'team_scores' ,
                     'opponent_scores', 'team_win_loss', 'game_venue')
    ordering = ("-date", 'competition',)
    search_fields = ('date', 'competition', 'game_type')
    search_help_text = ('team', 'game_type')

#Register Quarter Scores in the Admin area
@admin.register(QuarterlyScores)
class QuarterlyScoresAdmin(admin.ModelAdmin):
    list_display = ('game', 'team_quarter_1', 'team_quarter_2', 'team_quarter_3', 'team_quarter_4',
                    'opponent_quarter_1','opponent_quarter_2','opponent_quarter_3','opponent_quarter_4', )   
    ordering = ("game",)

# Register Standing Admin
@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ('competition', 'game_type','team', 'opponent', 'w', 'l', 'home_record', 'away_record', 'ppg', 'opp_ppg', 'strk', 'last_5')
    ordering = ("w",)


#Register News in the Admin area
@admin.register(TeamNews)
class TeamNewsAdmin(admin.ModelAdmin):
    list_display = ('published_date', 'image', 'heading', 'intro', 'content','category', 'competition')
    list_filter = ('published_date',)
    search_fields = ('category',)
    ordering = ('published_date',)
    


#Register News in the Admin area
@admin.register(Awards)
class AwardsAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'image',)
    list_filter = ('date',)
    search_fields = ('name',)
    ordering = ('date',)


     
#Register Career Records in the Admin area    
@admin.register(CareerRecords)
class CareerRecordsAdmin(admin.ModelAdmin):
    list_display = ('player', 'points_rec', 'rebounds_rec', 'assists_rec', 'blocks_rec', 
                    'steals_rec', 'efficiency_rec')
                    


#Register Action Photos in the Admin area
@admin.register(GalleryImages)
class GalleryImagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'images', 'team', 'player_pictures')


#Register Action Photos in the Admin area
@admin.register(ShotCharts)
class ShotChartAdmin(admin.ModelAdmin):
    list_display = ('chart_title', 'chart_images', 'team', 'player', 'chart_texts')



#Register the Sponsors of the team in the Admin area
@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo', 'website', 'team_sponsors')




# Contact Admin
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    fields = ( 'full_name', 'email', 'mobile',  'message', 'date_submitted')
    list_display = ( 'full_name', 'date_submitted')
    list_filter = ( 'full_name', 'date_submitted')
    ordering = ('full_name', 'date_submitted')



# Gallery Admin
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    fields = ( 'email', 'date_subscribed', 'phone' )
    readonly_fields = (  'date_subscribed', )
    list_display = ( 'date_subscribed', 'email','slug',)
    ordering = ('date_subscribed', 'email',)     
