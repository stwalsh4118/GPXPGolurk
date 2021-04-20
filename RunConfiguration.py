
class RunConfiguration:
    
    def __init__(self,
                 driver,
                 username,
                 run_amount = 1,
                 pokemon_per_minute = 300,
                 currently_selected_pokemon = "",
                 pass_orb = False,
                 box_number = 3,
                 mystery_egg_mode = False,
                 full_random_mode = False) -> None:
        
        self.driver = driver
        self.username = username
        self.run_amount = run_amount
        self.pass_orb = pass_orb
        self.currently_selected_pokemon = currently_selected_pokemon
        self.box_number = box_number
        self.mystery_egg_mode = mystery_egg_mode
        self.full_random_mode = full_random_mode
        self.pokemon_per_minute = pokemon_per_minute