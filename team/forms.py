from django import forms
from .models import Season, Competition, Team, TeamStaff, Opponent, Player, Game, PlayerStatLine, QuarterlyScores, Standing
from .models import Venue, CompetitionSeason, CareerRecords, ContentBlock, GalleryImages, ShotCharts, TeamNews, Sponsor, CareerRecords, Awards
from .models import Contact, NewsletterSubscriber
from django.forms import inlineformset_factory








# Venue Form
class venueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = '__all__'

        labels = {
            'name': 'Name',
            'city': 'City',
            'state_province': 'State/Province',
            'country': 'Country',
            'capacity': 'Seating Capacity',
            'established_date': 'Established Date',

        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Seatinig Capacity'}),
            'established_date':  forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Established Date'}),

        }

# Season Form
class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = '__all__'

        labels = {
            'name': 'Name',
            'year': 'Year',
            'is_current_season': 'Current Season',

        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
            'is_current_season': forms.CheckboxInput(),
        }


# COMPETITION FORM
class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = '__all__'
        labels = {
            'year': 'Year',
            'name': 'Competition Name',
            'competition_type': 'Competition Type',
            'team': 'Team',
            'opponents': 'Opponents',
            'start_date': 'Starting Date',
            'end_date': 'Ending Date',
            'description': 'Description',
            'is_current_competition': 'Current Competition',
        }
        widgets = {
            # Fix: Use Select widget for ForeignKey
            'year': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Competition Name'}),
            'tcompetition_type': forms.Select(attrs={'class': 'form-control'}),
            # Keep SelectMultiple for ManyToManyField
            'team': forms.Select(attrs={'class': 'form-control'}),
            'opponents': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Brief description about this competition.'}),
            'is_current_competition': forms.CheckboxInput(),
        }

    # Explicitly set the queryset for organizers
    year = forms.ModelChoiceField(
        queryset=Season.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Season Year"
    )





class TeamForm(forms.ModelForm):

    home_color_ui = forms.CharField(max_length=7, required=True)
    away_color_ui = forms.CharField(max_length=7, required=False)

    home_jersey_color = forms.CharField(required=False)
    away_jersey_color = forms.CharField(required=False)

    class Meta:
        model = Team
        fields = [
            'name', 'team_logo', 'abbreviation',
            'city', 'established_year',
            
            # Model fields populated by clean() method:
            'home_jersey_color', 'away_jersey_color',
            
            'facebook_link', 'twitter_link',
            'instagram_link', 'youtube_link', 'tiktok_link', 
            'competitions', # The Foreign Key field

            # Custom UI fields included in Meta.fields for processing:
            'home_color_ui',
            'away_color_ui',
        ]

        labels = {
            'name': 'Team Name',
            'team_logo': 'Team Logo',
            'abbreviation': 'Team Abbreviation',
            'city': 'City',
            'established_year': 'Established Year',
            'home_jersey_color': 'Home Color', # Used for errors if clean fails
            'away_jersey_color': 'Away Color', # Used for errors if clean fails
            'facebook_link': 'Facebook Url',
            'twitter_link': 'X Url',
            'instagram_link': 'Instagram Url',
            'youtube_link': 'Youtube Url',
            'tiktok_link': 'TiTok Url',
            'competitions': 'Competition'
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Team Name'}),
            'team_logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'abbreviation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Team Abbreviation, eg:XYZ'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Established Year'}),
            
            # 2. Set custom fields to HiddenInput so they don't render a text box
            'home_color_ui': forms.HiddenInput(),
            'away_color_ui': forms.HiddenInput(),
            
            'facebook_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Facebook Handle'}),
            'twitter_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'X Handle'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Instagram Handle'}),
            'youtube_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Youtube Handle'}),
            'tiktok_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'TiTok Handle'}),
            'competitions': forms.Select(attrs={'class': 'form-control static-input', 'placeholder': 'Select'})
        }

    def clean(self):
        """
        Transfers the validated color hex data from the UI fields to the 
        actual model fields (home_jersey_color and away_jersey_color).
        """
        cleaned_data = super().clean()
        
        # Get data from the custom fields (must match definition above)
        home_hex = cleaned_data.get('home_color_ui')
        away_hex = cleaned_data.get('away_color_ui')
        
        # 3. Assign the validated hex codes to the actual model fields
        if home_hex:
            # This is the value that will be saved to the database
            cleaned_data['home_jersey_color'] = home_hex
        
        # Assign away color, ensuring an empty string if it's optional and not provided
        cleaned_data['away_jersey_color'] = away_hex or '' 
        
        return cleaned_data




class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'
        

# Opponents Form
class OpponentForm(forms.ModelForm):
    class Meta:
        model = Opponent
        fields = '__all__'
      

       



# Game Form
class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

# Standing Form
class StandingForm(forms.ModelForm):
    class Meta:
        model = Standing
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        team = cleaned_data.get("team")
        opponent = cleaned_data.get("opponent")

        if team and opponent:
            raise forms.ValidationError("Please select either a Main Team OR an Opponent, not both.")
        if not team and not opponent:
            raise forms.ValidationError("You must select at least one Team or Opponent.")
        return cleaned_data        


class QuarterlyScoresForm(forms.ModelForm):
    class Meta:
        model = QuarterlyScores
        # Excluded 'game' because the FormSet handles the link automatically
        # Excluded 'quarterly_scores_for' because we will set it in the view
        exclude = ['game',]
        widgets = {
            'team_quarter_1': forms.NumberInput(attrs={'class': 'score-input'}),
            'team_quarter_2': forms.NumberInput(attrs={'class': 'score-input'}),
            'team_quarter_3': forms.NumberInput(attrs={'class': 'score-input'}),
            'team_quarter_4': forms.NumberInput(attrs={'class': 'score-input'}),
            'opponent_quarter_1': forms.NumberInput(attrs={'class': 'score-input'}),
            'opponent_quarter_2': forms.NumberInput(attrs={'class': 'score-input'}),
            'opponent_quarter_3': forms.NumberInput(attrs={'class': 'score-input'}),
            'opponent_quarter_4': forms.NumberInput(attrs={'class': 'score-input'}),
        }


     



# Players Social Media Accounts
class CareerRecordsForm(forms.ModelForm):
    class Meta:
        model = CareerRecords
        fields = '__all__'

   

        
# Gallery Photos
class GalleryImagesForm(forms.ModelForm):
    class Meta:
        model = GalleryImages
        fields = '__all__'
      
# Gallery Photos
class ShotChartForm(forms.ModelForm):
    class Meta:
        model = ShotCharts
        fields = '__all__'

# News Article
class TeamNewsForm(forms.ModelForm):
    class Meta:
        model = TeamNews
        fields = '__all__'
        

# News Article
class AwardsForm(forms.ModelForm):
    class Meta:
        model = Awards
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
         
        }
        


# News Article
class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = '__all__'
        labels = {
            'name': 'Sponsors Name',
            'logo': 'Logo',
            'website': 'Web Urls',
            'team_sponsors': 'Competition',

        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sponsors Names'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Photo'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website'}),
            'team_sponsors': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Competition'}),
        }

# Inline formset for players
#PlayerFormSet = inlineformset_factory(Team, Player, form=PlayerForm, extra=1)
class ContentBlockForm(forms.ModelForm):
    class Meta:
        model = ContentBlock
        fields = '__all__'
        labels = {
            'team': 'Team',
            'slug': 'Slug',
            'title': 'Content Title',
            'content_top': 'Top Contents',
            'image': 'Photos',
            'content_bottom': 'Bottom Contents',
            'content_type': 'Type Of Content',
            'position': 'Content positioning On page',
            'year': 'Year',
            'contents_for_this_competition': 'Competition',
            'is_active': 'Display Content',

        }
        widgets = {
            'team': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'content-slug-example'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'content_top': forms.Textarea(attrs={'class': 'form-control', 'rows':15, 'placeholder': 'Write your content here...'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Select'}),
            'content_bottom': forms.Textarea(attrs={'class': 'form-control', 'rows':15, 'placeholder': 'Write your content here...'}),
            'content_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Content...'}),
            'position': forms.Textarea(attrs={'class': 'form-control', 'rows':15, 'placeholder': 'Write your content here...'}),
            'year': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select'}),
            'contents_for_this_competition': forms.Select(attrs={'class': 'form-control', 'rows':15, 'placeholder': 'Select Competition'}),
            'is_active': forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
        }

# Season Form
class CompetitionSeasonForm(forms.ModelForm):
    class Meta:
        model = CompetitionSeason
        fields = '__all__'

        labels = {
            'name': 'Name',
            'year': 'Year',
            'is_current_season': 'Current Season',

        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
            'is_current_season': forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
        }





class PlayerStatLineForm(forms.ModelForm):
    class Meta:
        model = PlayerStatLine
        # Only included the fields i want to edit directly
        fields = [
            'starter',
            'player_name',
            'minutes',
            'points',
            'field_goal_made',
            'field_goal_attempts',
            'point_3_made',
            'point_3_attempts',
            'ft_made',
            'ft_attempts',
            'offensive_rebs',
            'defensive_rebs',
            'assists',
            'steals',
            'blocks',
            'turnovers',
        ]
        # Excluded calculated/derived fields so they don't cause validation errors
        exclude = [
            'fg_percent',
            'point_3_percent',
            'point_2_attempts',
            'point_2_made',
            'point_2_percent',
            'ft_percent',
            'total_rebounds',
            'personal_fouls',
            'plus_minus',
            'efficiency',
            'game_schedule',
            'team',
            'opponents',
        ]




#  Contact Form
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'full_name', 'email', 'mobile',  'message'
         
        ]

        labels = {
            'full_name': 'Name',
            'email': 'Email',
            'mobile': 'Enter Phone Number',
    
            'message': 'Message',
            
        }

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Pleas enter your name: '}),
            'email':  forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Correct Phone Number...'}),        
          
            'message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please Enter Your Message...'}),
        }


class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber

        fields = [ 'email', 'phone', ]

      