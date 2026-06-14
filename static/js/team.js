$(document).ready(function () {
    console.log("Document is ready");

    // RESET FUNCTION
    function resetGameDisplays() {
        $("#all-games-container, #regular-season-container, #playoff-container, #international-container").hide();
        $("#all_games_header").hide();
        $("#all_games_table").hide();
        $("#all_games_cards").show();
        $("#show-table-btn").text("View All Games");
        $("#regular_season_header").hide();
        $("#regular_season_table").hide();
        $("#regular_season_games_cards").show();
        $("#show-regular-season-table-btn").text("View All Games");
    }

    // Default load state
    resetGameDisplays();
    $("#all-games-container").show(); 

    // ALL GAMES TOGGLE
    $("#show-table-btn").click(function(e) {
        e.preventDefault(); 
        var tableUI = $("#all_games_table, #all_games_header");
        var cardUI = $("#all_games_cards");

        if ($("#all_games_table").is(":hidden")) {
            cardUI.hide();
            tableUI.fadeIn("fast");
            $(this).text("Back to Summary Cards");
        } else {
            tableUI.hide();
            cardUI.fadeIn("fast");
            $(this).text("View All Games");
        }
    });

    // REGULAR SEASON TOGGLE
    $("#show-regular-season-table-btn").click(function(e) {
        e.preventDefault(); 
        var tableUI = $("#regular_season_table, #regular_season_header");
        var cardUI = $("#regular_season_games_cards");

        if ($("#regular_season_table").is(":hidden")) {
            cardUI.hide();
            tableUI.fadeIn("fast");
            $(this).text("Back to Summary Cards");
        } else {
            tableUI.hide();
            cardUI.fadeIn("fast");
            $(this).text("View All Games");
        }
    });

    // FILTER LOGIC
    function filterGames() {
      const compFilter = $("#competition-filter").val();
      const monthFilter = $("#month-filter").val();
      const yearFilter = $("#year-filter").val();

      $(".game-result").each(function() {
        const gameType = $(this).data("type");
        const gameMonth = $(this).data("month");
        const gameYear = $(this).data("year");

        const matchesComp = (compFilter === "all" || gameType === compFilter);
        const matchesMonth = (monthFilter === "all" || gameMonth === monthFilter);
        const matchesYear = (yearFilter === "all" || gameYear === yearFilter);

        if (matchesComp && matchesMonth && matchesYear) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    }

    $("#competition-filter, #month-filter, #year-filter").change(filterGames);
});















/** 
$(document).ready(function () {
    console.log("Document is ready");

    /**
     * 1. RESET FUNCTION
     * Explicitly hides every container and table by its specific ID.
     
    function resetGameDisplays() {
        // Hide all major category containers
        $("#all_games_container, #regular_season_container, #playoff_container, #international_container").hide();
        
        // Explicitly hide All Games components
        $("#all_games_header").hide();
        $("#all_games_table").hide();
        $("#all_games_cards").show();

        // Explicitly hide Regular Season components
        $("#regular_season_header").hide();
        $("#regular_season_table").hide();
        $("#regular_season_games_cards").show();

        // Explicitly hide Playoff components
        $("#playoff_header").hide();
        $("#playoff_table").hide();
        $("#playoff_games_cards").show();

        // Explicitly hide International components
        $("#international_header").hide();
        $("#international_table").hide();
        $("#international_games_cards").show();
        
        // Reset the toggle button text back to default
        $("#show-table-btn").text("View All Games");
    }

     //Initial state: Show 'All Games' as default
    resetGameDisplays();
    $("#all_games_container").show(); 

    
    // * 2. TABLE TOGGLE LOGIC
     //* This handles the button click for the "All Games" section.
     
    $("#show-table-btn").click(function(e) {
        e.preventDefault(); 
        
        var tableUI = $("#all_games_table, #all_games_header");
        var cardUI = $("#all_games_cards");

        if ($("#all_games_table").is(":hidden")) {
            cardUI.hide();
            tableUI.fadeIn("fast");
            $(this).text("Back to Summary Cards");
        } else {
            tableUI.hide();
            cardUI.fadeIn("fast");
            $(this).text("View All Games");
        }
    });

    
     * 3. DROPDOWN FILTER LOGIC
     * Switches between containers based on the selection.
     
    $("#competition-filter").change(function () {                
        resetGameDisplays();

        var selectedValue = $(this).val();
        console.log("Dropdown changed to:", selectedValue);

        if (selectedValue === "all") {
            $("#all_games_container").fadeIn("slow");
        } 
        else if (selectedValue === "Regular Season") {
            $("#regular_season_container").fadeIn("slow");
        } 
        else if (selectedValue === "Playoffs") {
            $("#playoff_container").fadeIn("slow");
        } 
        else if (selectedValue === "International") {
            $("#international_container").fadeIn("slow");
        } 
        else {
            console.log("No matching games found for:", selectedValue);
        }
    });
}); 
*/