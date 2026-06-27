from django.test import TestCase
from .models import Team, Player, Competition, , TeamNews

from django.core.files.uploadedfile import SimpleUploadedFile


class PlayerModelTest(TestCase):
    def test_create_player_for_team(self):
        # Create a competition first (required by Team)
        competition = Competition.objects.create(name="National League")
        venue = Venue.objects.create(name="National Stadium", state_province="Lagos")

        # Create a team
        team = Team.objects.create(
            name="Lagos Lions",
            city="Lagos",
            venue=venue,
            competitions=competition
        )

        # Create a player
        player = Player.objects.create(
            team=team,
            player_name="Solomon",
            jersey_number=7,
            position="PG",
            height_cm=180,
            weight_kg=75,
            country="Nigeria",
            is_starter=True
        )

        # Assertions
        self.assertEqual(player.team.name, "Lagos Lions")
        self.assertEqual(player.position, "PG")
        self.assertTrue(Player.objects.filter(player_name="Solomon").exists())





class TeamNewsModelTest(TestCase):
    def setUp(self):
        # 1. Create a Competition object (required for the ForeignKey)
        self.comp = Competition.objects.create(name="June Championship")
        
        # 2. Create a dummy image for testing
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x44\x01\x00\x3b'
        )
        self.uploaded_image = SimpleUploadedFile('test_image.gif', self.small_gif, content_type='image/gif')

    def test_news_creation(self):
        """Test that a TeamNews object is correctly created and saved."""
        news = TeamNews.objects.create(
            category='Team',
            heading='Python Squad Dominates',
            intro='A great start to the tournament.',
            content='Full detailed article text here...',
            competition=self.comp,
            image=self.uploaded_image
        )

        # Verify the data was saved correctly
        self.assertEqual(news.heading, 'Python Squad Dominates')
        self.assertEqual(news.category, 'Team')
        self.assertEqual(news.competition.name, "June Championship")
        self.assertTrue(news.image.name.endswith('.gif'))
        self.assertIsNotNone(news.published_date) # Check auto_now_add worked










"""
class Cart:
    def __init__(self, request):
        # Store the current session and request object
        self.session = request.session
        self.request = request

        # Try to get the cart dictionary from the session
        cart = self.session.get('session_key')

        # If no cart exists yet, initialize an empty one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure the cart is available everywhere in the class
        self.cart = cart
    
    def add_to_database(self, product, quantity):
        
        #Add a product to the cart using its ID (passed directly),
        #and save the cart state to the user's Profile if logged in.
        
        product_id  = str(product)
        product_qty = int(quantity)

        # Add or update product quantity in the cart
        self.cart[product_id] = product_qty
        self.session.modified = True

        # If user is logged in, also save cart snapshot to Profile
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)

    def add_to_cart(self, product, quantity, color="Default", size="Standard"):
        
        #Add a product variation combo to the session dictionary,
        #and update back up data arrays on user profiles if authenticated.
        
        product_id = str(product.id)
        product_qty = int(quantity)

        # Stacking unique variant combination keys to allow multi-item checks
        variant_key = f"{product_id}-{color}-{size}"

        # Build or modify the variant item entry parameters
        ## This code looks inside the session basket (self.cart) to see if this exact unique variant key eg..("5-Black-XL") is already in there.
        if variant_key in self.cart:
            if isinstance(self.cart[variant_key], dict):
                self.cart[variant_key]['qty'] += product_qty
            else:
                self.cart[variant_key] += product_qty
        else:
            self.cart[variant_key] = {
                'id': product_id,
                'qty': product_qty,
                'color': color,
                'size': size
            }

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)
    
    
    
    def add_to_cart(self, product, quantity):
        
        #Add a product to the cart using its model instance (product.id),
        #and save the cart state to the user's Profile if logged in.
        
        product_id = str(product.id)
        product_qty = int(quantity)

        self.cart[product_id] = product_qty
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)
            


    
    def add_to_cart(self, product, quantity, color="Default", size="Standard"):
    
        #Add a product to the cart using a unique variation key,
        #and save the updated cart state to the user's Profile if logged in.
        
        product_id = str(product.id)
        product_qty = int(quantity)
    
        # 1. CREATE THE UNIQUE VARIANT KEY
        # This prevents different colors/sizes of the same product from overwriting each other
        variant_key = f"{product_id}-{color}-{size}"

        # 2. UPDATE THE CART DICTIONARY DATA
        if variant_key in self.cart:
            # If this exact combination already exists, just increment the quantity
            # (Handling both raw integers from old data and the new dict format safely)
            if isinstance(self.cart[variant_key], dict):
                self.cart[variant_key]['qty'] += product_qty
            else:
                self.cart[variant_key] += product_qty
        else:
            # If it's a completely new color or size variation, add it as a new line item
            self.cart[variant_key] = {
                'id': product_id,
                'qty': product_qty,
                'color': color,
                'size': size
            }

        # Mark the session as modified so Django saves it to cookies/session DB
        self.session.modified = True

        # 3. SYNC WITH USER PROFILE (DATABASE BACKUP)
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            
            # Convert our new nested dictionary structure into valid JSON for your text field
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)
    




    def __len__(self):
        
        Return the total number of items in the cart (sum of quantities).
        
        return sum(self.cart.values())

    def get_products(self):
        
        #Return all Product objects currently in the cart.
        
        product_ids = self.cart.keys()
        return Product.objects.filter(id__in=product_ids)

    def get_quantities(self):
        
        #Return the raw dictionary of product IDs and their quantities.
        
        return self.cart

    def update(self, product, quantity):
        
        #Update the quantity of a specific product in the cart.
        #Also sync the cart state to Profile if logged in.
        
        product_id = str(product)
        product_qty = int(quantity)

        if product_id in self.cart:
            self.cart[product_id] = product_qty

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)

    def delete(self, product):
        
        #Remove a product completely from the cart.
        #Also sync the cart state to Profile if logged in.
        
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)

    def cart_total(self):
        
        #Calculate the total price of all items in the cart,
        #taking into account sales prices if applicable.
        
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total = 0

        for key, value in self.cart.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sales:
                        total += product.sale_price * value
                    else:
                        total += product.price * value
        return total

    def clear(self):
        
        #Empty the entire cart (remove all items).
        #Also reset the saved cart in Profile if logged in.
        
        self.session['session_key'] = {}
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            current_user.update(old_cart="{}")
"""





 
"""
    # Update the quantity, color, size, and things about the cart
    def update(self, product, quantity, color="Default", size="Standard"):
        
        #Update the quantity of a specific product variant in the cart.
        
        product_id = str(product.id)
        variant_key = f"{product_id}-{color}-{size}"
        product_qty = int(quantity)

        if variant_key in self.cart:
            self.cart[variant_key]['qty'] = product_qty

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)

    # Cart Delete
    def delete(self, product, color="Default", size="Standard"):
        
        #Remove a product variant completely from the cart.
        
        product_id = str(product.id)
        variant_key = f"{product_id}-{color}-{size}"

        if variant_key in self.cart:
            del self.cart[variant_key]

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)
"""  











































"""
path('team/<int:competition_id>/<int:team_id>/', TeamDetailView.as_view(), name='team-id'),
path('about/', views.registration_page, name='about'),
# Season Urls
path('season_create/',SeasonCreateView.as_view(), name='season-create'),
path('season_competition_list/',SeasonCompetitionListView.as_view(), name='season-competition-list'),
path('season_id/<int:pk>/',SeasonDetailView.as_view(), name='season-id'),
path('season_update/<int:pk>/',SeasonUpdateView.as_view(), name='update-season'),
path('season_delete/<int:pk>/',views.delete_season, name='delete-season'),

# Competition Urls
path('competition_create/',CompetitionCreateView.as_view(), name='competition-create'),
#path('competitions_list/',CompetitionListView.as_view(), name='competitions-list'),

path('competition_update/<int:pk>/',CompetitionUpdateView.as_view(), name='competition-update'),
path('competition_delete/<int:pk>/',CompetitionDeleteView.as_view(), name='competition-delete'),

# Teams urls
# CBV Path for Team creation, listing, update and delete.
path('team_create/', TeamCreateView.as_view(), name='team-create'),
path('competition/<int:competition_id>/team_list/', TeamListView.as_view(), name='team-list'),
path('competition/<int:competition_id>/roster/', views.team_roster, name='team-roster'),
path('competition/<int:competition_id>/team/', TeamDetailView.as_view(), name='team-id'),
#path('teams_id/<int:pk>/<int:competition_id>/<int:game_id>/', TeamDetailView.as_view(), name='team-detail'),
path('competition/<int:competition_id>/update/', TeamUpdateView.as_view(), name='update-team'),
#path('delete_team/<int:pk>/', TeamDeleteView.as_view(), name='delete-team'),

# Team Staff urls
# CBV Path for Staff creation, listing, update and delete.
path('staff_create/', StaffCreateView.as_view(), name='staff-create'),
path('staff_id/<int:pk>/', StaffDetailView.as_view(), name='staff-id'),
path('staff_update/<int:competition_id>/<int:staff_id>/', StaffUpdateView.as_view(), name='update-staff'),
path('delete_staff/<int:pk>/', StaffDeleteView.as_view(), name='delete-staff'),

#Players Urls
path('player_create/',PlayerCreateView.as_view(), name='create-player'),
path('competition/<int:competition_id>/player/<int:pk>', PlayerDetailView.as_view(), name='players-id'),
path('player update/<int:competition_id>/player/<int:pk>', PlayerUpdateView.as_view(), name='update-player'),
path('delete_player/<int:pk>/', PlayerDeleteView.as_view(), name='delete-player'),


# Opponent urls
# CBV Path for Opponents creation, listing, update and delete.
path('opponent_create/', OpponentCreateView.as_view(), name='opponent-create'),
path('opponent_list/', OpponentListView.as_view(), name='opponent-list'),
path('opponent_id/<int:pk>/', OpponentDetailView.as_view(), name='opponent-id'),
path('update_opponent/<int:pk>/', OpponentUpdateView.as_view(), name='update-opponent'),
path('delete_opponent/<int:pk>/', views.delete_opponent, name='delete-opponent'),

#Games Urls
path('game_create/',GameCreateView.as_view(), name='game-create'),
path('competition/<int:competition_id>/game_list/',GameListView.as_view(), name='game-list'),
#path('game update/<int:competition_id>/<int:game_id>/', GameDetailView.as_view(), name='game-id'),
path('game update/<int:competition_id>/player/<int:pk>', GameUpdateView.as_view(), name='update-game'),
#path('delete_game/<int:pk>/', GameDeleteView.as_view(), name='delete-game'),



#Players Stats Lines
#path('player_stats_create/',PlayerStatsLineCreateView.as_view(), name='create-player-stats'),
#path('players_stats_list/', PlayerStatsLineListView.as_view(), name='players-stats-lists'),
#path('player_stats_id/<int:pk>/', PlayerStatsLineDetailView.as_view(), name='players-stats-id'),
#path('update_stats_player/<int:pk>/', PlayerStatsLineUpdateView.as_view(), name='update-player-stats'),
#path('delete_stats_player/<int:pk>/', PlayerStatsLineDeleteView.as_view(), name='delete-player-stats'),

#Quarterly Scores Urls
path('scores_create/',QuarterlyScoresCreateView.as_view(), name='create-scores'),
path('competition/<int:competition_id>/quarter_scores/',QuarterlyScoresListView.as_view(), name='scores-list'),
#path('scores_id/<int:pk>/', QuarterlyScoresDetailView.as_view(), name='scores-id'),
path('scores update/<int:competition_id>/scores/<int:pk>', QuarterlyScoresUpdateView.as_view(), name='update-scores'),
#path('delete_scores/<int:pk>/', QuarterlyScoresDeleteView.as_view(), name='delete-scores'),




#Sponsor 
path('create sponsor/', views.create_sponsor, name='create-sponsor'),
path('list sponsor/', views.list_sponsors, name='list-sponsor'),
path('update sponsor/<int:pk>/', views.update_sponsor, name='update-sponsor'),
path('delete sponsor/<int:pk>/', views.delete_sponsor, name='delete-sponsor'),
#path('delete_stats_player/<int:pk>/', PlayerStatsLineDeleteView.as_view(), name='delete-player-stats'),

"""
