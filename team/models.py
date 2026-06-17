from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class AutoSlugModel(models.Model):
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Looks for 'name' or 'title' automatically from whichever model uses it
            title_field = getattr(
                self, 'name', 
                getattr(self, 'title', 
                getattr(self, 'full_name', 
                getattr(self, 'player_name', None)))
            )
            #title_field = getattr(self, 'name', getattr(self, 'title', getattr(self, 'full_name', None)))
            if title_field:
                self.slug = slugify(title_field)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True # Tells Django not to build a physical table named AutoSlugModel



# Create your models here.

#The Venue Model is the master list of all physical locations where basketball games take place.
#It stores the static, unchanging details of every arena, gymnasium, or court the team might use.
class Venue(AutoSlugModel):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    capacity = models.IntegerField(blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        # Django's way of ensuring the model is pluralized correctly
        verbose_name_plural = "Venues"


# The Season Model defines the specific chronological timeframes for all organized play. 
# It separates historical data into clear, filterable segments.
class Season(AutoSlugModel):
    year = models.IntegerField(blank=True, null=True) 
    name = models.CharField(max_length=200)
    is_current_season = models.BooleanField(default=False)

    def __str__(self):
        return str(self.year)

    class Meta:
        # Django's way of ensuring the model is pluralized correctly
        verbose_name_plural = "Seasons"




# Types Of Competitions
COMPETITION_CHOICES = [
    ('LE', 'League'),
    ('TO', 'Tournament'),
    ('PO', 'Playoffs'),
    ('QU', 'Qualifiers'),
    ('EX', 'Exhibition'),
    ('FR', 'Friendly'), # If a player covers SF/PF
]

#The Competition Model
class Competition(AutoSlugModel):
    year = models.ForeignKey('Season', on_delete=models.CASCADE, null=True,blank=True)
    name = models.CharField(max_length=255)
    competition_type = models.CharField(max_length=2, choices=COMPETITION_CHOICES,default='LE' )
    team = models.ForeignKey('Team', on_delete=models.CASCADE,  null=True, blank=True,  related_name='team',)
    opponents = models.ManyToManyField('Opponent', blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_current_competition = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True,)

    def __str__(self):
        return self.name

    class Meta:
        # Django's way of ensuring the model is pluralized correctly
        verbose_name_plural = "Competitions"



class CompetitionSeason(AutoSlugModel):
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    champion = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, related_name='championships_won')

    class Meta:
        # Ensures that a specific competition/season combination can only exist once
        unique_together = ('season','competition')   



#Team Model
class Team(AutoSlugModel):
    name = models.CharField(max_length=100, unique=True)
    team_logo = models.ImageField(upload_to='uploads/Team_Logos/',blank=True, null=True)
    abbreviation = models.CharField(max_length=3, blank=True, null=True)
    city = models.CharField(max_length=100)
    competitions = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='team_competition',blank=True, null=True)
    established_year = models.IntegerField(blank=True, null=True)
    home_jersey_color = models.CharField(max_length=7)
    away_jersey_color = models.CharField(max_length=7, blank=True)
    facebook_link = models.URLField(verbose_name='Facebook URL', blank=True, null=True)
    twitter_link = models.URLField(verbose_name='X(Twitter) URL', blank=True, null=True)
    instagram_link = models.URLField(verbose_name='Instagram URL', blank=True, null=True)
    youtube_link = models.URLField(verbose_name='Youtube URL', blank=True, null=True)
    tiktok_link = models.URLField(verbose_name='TikTok', blank=True, null=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Team"  


# Staff Positions 
ROLE_CHOICES = (
    # 1. Executive / Front Office (Highest Level)
    ('Owner', 'Owner'),
    ('Team President', 'Team President'),
    ('Chief Executive Officer (CEO)', 'Chief Executive Officer (CEO)'),
    ('Chief Operating Officer (COO)', 'Chief Operating Officer (COO)'),
    ('General Manager',  'General Manager (GM)'),
    ('Sporting Director',  'Sporting Director'),
    ('Director Of Communication & Media',  'Director Of Communication & Media'),
  
    
    # 2. Coaching Staff (Tactics & Training)
    ('Head Coach',  'Head Coach'),
    ('Assistant Coach',  'Assistant Coach'),
    ('Scout',  'Scout'),
    ('Sports Technology & Analytics',  'Spoert Technology & Analytics'),
    
    # 3. Performance & Medical (Player Health & Development)
    ('Strength and Conditioning Coach', 'Strength and Conditioning Coach'),
    ('Athletic Trainer',  'Athletic Trainer'),
    ('Physiotherapist',  'Physiotherapist'),
    ('Dietitian/Nutritionist',  'Dietitian/Nutritionist'),
    ('Sports Psychologist',  'Sports Psychologist'),
    ('Equipment Manager', 'Equipment Manager'),
    
    # 4. Team Operations & Administration (Day-to-day logistics)
    ('Team Secretar',  'Team Secretary'),
    ('Team Administrator',  'Team Administrator'),
    ('Player Personnel Assistant',  'Player Personnel Assistant'),
)
#Team Staff Model
class TeamStaff(AutoSlugModel):
    full_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, related_name='team_staff', on_delete=models.CASCADE,blank=True, null=True)
    role = models.CharField( max_length=100,choices=ROLE_CHOICES,default='OWN')
    staff_image = models.ImageField(upload_to='uploads/Team_Staff_Photos/',blank=True, null=True)
   

    def __str__(self):
        return f"{self.get_role_display()}: {self.full_name}"

    class Meta:
        verbose_name_plural = "Team Staff"
        ordering = ['full_name']
        


#Opponent Model
class Opponent(AutoSlugModel):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=3, blank=True, null=True)
    city = models.CharField(max_length=100, default="City" )
    logo = models.ImageField(upload_to='uploads/Opponent_Photos/',blank=True, null=True)
    competitions = models.ForeignKey('Competition', on_delete=models.CASCADE, null=True,blank=True)
    
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Opponents"  




# Standard positions where a block might appear
BLOCK_POSITION_CHOICES = [
    ('TOP', 'Top Header/Announcement Bar'),
    ('SIDE', 'Sidebar/Rail'),
    ('MAIN', 'Main Body Section'),
    ('FOOT', 'Footer'),
    ('MISC', 'Miscellaneous/Special'),
]

# Defines the type of content this block contains
CONTENT_TYPE_CHOICES = [
    ('TEXT', 'Plain Text (Markdown/Basic)'),
    ('RICH', 'Rich Text (HTML Allowed)'),
    ('IMG_TEXT', 'Image with Text'), # Use this type for your text-image-text needs
    ('IMAGE', 'Image Only'),
]

class ContentBlock(models.Model):
    team = models.ForeignKey('Team', related_name='content_blocks', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=50, unique=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    content_top = models.TextField(blank=True, null=True,) 
    image = models.ImageField(upload_to='uploads/Contents_Photos/',blank=True, null=True)
    content_bottom = models.TextField(blank=True,  null=True,  ) 
    content_type = models.CharField(max_length=10,  choices=CONTENT_TYPE_CHOICES,  default='TEXT', )
    position = models.CharField(max_length=5, choices=BLOCK_POSITION_CHOICES, default='MISC')# Where the block is intended to be displayed
    is_active = models.BooleanField(default=True, )# Control when it appears
    
    def __str__(self):
        return f"Content Block: {self.title or self.slug}"
        
    class Meta:
        verbose_name_plural = "Content Blocks"
        ordering = ['slug'] # Good practice to add a default ordering



# --- Position Choices ---
PLAYER_POSITION_CHOICES = [
    ('SP', 'Select Position'),
    ('PG', 'Point Guard'),
    ('SG', 'Shooting Guard'),
    ('SF', 'Small Forward'),
    ('PF', 'Power Forward'),
    ('C', 'Center'),
    ('F', 'Forward'), # If a player covers SF/PF
    ('G', 'Guard'),   # If a player covers PG/SG
]
# Players Model
class Player(AutoSlugModel):
    team = models.ForeignKey('Team', related_name='players', on_delete=models.CASCADE,  null=True, blank=True)
    opponent = models.ForeignKey('Opponent', related_name='opponent_player', on_delete=models.SET_NULL, null=True, blank=True)
    player_name = models.CharField(max_length=100)
    jersey_number = models.PositiveIntegerField()
    position = models.CharField(max_length=2, choices=PLAYER_POSITION_CHOICES,default='SP', null=True, blank=True )
    date_of_birth = models.DateField(blank=True, null=True)
    height_cm = models.PositiveIntegerField(blank=True, null=True,)
    weight_kg = models.PositiveIntegerField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True)
    player_image = models.ImageField(upload_to='uploads/Players_Photos/',blank=True, null=True)
    biography = models.TextField(blank=True,)
    
    experience = models.PositiveIntegerField(blank=True, null=True,)
    draft_info = models.CharField(max_length=50, blank=True, null=True, default='2025: Rd 1, Pk 1 (PYT)')
    active_status = models.BooleanField(default=True,)
    is_starter = models.BooleanField(default=True,)
    facebook_link = models.URLField(verbose_name='Facebook URL', blank=True, null=True)
    twitter_link = models.URLField(verbose_name='X(Twitter) URL', blank=True, null=True)
    instagram_link = models.URLField(verbose_name='Instagram URL', blank=True, null=True)
    youtube_link = models.URLField(verbose_name='Youtube URL', blank=True, null=True)
    tiktok_link = models.URLField(verbose_name='TikTok', blank=True, null=True)
  
    def __str__(self):
        return self.player_name
        
    class Meta:
    
        verbose_name_plural = "Players"
        

# PlayerStatLine Model
class PlayerStatLine(models.Model):
    player_name = models.ForeignKey('Player', on_delete=models.CASCADE, blank=True, null=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, blank=True, null=True)
    opponent = models.ForeignKey('Opponent', on_delete=models.CASCADE, related_name='opponents', blank=True, null=True)
    game_schedule = models.ForeignKey('Game', on_delete=models.SET_NULL, related_name='game_stats', null=True, default=1)
    minutes = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    starter = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)
    field_goal_attempts = models.PositiveIntegerField(default=0)
    field_goal_made = models.PositiveIntegerField(default=0)
    
    point_3_attempts = models.PositiveIntegerField(default=0)
    point_3_made = models.PositiveIntegerField(default=0)
    
    point_2_attempts = models.PositiveIntegerField(default=0)
    point_2_made = models.PositiveIntegerField(default=0)
    
    ft_attempts = models.PositiveIntegerField(default=0)
    ft_made = models.PositiveIntegerField(default=0)
    
    offensive_rebs = models.PositiveIntegerField(default=0)
    defensive_rebs = models.PositiveIntegerField(default=0)
    
    blocks = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    steals = models.PositiveIntegerField(default=0)
    turnovers = models.PositiveIntegerField(default=0)
    personal_fouls = models.PositiveIntegerField(default=0)
   

    def __str__(self):
        return f"{self.player_name} - {self.game_schedule}"

    class Meta:
        verbose_name_plural = "Game Stats"





# Player cAREER RECORD  Model 
class CareerRecords(models.Model):
  
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='career_records',help_text="The player associated with career records.") 
    points_rec = models.TextField(blank=True,)
    rebounds_rec = models.TextField(blank=True,)
    assists_rec = models.TextField(blank=True,)
    blocks_rec = models.TextField(blank=True,)
    steals_rec = models.TextField(blank=True,)
    efficiency_rec = models.TextField(blank=True,)
    career_awards = models.CharField(max_length=100, default='', blank=True, null=True,)
    award_year = models.CharField(max_length=4, default='2026', blank=True, null=True,)
    
    
    def __str__(self):
        return f"{self.player.player_name}"
        
    class Meta:
        verbose_name_plural = "Players Career Records"
      




# Game models

class Game(AutoSlugModel):

    GAME_TYPES = (
        ('regular', 'Regular Season'),
        ('playoff', 'Playoffs'),
        ('preseason', 'Pre-Season'),
        ('tournament', 'Tournament'),
        ('international', 'International'),
    )

    WIN_LOSS_CHOICES = [('Win', 'W'), ('Loss', 'L')]
    INDICATOR_CHOICES = [('vs', 'Home'), ('@', 'Away')]
    
    competition = models.ForeignKey(Competition, related_name='games', on_delete=models.CASCADE, blank=True, null=True)
    game_type = models.CharField(max_length=20, choices=GAME_TYPES, default='regular')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default="00:00:00")    
    team = models.ForeignKey(Team, related_name='games', on_delete=models.CASCADE)
    indicator = models.CharField(max_length=4, default='vs', choices=INDICATOR_CHOICES, null=True)
    opponent = models.ForeignKey(Opponent, related_name='games_against', on_delete=models.CASCADE)
    team_scores = models.PositiveIntegerField(blank=True, null=True, default=0)
    opponent_scores = models.PositiveIntegerField(blank=True, null=True, default=0)
    team_win_loss = models.CharField(max_length=4, choices=WIN_LOSS_CHOICES, blank=True, null=True, verbose_name='Team Win/Loss')
    game_venue = models.ForeignKey(Venue, related_name='games', on_delete=models.CASCADE, blank=True, null=True)

    # SEPARATE SLUG FUNCTION LOGIC FROM THE CUSTOM CLASS
    def save(self, *args, **kwargs):
        if not self.slug: # Check if a slug doesn't exist yet
            # Piecing together the custom match text structure
            match_identity = f"{self.team.name} {self.indicator} {self.opponent.name} {self.date}"
            # slugify turns "Python vs JavaScript 2026-06-09" into "python-vs-javascript-2026-06-09"
            self.slug = slugify(match_identity)
            
        # Call the actual save method to commit changes to the database
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team.name} {self.indicator} {self.opponent.name} ({self.date})"        




# Inheriting from AutoSlugModel automatically gives this model a 'slug' field background column
class Standing(AutoSlugModel):
    GAME_TYPES = (
        ('Regular', 'Regular Season'),
        ('Playoff', 'Playoffs'),
        ('Preseason', 'Pre-Season'),
        ('Tournament', 'Tournament'),
        ('International', 'International'),
    )
   
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE, related_name='standings', blank=True, null=True)
    team = models.OneToOneField('Team', on_delete=models.CASCADE, null=True, blank=True, related_name='standing_stats')
    opponent = models.OneToOneField('Opponent', on_delete=models.CASCADE, null=True, blank=True, related_name='standing_stats')
    game_type = models.CharField(max_length=13, choices=GAME_TYPES, blank=True, null=True, default='Regular')

    # TABLE DATA (EDITABLE)
    w = models.PositiveIntegerField(default=0, verbose_name="W")
    l = models.PositiveIntegerField(default=0, verbose_name="L")
    
    home_record = models.CharField(max_length=20, default="0-0", verbose_name="HOME")
    away_record = models.CharField(max_length=20, default="0-0", verbose_name="AWAY")
    
    # Averages (Calculated as decimals for sorting accuracy)
    ppg = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, verbose_name="PPG")
    opp_ppg = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, verbose_name="OPP PPG")
    
    # Visual Indicators
    strk = models.CharField(max_length=10, default="W1", verbose_name="STRK")
    last_5 = models.CharField(max_length=10, default="0-0", verbose_name="L5")

    # Custom function to dynamically piece together a beautiful slug
    def save(self, *args, **kwargs):
        if not self.slug:
            # Check whether this standing row belongs to a home team or an opponent team
            if self.team:
                standing_identity = f"{self.team.name} {self.game_type}"
            elif self.opponent:
                standing_identity = f"{self.opponent.name} {self.game_type}"
            else:
                standing_identity = f"standing {self.id}"
                
            # slugify converts "Rivers Hoopers Regular" into "rivers-hoopers-regular"
            self.slug = slugify(standing_identity)
            
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.team.name if self.team else (self.opponent.name if self.opponent else "Unknown")
        return f"Standing for {name} ({self.game_type})"




# Quarterly Scores Model
class QuarterlyScores(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='quarterly_scores', default=1)
    team_quarter_1 = models.PositiveIntegerField(default=0)
    team_quarter_2 = models.PositiveIntegerField(default=0)
    team_quarter_3 = models.PositiveIntegerField(default=0)
    team_quarter_4 = models.PositiveIntegerField(default=0)
    opponent_quarter_1 = models.PositiveIntegerField(default=0)
    opponent_quarter_2 = models.PositiveIntegerField(default=0)
    opponent_quarter_3 = models.PositiveIntegerField(default=0)
    opponent_quarter_4 = models.PositiveIntegerField(default=0)
   


    def __str__(self):
        return f'{self.game}'


        #f"{self.team.name} vs {self.opponent} ({self.date})"


    class Meta:
        verbose_name_plural = 'Quarterly Scores'



# Action Photos Model
class GalleryImages(models.Model):
    title = models.CharField(max_length=20, default='', blank=True, null=True)
    images = models.ImageField(upload_to='uploads/Games_Image_Gallery/',blank=True, null=True)  # This will automatically create a folder in the project directory.
    team = models.ForeignKey(Team, related_name='team_pictures', on_delete=models.CASCADE, blank=True, null=True)
    player_pictures = models.ForeignKey(Player, related_name='player_pictures', on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = 'Image Gallery'

# Action Photos Model
class ShotCharts(models.Model):
    chart_title = models.CharField(max_length=20, default='', blank=True, null=True)
    chart_images = models.ImageField(upload_to='uploads/Shot_Chart_Gallery/',blank=True, null=True)  # This will automatically create a folder in the project directory.
    team = models.ForeignKey(Team, related_name='team_charts', on_delete=models.CASCADE, blank=True, null=True)
    player = models.ForeignKey(Player, related_name='player_chart', on_delete=models.CASCADE, blank=True, null=True)
    chart_texts = models.TextField(max_length=20000, default='', blank=True, null=True)
    
    

    def __str__(self):
        return self.chart_title

    class Meta:
        verbose_name_plural = 'Shot Charts'        





class TeamNews(models.Model):
    NEWS_TYPES = (
         
        ('Team', 'Team News'),
        ('Hot', 'Hot News'),
        ('Spotlight', 'Spotlight News'),
        ('League', 'League News'),
        ('Base', 'Base'),
    )
    category = models.CharField(max_length=15, choices=NEWS_TYPES, blank=True, null=True, default='Select News')
    published_date = models.DateTimeField(auto_now_add=True)
    
    image = models.ImageField(upload_to='uploads/News_Images/',blank=True, null=True)
    heading = models.CharField(max_length=80, blank=True)
    intro = models.TextField(blank=False, null=True)
    content = models.TextField()
    competition = models.ForeignKey('Competition', related_name='competition_news', on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return self.category

    class Meta:
        # Django's way of ensuring the model is pluralized correctly
        verbose_name_plural = "Team News"


# Sponsors model
class Awards(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True) 
    image = models.ImageField(upload_to='uploads/Awards/',blank=True, null=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Awards'


# Sponsors model
class Sponsor(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True) 
    logo = models.ImageField(upload_to='uploads/Sponsors_Photo/',blank=True, null=True)
    website = models.URLField()
    team_sponsors = models.ForeignKey('Competition', related_name='sponsors_for_this_competition', on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Sponsors'



# Contact Model
class Contact(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField("Email Address")
    mobile = models.CharField(max_length=15)
    
    message = models.TextField(blank=False, null=True)
    date_submitted =  models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.full_name

    class Meta:
        # Django's way of ensuring the model is pluralized correctly
        verbose_name_plural = "Contact"  

# Subscriber Model
class NewsletterSubscriber(models.Model):
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, default='08123456789')
    date_subscribed = models.DateTimeField(default=timezone.now)
    # This must be defined for the save() method to work:
    slug = models.SlugField(unique=True, blank=True, max_length=100) 

    def save(self, *args, **kwargs):
        # This is the correct logic: uses the unique email
        if not self.slug:
            self.slug = slugify(self.email) 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = 'Newsletter Suscriber'          